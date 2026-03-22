#!/usr/bin/env python3
"""
Debug TCAD page structure
"""
import sys
sys.path.insert(0, '/home/landon/.openclaw/venvs/scrapling/lib/python3.13/site-packages')

from scrapling.fetchers import StealthyFetcher

# Just fetch and examine the page
page = StealthyFetcher.fetch('https://travis.prodigycad.com/property-search', network_idle=True)

print(f"URL: {page.url}")
print(f"Status: {page.status}")
print(f"\n--- Looking for search elements ---")

# Find all inputs
inputs = page.find_all('input')
print(f"\nTotal inputs found: {len(inputs)}")

for i, inp in enumerate(inputs[:10]):
    attrs = dict(inp.attrs)
    print(f"\nInput {i}:")
    for k, v in attrs.items():
        print(f"  {k}: {v}")

# Also look for textareas
print("\n--- Textareas ---")
textareas = page.find_all('textarea')
print(f"Found {len(textareas)} textareas")

# Look for any element with 'search' in attributes
print("\n--- Elements with 'search' ---")
search_elements = page.css('[class*="search"], [id*="search"], [placeholder*="search"]').getall()
print(f"Found {len(search_elements)} elements with 'search'")
for el in search_elements[:5]:
    print(f"  Tag: {el.name}, Classes: {el.get('class')}, ID: {el.get('id')}")

# Save full HTML for inspection
with open('/tmp/tcad_full.html', 'w') as f:
    f.write(str(page))
print(f"\nFull HTML saved to /tmp/tcad_full.html")
