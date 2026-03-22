#!/usr/bin/env python3
"""
Check TCAD with StealthyFetcher and wait
"""
import sys
sys.path.insert(0, '/home/landon/.openclaw/venvs/scrapling/lib/python3.13/site-packages')

from scrapling.fetchers import StealthyFetcher

# Fetch with longer wait for JavaScript
page = StealthyFetcher.fetch(
    'https://travis.prodigycad.com/property/550733',
    wait=5000  # Wait 5 seconds after load
)

print(f"Fetched page: {page.url}")
print(f"Page length: {len(page.text)} chars")

# Look for Winding Shore
if 'Winding Shore' in page.text:
    print("\n✓ Winding Shore found!")
    # Extract lines containing it
    lines = [l for l in page.text.split('\n') if 'Winding Shore' in l]
    print(f"Found {len(lines)} mentions")
    for line in lines[:5]:
        print(f"  {line.strip()}")
else:
    print("\n✗ Winding Shore not found in page text")
    print("\nFirst 1000 chars of page:")
    print(page.text[:1000])
