#!/usr/bin/env python3
"""Query SQLite databases"""
import sqlite3
import json
import argparse
import sys

def query_db(db_path, query, params=None):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params.split(',') if isinstance(params, str) else params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            return {'data': result, 'count': len(result)}
        else:
            conn.commit()
            return {'affected': cursor.rowcount}
            
    except Exception as e:
        return {'error': str(e)}
    finally:
        conn.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True)
    parser.add_argument('--query', '-q', required=True)
    parser.add_argument('--params', '-p')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = query_db(args.db, args.query, args.params)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        elif 'data' in result:
            for row in result['data']:
                print(json.dumps(row))
        else:
            print(f"Affected rows: {result['affected']}")

if __name__ == '__main__':
    main()
