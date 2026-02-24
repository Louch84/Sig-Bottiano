---
name: advanced-memory
description: Vector search and knowledge graph capabilities for semantic memory. Supports ChromaDB for vector storage, embedding generation, similarity matching, and knowledge graph CRUD operations. Use when the user needs semantic search, memory retrieval, or building knowledge bases.
---

# Advanced Memory

Semantic search and knowledge graphs for intelligent memory.

## Quick Start

Store a memory:
```bash
python3 scripts/store_memory.py --content "Important fact to remember" --tags project,idea
```

Search memories:
```bash
python3 scripts/search_memory.py --query "What was that important fact?" --limit 5
```

Knowledge graph - Add node:
```bash
python3 scripts/kg_add.py --node "Project X" --type project --relations "depends_on:Project Y"
```

## Scripts

### Vector Memory (ChromaDB)
- `scripts/store_memory.py` - Store memories with embeddings
- `scripts/search_memory.py` - Semantic search memories
- `scripts/delete_memory.py` - Remove memories
- `scripts/list_memories.py` - List all memories

### Knowledge Graph
- `scripts/kg_add.py` - Add nodes/relations
- `scripts/kg_query.py` - Query the graph
- `scripts/kg_delete.py` - Remove nodes/relations
- `scripts/kg_visualize.py` - Export graph visualization

## Configuration

Default storage: `~/.openclaw/memory/chromadb/`

Environment variables:
```bash
export MEMORY_DB_PATH=/custom/path
export OPENAI_API_KEY=sk-xxx  # For embeddings (optional)
```

## Usage Examples

### Store with metadata
```bash
python3 scripts/store_memory.py \
  --content "Meeting with client about API design" \
  --tags meeting,api,client \
  --metadata '{"date": "2024-01-15", "priority": "high"}'
```

### Semantic search with filters
```bash
python3 scripts/search_memory.py \
  --query "API discussions" \
  --filter-tags meeting \
  --min-score 0.7 \
  --limit 10
```

### Knowledge graph query
```bash
python3 scripts/kg_query.py --node "Project X" --depth 2
```

### Import from files
```bash
python3 scripts/store_memory.py --import-file notes.md --split-by heading
```

## References

- [references/memory_architecture.md](references/memory_architecture.md) - Memory system design
- [references/kg_patterns.md](references/kg_patterns.md) - Knowledge graph patterns
