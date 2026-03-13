#!/usr/bin/env python3
"""Web Scraper - Pull data from anywhere"""
import requests
from bs4 import BeautifulSoup
import json

def scrape(url):
    """Scrape a webpage"""
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Get title
        title = soup.title.string if soup.title else "No title"
        
        # Get all text (first 2000 chars)
        text = soup.get_text()[:2000]
        
        return {"title": title, "text": text, "status": "ok"}
    except Exception as e:
        return {"error": str(e)}

def scrape_headlines(url):
    """Get headlines from a page"""
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        headlines = []
        for h in soup.find_all(['h1', 'h2', 'h3'])[:10]:
            if h.get_text().strip():
                headlines.append(h.get_text().strip())
        
        return headlines
    except:
        return []

# Quick tests
if __name__ == "__main__":
    print("Testing scraper...")
    print(scrape_headlines("https://news.ycombinator.com")[:5])
