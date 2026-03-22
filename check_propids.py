#!/usr/bin/env python3
"""
Check nearby TCAD PropIDs using StealthyFetcher
"""
import sys
sys.path.insert(0, '/home/landon/.openclaw/venvs/scrapling/lib/python3.13/site-packages')

from scrapling.fetchers import StealthyFetcher

# Try PropIDs around 550733 (which is 3524 Winding Shore)
target_ids = [550730, 550731, 550732, 550733, 550734, 550735]

print("Checking nearby PropIDs using StealthyFetcher...\n")

for prop_id in target_ids:
    url = f'https://travis.prodigycad.com/property/{prop_id}'
    try:
        page = StealthyFetcher.fetch(url, network_idle=True)
        text = page.text
        
        # Look for property address in the page
        if 'Winding Shore' in text:
            print(f"\n=== PropID {prop_id} ===")
            # Extract address
            import re
            addr_match = re.search(r'(\d+)\s+Winding\s+Shore[^\n]*', text)
            if addr_match:
                print(f"Address: {addr_match.group(0)}")
        else:
            print(f"PropID {prop_id}: Not a Winding Shore property")
    except Exception as e:
        print(f"PropID {prop_id}: {type(e).__name__}")

print("\n--- Check complete ---")
