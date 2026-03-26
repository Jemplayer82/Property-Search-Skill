#!/usr/bin/env python3
"""
Fetch today's lunch menu from Nutrislice for PfISD schools.
Uses browser automation to click through the landing page.
"""

import sys
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright


def fetch_lunch_menu(school_slug="rowe-lane-elementary", date=None):
    """
    Fetch lunch menu for a PfISD school.
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    try:
        with sync_playwright() as p:
            # Launch browser with stealth settings
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            )
            
            page = context.new_page()
            
            # Navigate to the menu URL
            menu_url = f"https://pfisd.nutrislice.com/menu/{school_slug}/lunch/{date}"
            page.goto(menu_url, wait_until='networkidle')
            
            # Wait a bit for any dynamic content
            page.wait_for_timeout(2000)
            
            # Check if we're on the landing page with "View Menus" button
            view_menus_button = page.locator('button:has-text("View Menus")')
            
            if view_menus_button.count() > 0:
                print("Found View Menus button, clicking...", file=sys.stderr)
                view_menus_button.click()
                page.wait_for_timeout(3000)  # Wait for menu to load
            
            # Now try to extract menu items
            items_found = []
            
            # Try various selectors
            selectors = [
                '.menu-item .name',
                '.menu-item-name',
                '.food-name',
                '.meal-item .name',
                '[data-menu-item] .name',
                '.cafe-item-name',
                '.menu-item-title',
                '.item-name',
                '.food-item',
                '.menu-item',
            ]
            
            for selector in selectors:
                elements = page.locator(selector).all()
                for elem in elements:
                    text = elem.text_content().strip()
                    if text and len(text) > 2 and len(text) < 100:
                        # Filter out navigation
                        if not any(x in text.lower() for x in [
                            "welcome", "terms", "privacy", "powered", "menu",
                            "back", "next", "home", "about", "contact", "view"
                        ]):
                            items_found.append(text)
            
            # Try extracting from script tags
            scripts = page.locator('script').all()
            for script in scripts:
                script_text = script.text_content() or ''
                if 'menu' in script_text.lower() or '__INITIAL_STATE__' in script_text:
                    json_matches = re.findall(r'window\.__[A-Z_]+__\s*=\s*(\{.*?\});', script_text, re.DOTALL)
                    for json_str in json_matches:
                        try:
                            data = json.loads(json_str)
                            json_items = extract_from_json(data, date)
                            items_found.extend(json_items)
                        except:
                            pass
            
            browser.close()
            
            # Remove duplicates
            seen = set()
            unique_items = []
            for item in items_found:
                item_clean = item.strip()
                if item_clean.lower() not in seen and len(item_clean) > 2:
                    seen.add(item_clean.lower())
                    unique_items.append(item_clean)
            
            if unique_items:
                return {
                    "success": True,
                    "school": school_slug,
                    "date": date,
                    "menu_items": unique_items[:20]
                }
            else:
                return {
                    "success": False,
                    "error": "Could not extract menu items",
                    "school": school_slug,
                    "date": date,
                    "note": "Tried clicking through landing page but no menu items found",
                    "direct_link": f"https://pfisd.nutrislice.com/menu/{school_slug}/lunch/{date}"
                }
                
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "school": school_slug,
            "date": date,
            "direct_link": f"https://pfisd.nutrislice.com/menu/{school_slug}/lunch/{date}"
        }


def extract_from_json(data, target_date):
    """Extract menu items from JSON data."""
    items = []
    if not isinstance(data, dict):
        return items

    for key in ["menu", "menus", "items", "foods", "meals", "lunch", "menuItems"]:
        if key in data:
            menu_data = data[key]
            if isinstance(menu_data, list):
                for item in menu_data:
                    if isinstance(item, dict):
                        name = item.get("name") or item.get("title") or item.get("itemName") or item.get("food", {}).get("name")
                        if name:
                            items.append(name)
            elif isinstance(menu_data, dict):
                for date_key in [target_date, target_date.replace("-", "")]:
                    if date_key in menu_data:
                        day_data = menu_data[date_key]
                        if isinstance(day_data, list):
                            for item in day_data:
                                if isinstance(item, dict):
                                    name = item.get("name") or item.get("title")
                                    if name:
                                        items.append(name)

    if "weeks" in data:
        for week in data["weeks"]:
            if "days" in week:
                for day in week["days"]:
                    day_date = day.get("date", "")
                    if target_date in str(day_date):
                        for key in ["menu_items", "items", "foods"]:
                            if key in day:
                                for item in day[key]:
                                    if isinstance(item, dict):
                                        name = item.get("name") or item.get("food", {}).get("name")
                                        if name:
                                            items.append(name)

    return items


def main():
    school = sys.argv[1] if len(sys.argv) > 1 else "rowe-lane-elementary"
    date = sys.argv[2] if len(sys.argv) > 2 else None

    result = fetch_lunch_menu(school, date)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
