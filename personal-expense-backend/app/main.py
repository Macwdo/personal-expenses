from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


Money = Annotated[Decimal, Field(decimal_places=2, ge=Decimal("0.00"))]


class ExpenseType(StrEnum):
    ONE_TIME = "one_time"
    INSTALLMENT = "installment"
    RECURRENT = "recurrent"


class PaymentKind(StrEnum):
    INITIAL = "initial"
    INSTALLMENT = "installment"
    SINGLE = "single"
    RECURRING = "recurring"
    ADDITIONAL = "additional"


class PaymentStatus(StrEnum):
    PLANNED = "planned"
    PENDING = "pending"
    DUE = "due"
    PAID = "paid"


class RepeatRule(StrEnum):
    NONE = "none"
    MONTHLY = "monthly"


class ExpenseBase(BaseModel):
    category_id: int = Field(ge=1)
    name: str = Field(min_length=1)
    type: ExpenseType
    total_value: Money | None = None
    starts_on: date | None = None
    ends_on: date | None = None
    notes: str | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    id: int


class CategoryBase(BaseModel):
    name: str = Field(min_length=1)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int


class IncomeBase(BaseModel):
    source: str = Field(min_length=1)
    amount: Money
    received_on: date
    notes: str | None = None


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(IncomeBase):
    pass


class Income(IncomeBase):
    id: int


class PaymentBase(BaseModel):
    kind: PaymentKind
    status: PaymentStatus = PaymentStatus.PLANNED
    amount: Money
    due_date: date | None = None
    paid_at: date | None = None
    installment_number: int | None = Field(default=None, ge=1)
    installment_count: int | None = Field(default=None, ge=1)
    repeats: RepeatRule = RepeatRule.NONE
    repeat_day: int | None = Field(default=None, ge=1, le=31)
    notes: str | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    pass


class Payment(PaymentBase):
    id: int
    expense_id: int


class ExpenseTotals(BaseModel):
    total_paid_amount: Decimal
    total_planned_amount: Decimal | None
    remaining_amount: Decimal | None
    paid_installments: int
    remaining_installments: int | None
    next_due_payment: Payment | None


class ExpenseWithPayments(Expense):
    category: Category
    payments: list[Payment]
    totals: ExpenseTotals


class MarkPaymentPaid(BaseModel):
    paid_at: date = Field(default_factory=date.today)


