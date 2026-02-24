# Memory Architecture

## Vector Memory

Stores content with searchable indices for semantic retrieval.

### Fields
- `id`: Unique identifier
- `content`: The stored text
- `tags`: Categorical labels
- `metadata`: Arbitrary key-value data
- `index`: Searchable word tokens

### Scoring
Simple word overlap scoring for similarity ranking.

## Knowledge Graph

Nodes connected by typed relations.

### Node Structure
```json
{
  "name": "Concept",
  "type": "entity|concept|event",
  "properties": {},
  "created": "timestamp"
}
```

### Relation Structure
```json
{
  "from": "Node A",
  "to": "Node B",
  "type": "relates_to|depends_on|part_of",
  "created": "timestamp"
}
```

## Best Practices

1. Tag memories with relevant categories
2. Keep content focused (one concept per memory)
3. Use consistent relation types in graphs
4. Query with specific terms for better results
