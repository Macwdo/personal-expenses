# Expense Relations

This document describes the target relational and URL shape for personal expenses. It keeps `Expense` as the parent record, models every paid or payable movement as a `Payment`, and exposes the frontend detail page through a URL segment that matches the expense type.

## Core Idea

An `Expense` represents the thing being paid for, such as a wedding, gym, subscription, phone, or hardware purchase.

A `Payment` represents one financial movement attached to an expense. Payments can be already paid, planned for the future, one-time, installment-based, or recurring.

```text
Expense 1 -> many Payments
```

The frontend detail route uses the expense type before the id:

```text
/expenses/unique/:expenseId
/expenses/recurrent/:expenseId
/expenses/installment/:expenseId
```

The API relation stays id-based:

```text
GET /expenses/:expenseId
GET /expenses/:expenseId/payments
```

The frontend validates that the type segment matches the fetched expense. For example, an expense with `type: "recurrent"` belongs at `/expenses/recurrent/:expenseId`; opening the same id at `/expenses/installment/:expenseId` should be treated as a missing page.

## Expense

`Expense` stores the stable identity and total planned value of the cost.

| Field         | Description                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------- |
| `id`          | Unique expense identifier.                                                                     |
| `category_id` | Foreign key to the related `Category` record used for filtering and grouping.                  |
| `name`        | Expense name, such as `Casamento`, `Academia Danilo`, or `Youtube`.                            |
| `type`        | Expense behavior: `one_time`, `installment`, or `recurrent`.                                   |
| `total_value` | Total planned value for the full expense.                                                      |
| `starts_on`   | Optional start date for planned or recurring payments.                                         |
| `ends_on`     | Optional end date. Usually present for installment expenses and absent for recurrent expenses. |
| `notes`       | Optional human notes.                                                                          |

## Expense Types

### One-Time Expense

A one-time expense is paid with a single payment.

Examples:

- A single purchase paid immediately.
- A service paid in full.

Rules:

- `Expense.type` is `one_time`.
- Frontend detail URL is `/expenses/unique/:expenseId`.
- `Expense.total_value` is equal to the single payment amount.
- The expense has one `Payment`.
- The related payment has `Payment.kind` set to `single`.
- Recurring, installment, initial, and additional payment kinds are not valid for this type.

### Installment Expense

An installment expense has a known total value and is paid over a fixed number of payments.

Examples:

- Wedding.
- Hardware purchase.
- Ring purchase.

Rules:

- `Expense.type` is `installment`.
- Frontend detail URL is `/expenses/installment/:expenseId`.
- `Expense.total_value` is the full agreed amount.
- The expense can have an initial payment.
- The expense can have multiple installment payments.
- The related payments can use `Payment.kind` values `initial`, `installment`, or `additional`.
- Installments usually repeat monthly on a specific day.
- The expense is complete when paid payments reach `total_value`.

### Recurrent Expense

A recurrent expense repeats without a fixed end date.

Examples:

- Gym.
- Subscriptions.
- Phone plan.

Rules:

- `Expense.type` is `recurrent`.
- Frontend detail URL is `/expenses/recurrent/:expenseId`.
- `Expense.total_value` can be `null` when there is no known lifetime total.
- The recurring payment amount is stored on the payment schedule.
- The related payment has `Payment.kind` set to `recurring`.
- Single, installment, initial, and additional payment kinds are not valid for this type.
- Payments continue until the expense is cancelled or an `ends_on` date is set.

## Payment

`Payment` stores an actual or planned money movement for an expense.

| Field                | Description                                                                     |
| -------------------- | ------------------------------------------------------------------------------- |
| `id`                 | Unique payment identifier.                                                      |
| `expense_id`         | Parent expense identifier.                                                      |
| `kind`               | Payment kind: `initial`, `installment`, `single`, `recurring`, or `additional`. |
| `status`             | Payment status: `planned`, `pending`, `due`, or `paid`.                         |
| `amount`             | Payment value.                                                                  |
| `due_date`           | Date this payment is expected.                                                  |
| `paid_at`            | Date this payment was actually paid. Empty for unpaid planned payments.         |
| `installment_number` | Installment position, when applicable.                                          |
| `installment_count`  | Total installment count, when applicable.                                       |
| `repeats`            | Repeat rule, such as `none` or `monthly`.                                       |
| `repeat_day`         | Day of the month for recurring or installment payments.                         |
| `notes`              | Optional human notes.                                                           |

