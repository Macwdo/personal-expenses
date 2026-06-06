Create a frontend-only personal finance app for tracking recurring, subscription, and installment-based expenses.

Use JSON seed data and browser localStorage as the data layer. Do not add a backend, database, API service, Supabase, or Django.

The original source data used Portuguese labels and comma decimal separators. Preserve the same seed values in normalized JSON, but expose clear English field names in the application code and UI where practical.

## Frontend

Use React with shadcn/ui.

- Build a home page that displays expenses in a shadcn table.
- Add filtering support by category.
- Add a button to create a new payment.
- The create button should navigate to a dedicated page for creating a payment.
- Use `zod`, `react-hook-form`, localStorage, JSON seed data, and shadcn form components for the payment form.
- The form should support both installment payments and recurring/subscription expenses with no fixed installment count.
- Currency fields should accept decimal input and display values consistently.
- Follow React and shadcn best practices.

## Data

Initial expenses should live in a JSON file and be copied into versioned localStorage on first load. Created payments should persist in localStorage.

## Data Fields

- `category`: Expense category. Use this for filtering.
- `name`: Expense or cost name.
- `monthly_cost`: Monthly recurring cost or installment value.
- `installments`: Total number of installments. `null` means recurring, subscription-based, or no fixed installment count.
- `paid_amount`: Amount paid through regular monthly/installment payments.
- `paid_installments`: Number of regular installments already paid.
- `paid_additional_amount`: Additional amount already paid outside the regular monthly/installment payment.
- `remaining_amount`: Remaining amount still due through regular payments.
- `remaining_additional_amount`: Additional remaining amount still due outside the regular payment flow.

## Derived Values

Calculate useful derived values in the frontend data layer:

- Total planned regular cost: `monthly_cost * installments` when `installments` is present.
- Remaining regular installments: `installments - paid_installments` when both values are present.
- Total paid amount: `paid_amount + paid_additional_amount`.
- Total remaining amount: `remaining_amount + remaining_additional_amount`.
- Overall planned amount: total paid amount plus total remaining amount, or the installment total when that is the more reliable source.

If imported totals conflict with calculated totals, keep the imported values, show the calculated values separately if useful, and avoid silently overwriting source data.

## Expected Behavior

- The home page should show all seeded expenses.
- Users should be able to create a new payment from the frontend.
- Created payments should persist in localStorage.
- The table should clearly show category, name, monthly cost, installments, paid amount, paid installments, paid additional amount, remaining amount, remaining additional amount, and useful derived totals.
- Rows with blank costs or blank installment counts should still render without breaking the UI.
- Category filtering should include the categories present in the seed data, such as `Casamento`, `Carro`, `Academia`, `Celular`, `Assinatura`, and `Hardware`.
