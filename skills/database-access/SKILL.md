---
name: database-access
description: Connect to and query SQL databases including SQLite, PostgreSQL, and MySQL. Supports connection management, parameterized queries, schema introspection, and transaction handling. Use when the user needs to query databases, manage data, or perform CRUD operations.
---

# Database Access

Query SQL databases with unified interface.

## Quick Start

SQLite (built-in):
```bash
python3 scripts/query_sqlite.py --db path/to/db.sqlite --query "SELECT * FROM users"
```

PostgreSQL:
```bash
python3 scripts/query_postgres.py --host localhost --db mydb --query "SELECT * FROM users"
```

MySQL:
```bash
python3 scripts/query_mysql.py --host localhost --db mydb --query "SELECT * FROM users"
```

## Scripts

- `scripts/query_sqlite.py` - SQLite queries
- `scripts/query_postgres.py` - PostgreSQL queries
- `scripts/query_mysql.py` - MySQL queries
- `scripts/schema_introspect.py` - Get table schemas

## Connection Management

Use environment variables or `--env-file` for credentials:
```bash
export DB_HOST=localhost
export DB_USER=admin
export DB_PASS=secret
export DB_NAME=mydb
```

## Usage Examples

### Parameterized queries
```bash
python3 scripts/query_sqlite.py --db app.db --query "SELECT * FROM users WHERE id = ?" --params 42
```

### Schema introspection
```bash
python3 scripts/schema_introspect.py --db app.db --type sqlite
```

### Transactions
```bash
python3 scripts/query_postgres.py --host db.example.com --query "BEGIN; UPDATE accounts SET balance = balance - 100 WHERE id = 1; COMMIT;"
```

## References

See [references/sql_patterns.md](references/sql_patterns.md) for common SQL patterns and best practices.
