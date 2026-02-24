#!/usr/bin/env python3
"""Query PostgreSQL databases"""
import argparse
import json
import sys
import os

def query_db(host, db, user, password, query, params=None, port=5432):
    try:
        import psycopg2
        import psycopg2.extras
        
        conn = psycopg2.connect(
            host=host, database=db, user=user, password=password, port=port
        )
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        if params:
            params = params.split(',') if isinstance(params, str) else params
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if cursor.description:
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            conn.close()
            return {'data': result, 'count': len(result)}
        else:
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return {'affected': affected}
            
    except ImportError:
        return {'error': 'psycopg2 not installed. Run: pip install psycopg2-binary'}
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default=os.getenv('DB_HOST', 'localhost'))
    parser.add_argument('--port', type=int, default=int(os.getenv('DB_PORT', 5432)))
    parser.add_argument('--db', default=os.getenv('DB_NAME'))
    parser.add_argument('--user', default=os.getenv('DB_USER'))
    parser.add_argument('--password', default=os.getenv('DB_PASS'))
    parser.add_argument('--query', '-q', required=True)
    parser.add_argument('--params', '-p')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = query_db(args.host, args.db, args.user, args.password, args.query, args.params, args.port)
    
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
