#!/usr/bin/env python3
"""Search for property deed on tccsearch.org using scrapling StealthyFetcher"""

from scrapling.fetchers import StealthyFetcher
from scrapling.parser import Selector

# Navigate to tccsearch.org
url = "https://tccsearch.org"

print(f"Fetching: {url}")
response = StealthyFetcher.fetch(url, headless=True, timeout=30000)

print(f"Status: {response.status}")
print(f"URL after redirects: {response.url}")

# Save HTML to file
with open('/home/landon/.openclaw/workspace/tccsearch_output.html', 'w') as f:
    f.write(response.text)

print("HTML saved to tccsearch_output.html")

# Parse the page
page = Selector(response.text)

# Try to find search elements
print("\n--- Looking for search elements ---")

# Check for login button or search link
login_links = page.css('a[href*="login"]')
print(f"Login links found: {len(login_links)}")

search_forms = page.css('form')
print(f"Forms found: {len(search_forms)}")

# Print page title
title = page.css('title::text').get()
print(f"Page title: {title}")

# Look for QuickSearch or property search link
quick_search = page.css('a[href*="QuickSearch"]')
print(f"QuickSearch links: {len(quick_search)}")

# Print first few links
links = page.css('a::attr(href)').getall()[:10]
print(f"\nFirst 10 links: {links}")
