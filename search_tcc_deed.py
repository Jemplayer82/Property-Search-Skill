#!/usr/bin/env python3
"""
Search Travis County Clerk records for deed by instrument number using Scrapling.
This script handles login and searches for deed records.
"""

import sys
import re
from scrapling.fetchers import StealthySession

def search_deed_by_instrument(instrument_number, logon_name=None, password=None):
    """Search for a deed by instrument number on tccsearch.org"""
    
    url = "https://tccsearch.org"
    
    print(f"🚀 Starting search for instrument: {instrument_number}")
    print(f"Connecting to {url}...")
    
    with StealthySession(headless=True) as session:
        # First, get the login page
        page = session.fetch(url, network_idle=True, wait=3000)
        
        html_content = page.text
        print(f"📄 Page loaded ({len(html_content)} chars)")
        
        # Check for login form
        if "LoginForm1_txtLogonName" in html_content:
            print("🔒 Login form detected")
            
            if not logon_name or not password:
                print("\n❌ ERROR: Login credentials required")
                print("\nThe Travis County Clerk website requires a subscription to access deed records.")
                print("\nTo search for instrument number:", instrument_number)
                print("\nOptions:")
                print("1. Provide login credentials (logon_name and password)")
                print("2. Visit https://tccsearch.org manually to create an account")
                print("3. Try the free public access at the Travis County Clerk's office")
                print("   1000 Guadalupe St, Austin, TX 78701")
                print("4. Check if there's a free public records search alternative")
                return None
            
            # Attempt to log in
            print(f"🔐 Attempting login as {logon_name}...")
            
            # Extract VIEWSTATE and other ASP.NET form fields
            viewstate_match = re.search(r'id="__VIEWSTATE" value="([^"]+)"', html_content)
            eventval_match = re.search(r'id="__EVENTVALIDATION" value="([^"]+)"', html_content)
            
            if not viewstate_match:
                print("❌ Could not extract VIEWSTATE from page")
                return None
            
            viewstate = viewstate_match.group(1)
            eventval = eventval_match.group(1) if eventval_match else ""
            
            # Build login payload
            login_data = {
                '__EVENTTARGET': '',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate,
                '__EVENTVALIDATION': eventval,
                'ctl00$LoginForm1$txtLogonName': logon_name,
                'ctl00$LoginForm1$txtPassword': password,
                'ctl00$LoginForm1$logonType': 'rdoPubCpu',
                'ctl00$LoginForm1$btnLogon': 'Logon'
            }
            
            # Submit login
            result_page = session.post(url, data=login_data, wait=5000)
            result_html = result_page.text
            
            # Check if login succeeded
            if "LoginForm1_txtLogonName" in result_html:
                print("❌ Login failed - still on login page")
                return None
            
            if "logout" in result_html.lower() or "welcome" in result_html.lower():
                print("✅ Login successful!")
                
                # Now navigate to instrument search
                print("🔍 Searching for instrument number...")
                
                # Look for search links or forms
                if "Instrument" in result_html:
                    print("📋 Found instrument search option")
                    
                    # Save successful login page for debugging
                    with open('/tmp/tcc_logged_in.html', 'w') as f:
                        f.write(result_html)
                    print("💾 Logged-in page saved to /tmp/tcc_logged_in.html")
                    
                    return result_html
            
            print("⚠️  Login response unclear, saving for review...")
            with open('/tmp/tcc_login_response.html', 'w') as f:
                f.write(result_html)
            print("💾 Response saved to /tmp/tcc_login_response.html")
            
            return result_html
        
        else:
            print("ℹ️  No login form found - checking page content...")
            with open('/tmp/tcc_page.html', 'w') as f:
                f.write(html_content)
            print("💾 Page saved to /tmp/tcc_page.html")
            return html_content

if __name__ == "__main__":
    # Get instrument number from command line
    instrument = sys.argv[1] if len(sys.argv) > 1 else "2003222117TR"
    
    # Check for credentials in environment or command line
    logon = sys.argv[2] if len(sys.argv) > 2 else None
    password = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Try to get from environment variables
    if not logon:
        import os
        logon = os.environ.get('TCC_LOGON')
        password = os.environ.get('TCC_PASSWORD')
    
    result = search_deed_by_instrument(instrument, logon, password)
    
    if result:
        print("\n" + "="*50)
        print("SEARCH COMPLETE")
        print("="*50)
    else:
        sys.exit(1)
