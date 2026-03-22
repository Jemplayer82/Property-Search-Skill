#!/usr/bin/env python3
"""
Search TCAD for property using Scrapling stealth mode
"""
import sys
sys.path.insert(0, '/home/landon/.openclaw/venvs/scrapling/lib/python3.13/site-packages')

from scrapling.fetchers import StealthySession
import time

# Search for 3520 Winding Shore Lane
search_address = "3520 Winding Shore Ln"

print(f"Searching TCAD for: {search_address}")

# Use session to keep browser open  
with StealthySession(headless=True) as session:
    # Fetch the page with network idle to let JavaScript load
    page = session.fetch('https://travis.prodigycad.com/property-search', network_idle=True)
    
    print(f"Page loaded: {page.url}")
    
    # Wait for JavaScript to render
    time.sleep(5)
    
    # Try to find search box by different methods
    print("\nTrying to find search input...")
    
    # Method 1: By attribute containing 'search'
    search_input = page.css('input[placeholder*="Search"]').get()
    if search_input:
        print("Found by placeholder 'Search'")
    else:
        # Method 2: All text inputs
        inputs = page.find_all('input', {'type': 'text'})
        print(f"Found {len(inputs)} text inputs")
        for i, inp in enumerate(inputs[:5]):
            attrs = {k: v for k, v in inp.attrs.items()}
            print(f"  Input {i}: {attrs}")
        
        # Method 3: Look for any input with 'Search' in any attribute
        all_inputs = page.find_all('input')
        for inp in all_inputs:
            for attr, val in inp.attrs.items():
                if 'search' in str(val).lower():
                    print(f"Found input with 'search' in {attr}: {val}")
                    search_input = inp
                    break
            if search_input:
                break
    
    if search_input:
        print(f"\nFound search input, filling with: {search_address}")
        # Fill in the address
        search_input.fill(search_address)
        
        # Submit the search by pressing Enter
        search_input.press('Enter')
        
        # Wait for AJAX results
        time.sleep(6)
        
        # Get updated content  
        page = session.fetch('https://travis.prodigycad.com/property-search', network_idle=True)
        time.sleep(3)
        
        # Look for results
        rows = page.css('[role="row"]').getall()
        print(f"\nFound {len(rows)} rows in results")
        
        if len(rows) > 1:
            for row in rows[1:10]:  # Skip header
                cells = row.css('[role="gridcell"]').getall()
                if len(cells) >= 9:
                    prop_id = cells[2].text().strip() if len(cells) > 2 else ''
                    owner = cells[7].text().strip() if len(cells) > 7 else ''
                    address = cells[8].text().strip() if len(cells) > 8 else ''
                    if prop_id and address:
                        print(f"\nPropID: {prop_id}")
                        print(f"  Owner: {owner}")
                        print(f"  Address: {address}")
        else:
            print("No results found in TCAD")
    else:
        print("\nCould not find search input - page may not have loaded properly")
        # Save HTML for debugging
        html = str(page)
        with open('/tmp/tcad_debug.html', 'w') as f:
            f.write(html[:5000])
        print("Saved first 5000 chars of HTML to /tmp/tcad_debug.html")
