#!/usr/bin/env python3
"""
Search TCAD using DynamicFetcher with actual browser
"""
import sys
sys.path.insert(0, '/home/landon/.openclaw/venvs/scrapling/lib/python3.13/site-packages')

from scrapling.fetchers import DynamicSession
import time

search_address = "3520 Winding Shore Ln"

print(f"Searching TCAD for: {search_address}")

with DynamicSession(headless=True, network_idle=True) as session:
    # Load the page with network idle to ensure JavaScript loads
    page = session.fetch('https://travis.prodigycad.com/property-search')
    
    print(f"Page loaded: {page.url}")
    
    # Wait for the page to fully render
    time.sleep(5)
    
    # Find the search input
    search_input = page.css('input[placeholder*="Search"]').get()
    
    if search_input:
        print(f"Found search input")
        
        # Fill the search
        search_input.fill(search_address)
        
        # Submit the form
        search_input.press('Enter')
        
        # Wait for results
        time.sleep(5)
        
        # Check for results
        rows = page.css('[role="row"]').getall()
        print(f"\nFound {len(rows)} rows")
        
        # Show results (skip header)
        for row in rows[1:10]:
            cells = row.css('[role="gridcell"]').getall()
            if len(cells) >= 9:
                prop_id = cells[2].text().strip()
                owner = cells[7].text().strip()
                address = cells[8].text().strip()
                if prop_id:
                    print(f"\nPropID: {prop_id}")
                    print(f"  Owner: {owner}")
                    print(f"  Address: {address}")
    else:
        print("Search input not found")
        # Debug - show page structure
        print("\nPage structure:")
        inputs = page.find_all('input')
        print(f"Found {len(inputs)} inputs total")
        
        # Look for any input
        for inp in inputs[:5]:
            print(f"Input: {dict(inp.attrs)}")