class InMemoryStore:
    def __init__(self) -> None:
        self.categories: dict[int, Category] = {}
        self.expenses: dict[int, Expense] = {}
        self.incomes: dict[int, Income] = {}
        self.payments: dict[int, Payment] = {}
        self.next_category_id = 1
        self.next_expense_id = 1
        self.next_income_id = 1
        self.next_payment_id = 1

    def clear(self) -> None:
        self.categories.clear()
        self.expenses.clear()
        self.incomes.clear()
        self.payments.clear()
        self.next_category_id = 1
        self.next_expense_id = 1
        self.next_income_id = 1
        self.next_payment_id = 1

    def create_category(self, payload: CategoryCreate) -> Category:
        name = normalize_category_name(payload.name)
        if self.find_category_by_name(name) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists.",
            )
        category = Category(id=self.next_category_id, name=name)
        self.categories[category.id] = category
        self.next_category_id += 1
        return category

    def find_category_by_name(self, name: str) -> Category | None:
        normalized_name = normalize_category_name(name)
        return next(
            (
                category
                for category in self.categories.values()
                if category.name == normalized_name
            ),
            None,
        )

    def get_category(self, category_id: int) -> Category:
        category = self.categories.get(category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )
        return category

    def update_category(self, category_id: int, payload: CategoryUpdate) -> Category:
        self.get_category(category_id)
        name = normalize_category_name(payload.name)
        duplicate = self.find_category_by_name(name)
        if duplicate is not None and duplicate.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists.",
            )

        updated = Category(id=category_id, name=name)
        self.categories[category_id] = updated
        return updated

    def delete_category(self, category_id: int) -> None:
        category = self.get_category(category_id)
        if any(expense.category_id == category.id for expense in self.expenses.values()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category is in use.",
            )
        self.categories.pop(category_id)

    def create_income(self, payload: IncomeCreate) -> Income:
        income = Income(
            id=self.next_income_id,
            **payload.model_dump(exclude={"source"}),
            source=normalize_income_source(payload.source),
        )
        self.incomes[income.id] = income
        self.next_income_id += 1
        return income

    def get_income(self, income_id: int) -> Income:
        income = self.incomes.get(income_id)
        if income is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Income not found.")
        return income

    def update_income(self, income_id: int, payload: IncomeUpdate) -> Income:
        self.get_income(income_id)
        updated = Income(
            id=income_id,
            **payload.model_dump(exclude={"source"}),
            source=normalize_income_source(payload.source),
        )
        self.incomes[income_id] = updated
        return updated

    def delete_income(self, income_id: int) -> None:
        self.get_income(income_id)
        self.incomes.pop(income_id)

    def list_incomes(self) -> list[Income]:
        return sorted(
            self.incomes.values(),
            key=lambda income: (income.received_on, income.id),
            reverse=True,
        )

    def create_expense(self, payload: ExpenseCreate) -> Expense:
        self.get_category(payload.category_id)
        expense = Expense(id=self.next_expense_id, **payload.model_dump())
        self.expenses[expense.id] = expense
        self.next_expense_id += 1
        return expense

    def get_expense(self, expense_id: int) -> Expense:
        expense = self.expenses.get(expense_id)
        if expense is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found.")
        return expense

    def update_expense(self, expense_id: int, payload: ExpenseUpdate) -> Expense:
        self.get_expense(expense_id)
        self.get_category(payload.category_id)
        self.validate_existing_payment_kinds(expense_id, payload.type)
        expense = Expense(id=expense_id, **payload.model_dump())
        self.expenses[expense_id] = expense
        return expense

    def delete_expense(self, expense_id: int) -> None:
        self.get_expense(expense_id)
        self.expenses.pop(expense_id)
        self.payments = {
            payment_id: payment
            for payment_id, payment in self.payments.items()
            if payment.expense_id != expense_id
        }

    def create_payment(self, expense_id: int, payload: PaymentCreate) -> Payment:
        expense = self.get_expense(expense_id)
        self.validate_payment_kind(expense.type, payload.kind)
        payment = Payment(id=self.next_payment_id, expense_id=expense_id, **payload.model_dump())
        self.payments[payment.id] = payment
        self.next_payment_id += 1
        return payment

    def get_payment(self, payment_id: int) -> Payment:
        payment = self.payments.get(payment_id)
        if payment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
        return payment

    def update_payment(self, payment_id: int, payload: PaymentUpdate) -> Payment:
        payment = self.get_payment(payment_id)
        expense = self.get_expense(payment.expense_id)
        self.validate_payment_kind(expense.type, payload.kind)
        updated = Payment(id=payment.id, expense_id=payment.expense_id, **payload.model_dump())
        self.payments[payment_id] = updated
        return updated

    def delete_payment(self, payment_id: int) -> None:
        self.get_payment(payment_id)
        self.payments.pop(payment_id)

    def list_payments(self, expense_id: int | None = None) -> list[Payment]:
        payments = list(self.payments.values())
        if expense_id is not None:
            payments = [payment for payment in payments if payment.expense_id == expense_id]
        return sorted(payments, key=lambda payment: (payment.due_date or date.max, payment.id))

    def mark_payment_paid(self, payment_id: int, payload: MarkPaymentPaid) -> Payment:
        payment = self.get_payment(payment_id)
        updated = payment.model_copy(update={"status": PaymentStatus.PAID, "paid_at": payload.paid_at})
        self.payments[payment_id] = updated
        return updated

    def expense_with_payments(self, expense_id: int) -> ExpenseWithPayments:
        expense = self.get_expense(expense_id)
        payments = self.list_payments(expense_id)
        return ExpenseWithPayments(
            **expense.model_dump(),
            category=self.get_category(expense.category_id),
            payments=payments,
            totals=calculate_totals(expense, payments),
        )

    def validate_existing_payment_kinds(self, expense_id: int, expense_type: ExpenseType) -> None:
        for payment in self.list_payments(expense_id):
            self.validate_payment_kind(expense_type, payment.kind)

    def validate_payment_kind(self, expense_type: ExpenseType, payment_kind: PaymentKind) -> None:
        allowed_kinds: dict[ExpenseType, set[PaymentKind]] = {
            ExpenseType.ONE_TIME: {PaymentKind.SINGLE},
            ExpenseType.RECURRENT: {PaymentKind.RECURRING},
            ExpenseType.INSTALLMENT: {
                PaymentKind.INITIAL,
                PaymentKind.INSTALLMENT,
                PaymentKind.ADDITIONAL,
            },
        }

        if payment_kind not in allowed_kinds[expense_type]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{payment_kind.value} payments are not allowed for {expense_type.value} expenses.",
            )


