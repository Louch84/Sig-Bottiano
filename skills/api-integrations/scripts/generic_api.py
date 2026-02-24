#!/usr/bin/env python3
"""Generic API client for any HTTP service"""
import requests
import argparse
import json
import os
import sys

def api_call(url, method='GET', data=None, headers=None, timeout=30):
    headers = headers or {}
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, timeout=timeout)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == 'PUT':
            resp = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers, timeout=timeout)
        elif method == 'PATCH':
            resp = requests.patch(url, headers=headers, json=data, timeout=timeout)
        else:
            return {'error': f'Unsupported method: {method}'}
        
        result = {
            'status': resp.status_code,
            'headers': dict(resp.headers)
        }
        
        try:
            result['data'] = resp.json()
        except:
            result['text'] = resp.text
        
        return result
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', '-u', required=True)
    parser.add_argument('--method', '-m', default='GET')
    parser.add_argument('--data', '-d')
    parser.add_argument('--header', '-H', action='append')
    parser.add_argument('--timeout', '-t', type=int, default=30)
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    headers = {}
    if args.header:
        for h in args.header:
            key, val = h.split(':', 1)
            headers[key.strip()] = val.strip()
    
    data = json.loads(args.data) if args.data else None
    result = api_call(args.url, args.method, data, headers, args.timeout)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get('error'):
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        if 'data' in result:
            print(json.dumps(result['data'], indent=2))
        else:
            print(result.get('text', ''))

if __name__ == '__main__':
    main()
