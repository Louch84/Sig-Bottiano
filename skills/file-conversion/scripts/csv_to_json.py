#!/usr/bin/env python3
"""CSV to JSON converter"""
import argparse
import csv
import json
import sys

def csv_to_json(input_path, output_path=None, delimiter=',', headers=None):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            if headers:
                fieldnames = headers.split(',')
                reader = csv.DictReader(f, fieldnames=fieldnames, delimiter=delimiter)
            else:
                reader = csv.DictReader(f, delimiter=delimiter)
            
            rows = list(reader)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(rows, f, indent=2)
            return {'success': True, 'count': len(rows), 'output': output_path}
        else:
            return {'success': True, 'data': rows}
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True)
    parser.add_argument('--output', '-o')
    parser.add_argument('--delimiter', '-d', default=',')
    parser.add_argument('--headers', '-H')
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    result = csv_to_json(args.input, args.output, args.delimiter, args.headers)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        elif args.output:
            print(f"Converted {result['count']} rows to {args.output}")
        else:
            print(json.dumps(result['data'], indent=2))

if __name__ == '__main__':
    main()