def normalize_category_name(name: str) -> str:
    normalized_name = name.strip()
    if normalized_name == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Category name is required.",
        )
    return normalized_name


def normalize_income_source(source: str) -> str:
    normalized_source = source.strip()
    if normalized_source == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Income source is required.",
        )
    return normalized_source


def calculate_totals(expense: Expense, payments: list[Payment]) -> ExpenseTotals:
    paid_payments = [payment for payment in payments if payment.status == PaymentStatus.PAID]
    planned_payments = [payment for payment in payments if payment.status != PaymentStatus.PAID]
    installment_payments = [payment for payment in payments if payment.kind == PaymentKind.INSTALLMENT]
    paid_installments = len(
        [payment for payment in installment_payments if payment.status == PaymentStatus.PAID]
    )
    installment_count = next(
        (payment.installment_count for payment in installment_payments if payment.installment_count is not None),
        None,
    )
    next_due_payment = next(
        (
            payment
            for payment in sorted(planned_payments, key=lambda item: (item.due_date or date.max, item.id))
            if payment.status != PaymentStatus.PAID
        ),
        None,
    )

    total_paid_amount = sum((payment.amount for payment in paid_payments), Decimal("0.00"))
    payment_total = sum((payment.amount for payment in planned_payments), Decimal("0.00"))
    total_planned_amount = expense.total_value if expense.total_value is not None else payment_total
    remaining_amount = (
        max(expense.total_value - total_paid_amount, Decimal("0.00"))
        if expense.total_value is not None
        else None
    )
    remaining_installments = (
        max(installment_count - paid_installments, 0) if installment_count is not None else None
    )

    return ExpenseTotals(
        total_paid_amount=total_paid_amount,
        total_planned_amount=total_planned_amount,
        remaining_amount=remaining_amount,
        paid_installments=paid_installments,
        remaining_installments=remaining_installments,
        next_due_payment=next_due_payment,
    )


def seed_store(store: InMemoryStore) -> None:
    category_ids = {
        name: store.create_category(CategoryCreate(name=name)).id
        for name in [
            "Casamento",
            "Carro",
            "Academia",
            "Celular",
            "Assinatura",
            "Hardware",
        ]
    }

    wedding = store.create_expense(
        ExpenseCreate(
            category_id=category_ids["Casamento"],
            name="Casamento",
            type=ExpenseType.INSTALLMENT,
            total_value=Decimal("60800.00"),
            notes="Seeded from the existing wedding aggregate expense.",
        )
    )
    store.create_payment(
        wedding.id,
        PaymentCreate(
            kind=PaymentKind.INITIAL,
            status=PaymentStatus.PAID,
            amount=Decimal("3000.00"),
            repeats=RepeatRule.NONE,
        ),
    )
    store.create_payment(
        wedding.id,
        PaymentCreate(
            kind=PaymentKind.ADDITIONAL,
            status=PaymentStatus.PAID,
            amount=Decimal("5798.99"),
            repeats=RepeatRule.NONE,
        ),
    )
    for installment_number in range(1, 4):
        store.create_payment(
            wedding.id,
            PaymentCreate(
                kind=PaymentKind.INSTALLMENT,
                status=PaymentStatus.PAID,
                amount=Decimal("1000.00"),
                installment_number=installment_number,
                installment_count=22,
                repeats=RepeatRule.MONTHLY,
            ),
        )
    for installment_number in range(4, 23):
        store.create_payment(
            wedding.id,
            PaymentCreate(
                kind=PaymentKind.INSTALLMENT,
                status=PaymentStatus.PLANNED,
                amount=Decimal("1000.00"),
                installment_number=installment_number,
                installment_count=22,
                repeats=RepeatRule.MONTHLY,
            ),
        )

    gym = store.create_expense(
        ExpenseCreate(
            category_id=category_ids["Academia"],
            name="Academia Danilo",
            type=ExpenseType.RECURRENT,
            total_value=None,
        )
    )
    store.create_payment(
        gym.id,
        PaymentCreate(
            kind=PaymentKind.RECURRING,
            status=PaymentStatus.PLANNED,
            amount=Decimal("300.00"),
            repeats=RepeatRule.MONTHLY,
        ),
    )

    youtube = store.create_expense(
        ExpenseCreate(
            category_id=category_ids["Assinatura"],
            name="Youtube",
            type=ExpenseType.RECURRENT,
            total_value=None,
        )
    )
    store.create_payment(
        youtube.id,
        PaymentCreate(
            kind=PaymentKind.RECURRING,
            status=PaymentStatus.PLANNED,
            amount=Decimal("0.00"),
            repeats=RepeatRule.MONTHLY,
        ),
    )


