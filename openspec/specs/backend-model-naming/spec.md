## Requirements

### Requirement: Domain Model Symbols
The backend SHALL expose Django model classes through suffix-free domain names and SHALL NOT keep active backend references to the old `*Model` domain symbols.

#### Scenario: Backend imports domain models
- **WHEN** backend modules import or type-reference a domain Django model
- **THEN** they use suffix-free symbols such as `Category`, `Expense`, `Installment`, `Payment`, `Income`, `ChatSession`, `ChatMessage`, and `PluggyUser`

#### Scenario: Backend is searched for old model symbols
- **WHEN** the backend source tree is searched for old symbols matching the discovered domain `*Model` mapping
- **THEN** no intentional source reference remains outside obsolete generated artifacts that the implementation explicitly justifies

### Requirement: Runtime Behavior Is Preserved
The rename MUST preserve existing database storage, relationships, validation, API routes, response fields, fixtures, and business behavior for every renamed model.

#### Scenario: Existing tables remain stable
- **WHEN** migrations are generated and inspected for the model renames
- **THEN** the physical database tables remain unchanged and existing rows are not deleted or recreated by the rename

#### Scenario: Existing API behavior remains stable
- **WHEN** clients use existing backend endpoints for renamed domains
- **THEN** route paths, request fields, response fields, status codes, totals, and validation errors remain unchanged

### Requirement: Rename Scope Is Limited
The backend SHALL limit this naming change to discovered domain Django model symbols and SHALL NOT rename unrelated framework classes or public API vocabulary.

#### Scenario: Framework names remain unchanged
- **WHEN** the rename is implemented
- **THEN** existing framework or base classes such as `BaseModelViewSet`, `ModelSerializer`, and DRF mixins keep their current names

#### Scenario: Public domain names remain unchanged
- **WHEN** backend serializers, viewsets, URLs, fixtures, and JSON payloads are reviewed
- **THEN** public names that already use domain vocabulary remain compatible unless they referenced an old Python class symbol
