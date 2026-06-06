# Personal Expenses

Personal finance app for recurring, subscription, and installment-based expenses. The app is now frontend-only and stores data in browser localStorage, seeded from JSON on first load.

## Frontend Setup

```bash
cd personal-expenses-front
bun install
bun dev
```

The frontend uses Next, zod, react-hook-form, localStorage, JSON seed data, and shadcn-style UI components. Currency inputs accept either `.` or `,` decimal separators.

## Data

Initial expenses live in `personal-expenses-front/lib/seed-expenses.json`. On first load, the app copies that JSON into versioned localStorage under `personal-expenses:v1`; later changes stay in the browser.
