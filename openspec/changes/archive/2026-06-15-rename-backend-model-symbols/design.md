## Context

The Django backend keeps domain apps under `apps/`, with read behavior in selectors, write behavior in services, validation in serializers/models, and public API wiring in thin viewsets. The current backend model symbols follow a `*Model` suffix pattern across several apps:

- `apps/categories/models.py`: `CategoryModel`
- `apps/expenses/models.py`: `ExpenseModel`
- `apps/payments/models.py`: `InstallmentModel`, `PaymentModel`
- `apps/incomes/models.py`: `IncomeModel`
- `apps/chat/models.py`: `ChatSessionModel`, `ChatMessageModel`
- `apps/financial/models.py`: `PluggyUserModel`

Some domain models use `Meta.app_label = "api"` and are re-exported through `apps/api/models.py`; migrations also refer to the old class names. The requested convention is to remove the `Model` suffix from these backend Django model symbols and use the domain names directly.

## Goals / Non-Goals

**Goals:**
- Rename every backend Django model class ending in `Model` to a suffix-free domain symbol:
  `Category`, `Expense`, `Installment`, `Payment`, `Income`, `ChatSession`, `ChatMessage`, and `PluggyUser`.
- Update all backend Python references, type hints, admin registrations/classes, serializers, filters, selectors, services, views, tests, string model references, cross-app exports, and migrations that depend on the old names.
- Preserve existing database table names, related names, constraints, endpoint paths, serializer fields, response fields, fixtures, and business behavior.
- Validate the rename with repository-native search, migration, test, and lint commands.

**Non-Goals:**
- Rename framework/base classes whose names include `Model` but are not domain model symbols, such as `BaseModelViewSet` or DRF mixins.
- Rename endpoint paths, serializer field names, fixture keys, JSON fields, database tables, or user-facing domain vocabulary.
- Introduce compatibility aliases like `PaymentModel = Payment` after the sweep.
- Change business rules, query behavior, validation rules, or app boundaries while performing the rename.

## Decisions

1. Apply the suffix removal consistently to all backend Django model symbols.

   Rationale: Renaming only one model would leave the old pattern in place and fail the requested convention. The target mapping is explicit and finite:
   `CategoryModel -> Category`, `ExpenseModel -> Expense`, `InstallmentModel -> Installment`, `PaymentModel -> Payment`, `IncomeModel -> Income`, `ChatSessionModel -> ChatSession`, `ChatMessageModel -> ChatMessage`, and `PluggyUserModel -> PluggyUser`.

   Alternative considered: Rename only payment-related models first. Rejected because the user clarified that all occurrences in this pattern should match.

2. Use direct renames instead of compatibility aliases.

   Rationale: The requested outcome is a clean naming pattern. Temporary aliases would leave two active names, hide missed imports, and make future code drift easier.

   Alternative considered: Keep aliases during transition. Rejected because this backend is local and can be swept atomically with validation.

3. Keep public API and database names stable.

   Rationale: The class names are internal Django/Python symbols. Existing route paths, serializer fields, related names, fixtures, and explicit `db_table` values are part of runtime behavior and should not change as part of a symbol cleanup.

   Alternative considered: Rename public names alongside class names. Rejected because it would create avoidable API and data migration risk.

4. Treat Django migration state as a set of model renames, not delete/create operations.

   Rationale: Django model class names are part of migration state even when physical tables are stable. The implementation must avoid destructive migration behavior and must handle string relations such as `"api.CategoryModel"` and `"api.ChatSessionModel"`.

   Alternative considered: Only edit Python source and tests. Rejected because migration checks could still detect pending state changes or generate destructive operations.

5. Sweep cross-app consumers and documentation references.

   Rationale: The old symbols appear in domain apps, `apps/api` re-exports, tests, admin side-effect imports, service docstrings, docs, and migrations. Updating only model modules would break imports and leave misleading descriptions.

   Alternative considered: Restrict the change to runtime code. Rejected because tests and docs would keep the old convention alive.

## Risks / Trade-offs

- Django migration autodetection may infer delete/create operations for several models -> Inspect migration output and use explicit rename-state operations or state edits that preserve existing tables.
- Editing initial migrations may conflict with already-applied local databases -> Prefer forward migrations for applied environments unless the repository intentionally treats early initial migrations as mutable.
- Broad renames can accidentally touch non-domain framework names -> Limit replacements to the discovered model symbol mapping and avoid `BaseModelViewSet`, `ModelSerializer`, and `ListModelMixin`.
- String model relations and migration `model_name` references can be missed -> Include migrations and quoted model references in the search checklist.
- The backend working tree currently contains unrelated local changes, including `apps/transactions/` -> Preserve unrelated edits and update only files that contain old model symbols or required descriptions.

## Migration Plan

1. Rename each model class in its owning `models.py` file while preserving fields, `Meta.app_label`, `Meta.db_table`, constraints, validation, and string output.
2. Update imports, annotations, ORM calls, admin registrations/classes, serializer/filter `Meta.model`, string relations, cross-app exports, tests, fixtures references, and docs across `pingou-o-que-backend`.
3. Create or adjust Django migration state so the class renames are represented safely and do not rename tables or recreate data.
4. Run validation commands. Roll back by reverting the rename commit and associated migration if needed.

## Open Questions

- Should existing initial migrations be edited because the project is early, or should new forward rename migrations be added for safer applied-database behavior? The implementation should inspect current migration history and choose the least risky repository-native path.
