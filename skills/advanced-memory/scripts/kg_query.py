#!/usr/bin/env python3
"""Simple knowledge graph using JSON storage"""
import argparse
import json
import os
from datetime import datetime

KG_FILE = os.path.expanduser('~/.openclaw/memory/knowledge_graph.json')

def load_graph():
    if os.path.exists(KG_FILE):
        with open(KG_FILE) as f:
            return json.load(f)
    return {'nodes': {}, 'relations': []}

def save_graph(graph):
    os.makedirs(os.path.dirname(KG_FILE), exist_ok=True)
    with open(KG_FILE, 'w') as f:
        json.dump(graph, f, indent=2)

def add_node(name, node_type='concept', properties=None):
    graph = load_graph()
    graph['nodes'][name] = {
        'type': node_type,
        'properties': properties or {},
        'created': datetime.now().isoformat()
    }
    save_graph(graph)
    return {'success': True}

def add_relation(from_node, to_node, relation_type):
    graph = load_graph()
    if from_node not in graph['nodes']:
        add_node(from_node)
    if to_node not in graph['nodes']:
        add_node(to_node)
    
    graph['relations'].append({
        'from': from_node,
        'to': to_node,
        'type': relation_type,
        'created': datetime.now().isoformat()
    })
    save_graph(graph)
    return {'success': True}

def query_node(name, depth=1):
    graph = load_graph()
    if name not in graph['nodes']:
        return {'error': f'Node "{name}" not found'}
    
    result = {
        'node': graph['nodes'][name],
        'relations': []
    }
    
    for rel in graph['relations']:
        if rel['from'] == name or rel['to'] == name:
            result['relations'].append(rel)
    
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--node', '-n')
    parser.add_argument('--type', '-t', default='concept')
    parser.add_argument('--relations', '-r')
    parser.add_argument('--depth', '-d', type=int, default=1)
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    if args.node:
        result = query_node(args.node, args.depth)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if 'error' in result:
                print(f"Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
            print(f"Node: {args.node}")
            print(f"Type: {result['node']['type']}")
            if result['relations']:
                print("\nRelations:")
                for r in result['relations']:
                    print(f"  {r['from']} --[{r['type']}]--> {r['to']}")

if __name__ == '__main__':
    main()
