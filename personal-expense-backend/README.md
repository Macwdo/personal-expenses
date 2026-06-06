# Personal Expense Backend

FastAPI backend for relational personal expenses.

The app keeps all data in memory. Data is created during FastAPI lifespan startup and cleared during shutdown.

## Setup

```bash
cd personal-expense-backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

API docs are available at `http://127.0.0.1:8000/docs`.

## Model

```text
Expense 1 -> many Payments
```

`Expense` stores the stable cost, such as wedding, gym, or subscription.

`Payment` stores each paid or planned money movement for an expense.

The payment status values are `planned`, `pending`, `due`, and `paid`.