## Wedding Example

The current seed has a wedding row in `personal-expenses-front/lib/seed-expenses.json`.

The wedding should become one `Expense` with many `Payment` records.

```json
{
  "expense": {
    "id": 1,
    "category": "Casamento",
    "name": "Casamento",
    "type": "installment",
    "total_value": "60800.00",
    "starts_on": null,
    "ends_on": null
  },
  "payments": [
    {
      "id": 1,
      "expense_id": 1,
      "kind": "initial",
      "status": "paid",
      "amount": "3000.00",
      "due_date": null,
      "paid_at": null,
      "installment_number": null,
      "installment_count": null,
      "repeats": "none",
      "repeat_day": null
    },
    {
      "id": 2,
      "expense_id": 1,
      "kind": "additional",
      "status": "paid",
      "amount": "5798.99",
      "due_date": null,
      "paid_at": null,
      "installment_number": null,
      "installment_count": null,
      "repeats": "none",
      "repeat_day": null
    },
    {
      "id": 3,
      "expense_id": 1,
      "kind": "installment",
      "status": "planned",
      "amount": "1000.00",
      "due_date": null,
      "paid_at": null,
      "installment_number": 1,
      "installment_count": 22,
      "repeats": "monthly",
      "repeat_day": null
    }
  ]
}
```

The existing seed says the wedding has:

- `monthly_cost`: `1000.00`
- `installments`: `22`
- `paid_amount`: `3000.00`
- `paid_installments`: `3`
- `paid_additional_amount`: `5798.99`
- `remaining_amount`: `22000.00`
- `remaining_additional_amount`: `60800.00`

For a relational model, the final migration should split those aggregate values into individual payment rows. Dates are not present in the seed, so `due_date`, `paid_at`, and `repeat_day` need user-provided values before exact payment schedules can be generated.

## Recurrent Gym Example

```json
{
  "expense": {
    "id": 5,
    "category": "Academia",
    "name": "Academia Danilo",
    "type": "recurrent",
    "total_value": null,
    "starts_on": null,
    "ends_on": null
  },
  "payments": [
    {
      "id": 50,
      "expense_id": 5,
      "kind": "recurring",
      "status": "planned",
      "amount": "300.00",
      "due_date": null,
      "paid_at": null,
      "installment_number": null,
      "installment_count": null,
      "repeats": "monthly",
      "repeat_day": null
    }
  ]
}
```

## Derived Values

These values should be calculated from related payments instead of stored directly on the expense.

| Value                    | Formula                                                                         |
| ------------------------ | ------------------------------------------------------------------------------- |
| `total_paid_amount`      | Sum of paid payment amounts.                                                    |
| `total_planned_amount`   | Sum of paid and planned payment amounts, or `Expense.total_value` when present. |
| `remaining_amount`       | `Expense.total_value - total_paid_amount` when `total_value` is known.          |
| `paid_installments`      | Count of paid payments where `kind` is `installment`.                           |
| `remaining_installments` | `installment_count - paid_installments` when `installment_count` is known.      |
| `next_due_payment`       | Earliest planned payment by `due_date`.                                         |

## Migration From Current Seed Shape

Current aggregate fields can map to the relational model like this:

| Current field                 | New location                                                   |
| ----------------------------- | -------------------------------------------------------------- |
| `category`                    | `Expense.category_id` and related `Category` record            |
| `name`                        | `Expense.name`                                                 |
| `monthly_cost`                | Default amount for installment or recurring `Payment` records. |
| `installments`                | `Payment.installment_count` for installment payments.          |
| `paid_amount`                 | One or more paid `Payment` records.                            |
| `paid_installments`           | Count used to generate paid installment records.               |
| `paid_additional_amount`      | Paid `Payment` with `kind: "additional"`.                      |
| `remaining_amount`            | Planned installment `Payment` records.                         |
| `remaining_additional_amount` | Planned or pending `Payment` with `kind: "additional"`.        |

## Open Data Needed

The current seed does not include enough information to create exact dated payment rows.

Needed values:

- Payment due day for each recurring or installment expense.
- Start date for installment plans.
- Paid dates for historical payments.
- Whether `remaining_additional_amount` belongs to the same expense total or represents a separate future agreement.
- Whether recurrent expenses should generate future payment rows ahead of time or calculate the next payment dynamically.
