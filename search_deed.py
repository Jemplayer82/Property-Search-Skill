#!/usr/bin/env python3
"""Search Travis County Clerk records for deed by instrument number using Scrapling"""

import sys
from scrapling.fetchers import StealthyFetcher

def search_deed_by_instrument(instrument_number):
    """Search for a deed by instrument number on tccsearch.org"""
    
    url = "https://tccsearch.org"
    
    print(f"Fetching {url}...")
    
    # Use stealthy fetcher to handle any anti-bot protections
    page = StealthyFetcher.fetch(url, headless=True)
    
    # Get the page content
    html_content = page.text
    
    # Check if we got a login form
    if "Logon Name" in html_content or "Password" in html_content:
        print("⚠️  The site requires login credentials to access deed records.")
        print("\nTo search for instrument number: {instrument_number}")
        print("\nOptions:")
        print("1. Provide login credentials (if you have a subscription)")
        print("2. Visit https://tccsearch.org manually to create an account")
        print("3. Try the free public access at the Travis County Clerk's office")
        return None
    
    # Check for disclaimer/acceptance page
    if "disclaimer" in html_content.lower() or "acknowledge" in html_content.lower():
        print("Found disclaimer page - need to accept terms first")
        # Look for accept button/link
        accept_links = page.css('a[href*="Accept"], a[onclick*="Accept"], input[value*="Accept"]')
        if accept_links:
            print(f"Found {len(accept_links)} accept elements")
    
    # Save the page for debugging
    with open('/tmp/tcc_page.html', 'w') as f:
        f.write(html_content)
    
    print(f"Page saved to /tmp/tcc_page.html ({len(html_content)} chars)")
    
    return html_content

if __name__ == "__main__":
    # Default instrument number for 3520 Winding Shore Lane (Willy property)
    instrument = sys.argv[1] if len(sys.argv) > 1 else "2003222117TR"
    
    print(f"Searching for instrument: {instrument}")
    result = search_deed_by_instrument(instrument)
    
    if result:
        print("\nPage content preview:")
        print(result[:1000])
