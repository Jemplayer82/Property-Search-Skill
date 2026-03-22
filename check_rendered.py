#!/usr/bin/env python3
"""
Search for all Winding Shore properties in TCAD using DynamicSession
"""
import sys
sys.path.insert(0, '/home/landon/.openclaw/venvs/scrapling/lib/python3.13/site-packages')

from scrapling.fetchers import DynamicSession
import time

with DynamicSession(headless=True, disable_resources=True) as session:
    # Navigate to search page
    page = session.fetch('https://travis.prodigycad.com/property-search')
    time.sleep(5)  # Wait for JavaScript
    
    # Check if we have any content
    print(f"Page title: {page.title if hasattr(page, 'title') else 'N/A'}")
    print(f"Page text length: {len(page.text)}")
    
    # Look for specific text
    if 'Winding Shore' in page.text:
        print("\nWinding Shore found in page")
    else:
        print("\nNo Winding Shore in static content")
    
    # Check for the search input via JavaScript evaluation
    try:
        # Try to evaluate JS to get the page state
        print("\n--- Checking for rendered content ---")
        # Find all elements
        all_text = page.text
        print(f"Page contains {len(all_text)} characters")
        print(f"First 500 chars: {all_text[:500]}")
    except Exception as e:
        print(f"Error: {e}")
