## 1. Discovery And Safety

- [x] 1.1 Confirm the target `pingou-o-que-backend` worktree and preserve unrelated local changes before editing.
- [x] 1.2 Run a backend-wide search for domain model symbols ending in `Model` and record every source, test, admin, migration, string reference, docstring, and export reference to update.
- [x] 1.3 Confirm the rename map: `CategoryModel -> Category`, `ExpenseModel -> Expense`, `InstallmentModel -> Installment`, `PaymentModel -> Payment`, `IncomeModel -> Income`, `ChatSessionModel -> ChatSession`, `ChatMessageModel -> ChatMessage`, and `PluggyUserModel -> PluggyUser`.
- [x] 1.4 Inspect current migration history for `api`, `incomes`, and `financial`, then decide whether the safe repository-native path is forward rename migrations or initial migration state updates.

## 2. Rename Implementation

- [x] 2.1 Rename each owning model class in `apps/categories`, `apps/expenses`, `apps/payments`, `apps/incomes`, `apps/chat`, and `apps/financial` while preserving fields, constraints, `Meta.app_label`, `Meta.db_table`, validation, and string output.
- [x] 2.2 Update `apps/api/models.py` exports and all imports from `apps.api.models` or owning model modules to use the suffix-free domain symbols.
- [x] 2.3 Update admin registrations, admin class names, and admin side-effect imports across domain apps and `apps/api/admin.py`.
- [x] 2.4 Update selectors, serializers, filters, services, and views so ORM calls, `DoesNotExist` handling, `Meta.model`, return types, query annotations, and service docstrings use suffix-free domain symbols.
- [x] 2.5 Update string model references such as `"api.CategoryModel"`, `"api.ExpenseModel"`, and `"api.ChatSessionModel"` to their renamed model targets.
- [x] 2.6 Update API helpers and tests under `apps/api/tests`, `apps/*/tests`, and `apps/core/tests` to import and assert through the new suffix-free symbols.
- [x] 2.7 Update documentation and descriptions that refer to old domain `*Model` symbols, while leaving ordinary framework names and generic "model" prose intact.
- [x] 2.8 Add or adjust Django migration state so all class renames are represented without changing existing physical tables or recreating data.
- [x] 2.9 Avoid adding old-name compatibility aliases or changing unrelated framework classes such as `BaseModelViewSet`, `ModelSerializer`, and DRF mixins.

## 3. Validation

- [x] 3.1 Run `rg -n "(CategoryModel|ExpenseModel|InstallmentModel|PaymentModel|IncomeModel|ChatSessionModel|ChatMessageModel|PluggyUserModel)" . -g '*.py' -g '*.md' -g '*.toml' -g '*.yaml'` from `pingou-o-que-backend` and resolve every remaining intentional old-symbol match.
- [x] 3.2 Run `./.venv/bin/python manage.py makemigrations --check --dry-run` from `pingou-o-que-backend` after migration handling to confirm no unexpected model changes remain.
- [x] 3.3 Run migration validation with `./.venv/bin/python manage.py migrate` or the repository-equivalent migration smoke test if database access is available.
- [x] 3.4 Run focused regression tests for affected categories, expenses, payments/installments, incomes, chat, financial, seed data, and validation layers with `./.venv/bin/python -m pytest`.
- [x] 3.5 Run `ruff check .` from `pingou-o-que-backend` and fix rename-related lint issues.
