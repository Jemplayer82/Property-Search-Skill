#!/usr/bin/env python3
"""
Debug the Change button and Lunch selector on SchoolDish - take screenshots.
"""

from playwright.sync_api import sync_playwright


def debug_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for debugging
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # Navigate to the school menu page
        url = "https://pflugerville.schooldish.com/en/schoolmenus/rowelaneelementaryschool/"
        page.goto(url, wait_until='networkidle')
        page.wait_for_timeout(3000)
        
        print("=== Screenshot before clicking Change ===")
        page.screenshot(path='/home/landon/.openclaw/workspace/before_change.png')
        
        # Look for the Change button
        change_btn = page.locator('button:has-text("Change")').first
        if change_btn.count() > 0:
            print("Found Change button, clicking...")
            change_btn.click()
            page.wait_for_timeout(3000)
            
            print("=== Screenshot after clicking Change ===")
            page.screenshot(path='/home/landon/.openclaw/workspace/after_change.png')
            
            # Look at the dialog/modal that appeared
            dialog = page.locator('[role="dialog"], .modal, .popup, [class*="dialog"]').first
            if dialog.count() > 0:
                print("\nFound dialog/modal")
                dialog_html = dialog.evaluate('el => el.outerHTML')
                print(f"Dialog HTML:\n{dialog_html[:2000]}")
                
                # Save screenshot of dialog
                dialog.screenshot(path='/home/landon/.openclaw/workspace/dialog.png')
            else:
                print("\nNo dialog found")
        
        print("\nScreenshots saved:")
        print("  - before_change.png")
        print("  - after_change.png")  
        print("  - dialog.png")
        
        browser.close()


if __name__ == "__main__":
    debug_menu()
