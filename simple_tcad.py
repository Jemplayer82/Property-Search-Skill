#!/usr/bin/env python3
"""
Simple TCAD check with DynamicSession
"""
import sys
sys.path.insert(0, '/home/landon/.openclaw/venvs/scrapling/lib/python3.13/site-packages')

from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True) as session:
    page = session.fetch('https://travis.prodigycad.com/property-search')
    
    print("Page loaded successfully")
    print(f"URL: {page.url}")
    
    # Simple check for inputs
    inputs = page.find_all('input')
    print(f"\nNumber of inputs: {len(inputs)}")
    
    if inputs:
        for i, inp in enumerate(inputs[:3]):
            print(f"Input {i}: {inp.get('placeholder', 'no placeholder')}")
    
    print("\n--- Done ---")
