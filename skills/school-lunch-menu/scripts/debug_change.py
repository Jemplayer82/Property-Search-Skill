#!/usr/bin/env python3
"""
Debug the Change button and Lunch selector on SchoolDish.
"""

from playwright.sync_api import sync_playwright


def debug_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # Navigate to the school menu page
        url = "https://pflugerville.schooldish.com/en/schoolmenus/rowelaneelementaryschool/"
        page.goto(url, wait_until='networkidle')
        page.wait_for_timeout(3000)
        
        print("=== Before clicking Change ===")
        print(f"URL: {page.url}")
        
        # Get the page HTML around the meal selector
        html = page.content()
        
        # Look for the Change button and surrounding context
        change_btn = page.locator('button:has-text("Change")').first
        if change_btn.count() > 0:
            print("\nFound Change button")
            
            # Get the parent container
            parent_html = change_btn.locator('xpath=..').evaluate('el => el.outerHTML')
            print(f"\nParent HTML:\n{parent_html[:500]}")
            
            # Click the button
            print("\n=== Clicking Change button ===")
            change_btn.click()
            page.wait_for_timeout(3000)
            
            print(f"\n=== After clicking Change ===")
            print(f"URL: {page.url}")
            
            # Look for any new elements that appeared
            # Check for dropdowns, modals, or radio buttons
            all_buttons = page.locator('button').all()
            print(f"\nAll buttons on page ({len(all_buttons)}):")
            for i, btn in enumerate(all_buttons[:15]):
                text = btn.text_content().strip()
                if text:
                    print(f"  {i}: '{text[:50]}'")
            
            # Look for Lunch specifically
            print("\n=== Looking for Lunch elements ===")
            lunch_elements = page.locator('*:has-text("Lunch")').all()
            print(f"Found {len(lunch_elements)} elements containing 'Lunch':")
            for i, elem in enumerate(lunch_elements[:10]):
                try:
                    tag = elem.evaluate('el => el.tagName')
                    text = elem.text_content().strip()[:100]
                    print(f"  {i}: <{tag}> '{text}'")
                except:
                    print(f"  {i}: (could not get info)")
            
            # Try to find radio buttons or checkboxes
            inputs = page.locator('input[type="radio"], input[type="checkbox"]').all()
            print(f"\n=== Found {len(inputs)} radio/checkbox inputs ===")
            for inp in inputs[:10]:
                try:
                    input_type = inp.get_attribute('type')
                    input_id = inp.get_attribute('id')
                    input_name = inp.get_attribute('name')
                    input_value = inp.get_attribute('value')
                    is_checked = inp.is_checked()
                    print(f"  type={input_type}, id={input_id}, name={input_name}, value={input_value}, checked={is_checked}")
                except:
                    pass
        
        browser.close()


if __name__ == "__main__":
    debug_menu()
