#!/usr/bin/env python3
"""
Web Search - Using Tavily API
Adds real-time research capability
"""

import requests
import json

TAVILY_API_KEY = "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"

def search(query, max_results=5):
    """Search the web using Tavily"""
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            results = response.json()
            return {
                "status": "success",
                "results": results.get("results", []),
                "answer": results.get("answer", "")
            }
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def quick_answer(query):
    """Get quick answer from Tavily"""
    url = "https://api.tavily.com/extract"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": TAVILY_API_KEY,
        "query": query
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        if response.status_code == 200:
            return {"status": "success", "answer": response.json()}
        else:
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Test
    result = search("Python best practices 2026")
    print(json.dumps(result, indent=2))
