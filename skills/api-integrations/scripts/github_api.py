#!/usr/bin/env python3
"""GitHub API client"""
import requests
import argparse
import json
import os
import sys

BASE_URL = 'https://api.github.com'

def api_call(endpoint, method='GET', data=None, params=None, token=None):
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'OpenClaw-GitHub-Client'
    }
    if token:
        headers['Authorization'] = f'token {token}'
    
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    
    try:
        if method == 'GET':
            resp = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            resp = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            resp = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            resp = requests.delete(url, headers=headers)
        else:
            return {'error': f'Unsupported method: {method}'}
        
        resp.raise_for_status()
        return resp.json() if resp.content else {'success': True}
    except requests.exceptions.HTTPError as e:
        return {'error': f'HTTP {e.response.status_code}: {e.response.text}'}
    except Exception as e:
        return {'error': str(e)}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', '-e', required=True)
    parser.add_argument('--method', '-m', default='GET')
    parser.add_argument('--data', '-d')
    parser.add_argument('--params', '-p')
    parser.add_argument('--token', default=os.getenv('GITHUB_TOKEN'))
    parser.add_argument('--json', '-j', action='store_true')
    args = parser.parse_args()
    
    data = json.loads(args.data) if args.data else None
    params = json.loads(args.params) if args.params else None
    
    result = api_call(args.endpoint, args.method, data, params, args.token)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
