# ADR-003: Repository Pattern for Data Access

## Status
Accepted

## Context
v1.0 had SQL scattered across UI, tracker, and reporting modules with inconsistent table/column names.

## Decision
Implemented the Repository Pattern with dedicated repository classes per table.

## Rationale
- **Single responsibility**: Each repo handles one table
- **Testability**: Repos accept DatabasePool, easily mocked
- **Consistency**: All SQL in one place per entity
- **Type safety**: Repos return dataclass models, not raw tuples

## Structure
- `ActivityRepository` -> `activity_log` table
- `FocusSettingsRepository` -> `focus_settings` table
- `GoalsRepository` -> `goals` table

## Consequences
- Slight overhead for simple queries
- Must update repo when schema changes
- All components depend on repos, not raw SQL