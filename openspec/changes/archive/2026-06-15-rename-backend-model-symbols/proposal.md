## Why

The backend currently uses a Django model naming pattern with domain classes ending in `Model`, such as `InstallmentModel` and `PaymentModel`. The requested convention is to use the domain name directly for all backend Django model classes, reducing suffix noise and making model references read consistently across the codebase.

## What Changes

- Rename every backend Django model class that follows the `*Model` pattern to its domain name:
  - `CategoryModel` -> `Category`
  - `ExpenseModel` -> `Expense`
  - `InstallmentModel` -> `Installment`
  - `PaymentModel` -> `Payment`
  - `IncomeModel` -> `Income`
  - `ChatSessionModel` -> `ChatSession`
  - `ChatMessageModel` -> `ChatMessage`
  - `PluggyUserModel` -> `PluggyUser`
- Update all backend imports, type hints, admin registrations, selectors, serializers, services, tests, model string references, migrations, and cross-app exports that reference the old `*Model` symbols.
- Preserve existing API behavior, endpoint names, response field names, business validation, related names, and physical database tables.
- Handle Django migration state so class renames are represented as model renames instead of destructive delete/create operations.
- Leave framework and infrastructure names that are not domain model symbols unchanged, such as `BaseModelViewSet`, DRF mixins, and ordinary prose uses of the word "model".

## Capabilities

### New Capabilities
- `backend-model-naming`: Backend Django model symbols use domain names without the `Model` suffix while preserving public API and database behavior.

### Modified Capabilities
- None.

## Impact

- Affected backend areas include model modules, admin modules, serializers, filters, selectors, services, views, route helpers, tests, cross-app exports in `apps/api/models.py`, model string references such as `"api.CategoryModel"`, and migrations in `apps/api`, `apps/incomes`, and `apps/financial`.
- No frontend API contract, route path, serializer field, related name, business rule, or database table rename is intended.
- Validation should include a backend-wide search for old `*Model` symbols, Django migration checks, focused domain API/service tests, seed and validation-layer tests, and linting.
