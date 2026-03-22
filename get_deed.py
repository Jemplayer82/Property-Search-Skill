import sys
import time
from scrapling import StealthyFetcher

def search_tcad(address):
    """
    Search Travis County Appraisal District for property by address.
    Returns owner name and property ID if found.
    """
    url = "https://tcad.org/property-search/"
    fetcher = StealthyFetcher(
        headless=True,
        bypass_csp=True,
        ignore_http_errors=True,
        disable_resources=True,
        timeout=30000,
    )
    try:
        # Go to the TCAD property search page
        page = fetcher.fetch(url)
        
        # Wait for the search form to load
        # Note: We might need to interact with the page to enter the address
        # Since we are using StealthyFetcher, we can use its methods to fill forms
        # However, StealthyFetcher is more for fetching and parsing, not for complex interactions.
        # We might need to use a different approach for form submission.
        # Let's try to get the page and then parse for the form and submit via POST if possible.
        # Alternatively, we can use the fetcher's fill and click methods if available.
        # Looking at scrapling documentation, StealthyFetcher has methods like fill, click, etc.
        
        # We'll try to fill the address in the search box and submit.
        # First, let's see what the page looks like by getting the HTML and then we can decide.
        # But for simplicity, we'll assume we can find an input for address and a search button.
        
        # We'll try to fill the address in the input with id or name containing 'address'
        # and then click the search button.
        
        # However, without knowing the exact structure, we might need to inspect.
        # Let's try a different approach: use the fetcher to go to the page and then
        # use the built-in methods to interact.
        
        # We'll wait for the page to load and then try to fill the form.
        # Since we are in a stealthy fetcher, we can use:
        # page.fill('input[name="address"]', address)
        # page.click('button:has-text("Search")')
        
        # But let's first get the page and see what we can find.
        # We'll print the page title to see if we loaded correctly.
        print("Page title:", page.title())
        
        # Now, let's try to find the address input and search button.
        # We'll use CSS selectors.
        # Common patterns for address input: input[name*="address"], input[id*="address"], etc.
        # We'll try a few.
        
        # Wait for the page to be ready (we already waited in fetch, but we can wait more)
        # We'll try to fill the address.
        try:
            # Try to fill the address in the first input we find that looks like an address input
            page.fill('input[type="text"]', address)
        except Exception as e:
            print("Could not fill address input: ", e)
            # Try to find by placeholder
            try:
                page.fill('input[placeholder*="address" i]', address)
            except Exception as e2:
                print("Could not fill by placeholder: ", e2)
                # We'll try to get all inputs and see if we can find one that might be for address
                inputs = page.query_selector_all('input')
                for inp in inputs:
                    placeholder = inp.get_attribute('placeholder') or ''
                    if 'address' in placeholder.lower() or 'property' in placeholder.lower():
                        inp.fill(address)
                        break
                else:
                    print("Could not find address input")
                    return None
        
        # Now, try to click the search button
        try:
            page.click('button:has-text("Search")')
        except Exception as e:
            print("Could not click search button: ", e)
            # Try to find by type submit
            try:
                page.click('input[type="submit"]')
            except Exception as e2:
                print("Could not click submit input: ", e2)
                # Try to find by role button
                try:
                    page.click('role=button[name="Search"]')
                except Exception as e3:
                    print("Could not find search button: ", e3)
                    return None
        
        # Wait for results to load
        time.sleep(5)  # Wait for 5 seconds for results to load
        
        # Now, we expect to see a list of results or a property detail page.
        # Let's get the page content and see if we can find the owner name.
        # We'll look for common patterns: "Owner Name", "Property Owner", etc.
        html = page.html()
        
        # We'll parse the HTML with BeautifulSoup or just use string search for simplicity.
        # Since we are in a controlled environment, we can use string search.
        # But let's try to use the fetcher's parsing capabilities.
        # We can use page.query_selector to get elements.
        
        # Try to find the owner name in the results.
        # We'll look for a table or div that contains the owner information.
        # Common selectors: .owner-name, #owner, etc.
        owner_element = page.query_selector('.owner-name, #owner, [data-label*="owner" i], td:has-text("Owner")')
        if owner_element:
            owner_name = owner_element.text_content().strip()
            print("Found owner name: ", owner_name)
            
            # Also try to get the property ID (if available)
            property_id_element = page.query_selector('.property-id, #property-id, [data-label*="id" i], td:has-text("Property ID")')
            property_id = property_id_element.text_content().strip() if property_id_element else None
            print("Property ID: ", property_id)
            
            return {
                'owner_name': owner_name,
                'property_id': property_id
            }
        else:
            print("Could not find owner name in the results.")
            # Let's save the HTML for debugging
            with open('tcad_search_results.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("Saved HTML to tcad_search_results.html for debugging")
            return None
            
    except Exception as e:
        print("Error during TCAD search: ", e)
        return None
    finally:
        fetcher.close()

def search_tclerk(owner_name, address):
    """
    Search Travis County Clerk's Official Public Records for deeds by owner name and/or address.
    Returns deed information if found.
    """
    url = "https://officialpublicrecords.traviscountytx.gov/"
    fetcher = StealthyFetcher(
        headless=True,
        bypass_csp=True,
        ignore_http_errors=True,
        disable_resources=True,
        timeout=30000,
    )
    try:
        page = fetcher.fetch(url)
        print("Clerk page title:", page.title())
        
        # We'll try to search by owner name first.
        # Look for a search form.
        try:
            # Fill the owner name in the grantor/grantee field
            page.fill('input[name*="grantor" i], input[name*="grantee" i], input[placeholder*="name" i]', owner_name)
        except Exception as e:
            print("Could not fill owner name in clerk search: ", e)
            # Try to find by label
            labels = page.query_selector_all('label')
            for label in labels:
                if 'grantor' in label.text_content().lower() or 'grantee' in label.text_content().lower():
                    # Find the associated input
                    # We'll assume the input is next or we can use the for attribute
                    for_attr = label.get_attribute('for')
                    if for_attr:
                        inp = page.query_selector(f'#{for_attr}')
                        if inp:
                            inp.fill(owner_name)
                            break
            else:
                print("Could not find grantor/grantee input")
                return None
        
        # We might also want to fill the address if available, but let's try with owner name first.
        # Click search
        try:
            page.click('button:has-text("Search"), input[type="submit"]')
        except Exception as e:
            print("Could not click search on clerk site: ", e)
            return None
        
        time.sleep(5)  # Wait for results
        
        # Now, we expect to see a list of documents.
        # We'll look for the most recent deed (likely a Warranty Deed or Deed of Trust).
        # We'll try to find a table of results and then look for a deed.
        # We'll extract the first few results and see if we can get the deed info.
        
        # Let's get the page HTML and look for common deed types.
        html = page.html()
        
        # We'll try to find rows in a table that contain the document type.
        # Common selectors: tr, .result-row, etc.
        rows = page.query_selector_all('tr, .result-row, .search-result')
        for row in rows:
            text = row.text_content().lower()
            if 'deed' in text and ('warranty' in text or 'trust' in text or 'grant' in text):
                # We found a deed row, now extract the details.
                # We'll try to get the document date, type, and maybe a link to the document.
                # We'll look for cells in the row.
                cells = row.query_selector_all('td')
                if len(cells) >= 3:
                    doc_type = cells[0].text_content().strip()
                    doc_date = cells[1].text_content().strip()
                    doc_link = cells[2].query_selector('a')
                    doc_url = doc_link.get_attribute('href') if doc_link else None
                    print("Found deed: ", doc_type, doc_date, doc_url)
                    return {
                        'type': doc_type,
                        'date': doc_date,
                        'url': doc_url
                    }
        
        # If we didn't find in rows, let's save the HTML for debugging.
        with open('tclerk_search_results.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Saved clerk search HTML to tclerk_search_results.html")
        return None
        
    except Exception as e:
        print("Error during TClerk search: ", e)
        return None
    finally:
        fetcher.close()

def main():
    address = "3524 Winding Shore Ln, Pflugerville, TX"
    print(f"Searching for deed information for: {address}")
    
    # Step 1: Search TCAD for owner name
    tcad_result = search_tcad(address)
    if not tcad_result:
        print("Failed to get owner name from TCAD. Trying to search clerk by address directly...")
        # We might try to search the clerk by address, but let's first see if we can get the owner name from TCAD by a different method.
        # For now, we'll exit.
        return
    
    owner_name = tcad_result.get('owner_name')
    property_id = tcad_result.get('property_id')
    print(f"Owner name from TCAD: {owner_name}")
    print(f"Property ID from TCAD: {property_id}")
    
    # Step 2: Search TClerk for deeds by owner name
    clerk_result = search_tclerk(owner_name, address)
    if clerk_result:
        print("Deed found:")
        print(f"  Type: {clerk_result['type']}")
        print(f"  Date: {clerk_result['date']}")
        print(f"  URL: {clerk_result['url']}")
    else:
        print("No deed found in TClerk search by owner name.")
        # We could try to search by address or property ID if we have it.
        if property_id:
            print("Trying to search by property ID...")
            # We would need to implement a search by property ID in the clerk's site.
            # But for now, we'll just note that we didn't find it.
            pass

if __name__ == "__main__":
    main()