# SQL Patterns Reference

## Common Queries

### Pagination
```sql
SELECT * FROM table ORDER BY id LIMIT 20 OFFSET 40;
```

### Search
```sql
SELECT * FROM table WHERE name ILIKE '%search%';
```

### Aggregations
```sql
SELECT category, COUNT(*), AVG(value) 
FROM table 
GROUP BY category 
HAVING COUNT(*) > 5;
```

## Best Practices

1. Use parameterized queries to prevent SQL injection
2. Add indexes on frequently queried columns
3. Use transactions for multi-statement operations
4. Limit results with pagination for large datasets
