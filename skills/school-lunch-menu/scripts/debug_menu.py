#!/usr/bin/env python3
"""
Debug script to see what Nutrislice looks like after clicking View Menus.
"""

import sys
import json
from datetime import datetime
from playwright.sync_api import sync_playwright


def debug_menu(school_slug="rowe-lane-elementary", date=None):
    """Debug the menu page to see what we're dealing with."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            menu_url = f"https://pfisd.nutrislice.com/menu/{school_slug}/lunch/{date}"
            page.goto(menu_url, wait_until='networkidle')
            page.wait_for_timeout(2000)
            
            # Check if we're on the landing page
            view_menus_button = page.locator('button:has-text("View Menus")')
            
            if view_menus_button.count() > 0:
                print("Found View Menus button, clicking...", file=sys.stderr)
                view_menus_button.click()
                page.wait_for_timeout(5000)  # Wait longer for menu
            
            # Save screenshot
            screenshot_path = f"/home/landon/.openclaw/workspace/nutrislice_debug.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to: {screenshot_path}", file=sys.stderr)
            
            # Print page HTML
            html = page.content()
            print(f"\n--- HTML length: {len(html)} chars ---", file=sys.stderr)
            print(f"--- First 3000 chars ---\n{html[:3000]}", file=sys.stderr)
            
            # Try to find all text content
            all_text = page.locator('body').text_content()
            print(f"\n--- Page text (first 2000 chars) ---\n{all_text[:2000]}", file=sys.stderr)
            
            # Look for any elements with 'menu' or 'food' in class/name
            all_elements = page.locator('[class*="menu"], [class*="food"], [class*="meal"], [class*="item"]').all()
            print(f"\n--- Found {len(all_elements)} potential menu elements ---", file=sys.stderr)
            for i, elem in enumerate(all_elements[:20]):
                text = elem.text_content().strip()[:100]
                class_attr = elem.get_attribute('class') or ''
                print(f"  {i}: class='{class_attr[:50]}' text='{text}'", file=sys.stderr)
            
            browser.close()
            
            return {
                "success": True,
                "screenshot": screenshot_path,
                "html_length": len(html)
            }
                
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


if __name__ == "__main__":
    school = sys.argv[1] if len(sys.argv) > 1 else "rowe-lane-elementary"
    result = debug_menu(school)
    print(json.dumps(result, indent=2))
