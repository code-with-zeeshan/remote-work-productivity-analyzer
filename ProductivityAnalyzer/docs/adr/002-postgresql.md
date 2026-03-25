# ADR-002: Use PostgreSQL for Data Storage

## Status
Accepted

## Context
v1.0 mixed SQLite and PostgreSQL creating bugs. Needed a single, reliable database.

## Decision
Standardized on PostgreSQL with psycopg2 and connection pooling.

## Rationale
- **ACID compliance**: Reliable for activity logging
- **Connection pooling**: SimpleConnectionPool handles concurrent access
- **Cloud-ready**: Works with local or remote (Aiven, Supabase, etc.)
- **Migrations**: Custom migration system tracks schema versions
- **Indexing**: Proper indexes on timestamp and category columns

## Consequences
- Requires PostgreSQL installation or remote service
- More setup than SQLite for first-time users
- Connection pool must be properly managed (context managers)