def get_store(request: Request) -> InMemoryStore:
    return request.app.state.store


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = InMemoryStore()
    seed_store(store)
    app.state.store = store
    yield
    store.clear()


app = FastAPI(title="Personal Expense Backend", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/categories", response_model=list[Category])
def list_categories(request: Request) -> list[Category]:
    store = get_store(request)
    return sorted(store.categories.values(), key=lambda category: category.name)


@app.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, request: Request) -> Category:
    return get_store(request).create_category(payload)


@app.put("/categories/{category_id}", response_model=Category)
def update_category(category_id: int, payload: CategoryUpdate, request: Request) -> Category:
    return get_store(request).update_category(category_id, payload)


@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, request: Request) -> None:
    get_store(request).delete_category(category_id)


@app.get("/incomes", response_model=list[Income])
def list_incomes(request: Request) -> list[Income]:
    return get_store(request).list_incomes()


@app.post("/incomes", response_model=Income, status_code=status.HTTP_201_CREATED)
def create_income(payload: IncomeCreate, request: Request) -> Income:
    return get_store(request).create_income(payload)


@app.get("/incomes/{income_id}", response_model=Income)
def get_income(income_id: int, request: Request) -> Income:
    return get_store(request).get_income(income_id)


@app.put("/incomes/{income_id}", response_model=Income)
def update_income(income_id: int, payload: IncomeUpdate, request: Request) -> Income:
    return get_store(request).update_income(income_id, payload)


@app.delete("/incomes/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: int, request: Request) -> None:
    get_store(request).delete_income(income_id)


@app.get("/expenses", response_model=list[ExpenseWithPayments])
def list_expenses(request: Request) -> list[ExpenseWithPayments]:
    store = get_store(request)
    return [store.expense_with_payments(expense.id) for expense in store.expenses.values()]


@app.post("/expenses", response_model=ExpenseWithPayments, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, request: Request) -> ExpenseWithPayments:
    store = get_store(request)
    expense = store.create_expense(payload)
    return store.expense_with_payments(expense.id)


@app.get("/expenses/{expense_id}", response_model=ExpenseWithPayments)
def get_expense(expense_id: int, request: Request) -> ExpenseWithPayments:
    return get_store(request).expense_with_payments(expense_id)


@app.put("/expenses/{expense_id}", response_model=ExpenseWithPayments)
def update_expense(expense_id: int, payload: ExpenseUpdate, request: Request) -> ExpenseWithPayments:
    store = get_store(request)
    expense = store.update_expense(expense_id, payload)
    return store.expense_with_payments(expense.id)


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, request: Request) -> None:
    get_store(request).delete_expense(expense_id)


@app.get("/expenses/{expense_id}/payments", response_model=list[Payment])
def list_expense_payments(expense_id: int, request: Request) -> list[Payment]:
    store = get_store(request)
    store.get_expense(expense_id)
    return store.list_payments(expense_id)


@app.post("/expenses/{expense_id}/payments", response_model=Payment, status_code=status.HTTP_201_CREATED)
def create_payment(expense_id: int, payload: PaymentCreate, request: Request) -> Payment:
    return get_store(request).create_payment(expense_id, payload)


@app.get("/payments", response_model=list[Payment])
def list_payments(request: Request) -> list[Payment]:
    return get_store(request).list_payments()


@app.put("/payments/{payment_id}", response_model=Payment)
def update_payment(payment_id: int, payload: PaymentUpdate, request: Request) -> Payment:
    return get_store(request).update_payment(payment_id, payload)


@app.delete("/payments/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, request: Request) -> None:
    get_store(request).delete_payment(payment_id)


@app.patch("/payments/{payment_id}/pay", response_model=Payment)
def mark_payment_paid(payment_id: int, payload: MarkPaymentPaid, request: Request) -> Payment:
    return get_store(request).mark_payment_paid(payment_id, payload)
