#!/usr/bin/env python3
"""
Fetch LUNCH menu from SchoolDish for PfISD schools.
Usage: python3 get_lunch.py [school_slug] [YYYY-MM-DD or "tomorrow"]
"""

import sys
import json
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright


def fetch_lunch_menu(school_slug="rowelaneelementaryschool", date_str=None):
    """
    Fetch lunch menu for a PfISD school from SchoolDish.
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    target_day = str(target_date.day)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Navigate to the school menu page
            url = f"https://pflugerville.schooldish.com/en/schoolmenus/{school_slug}/"
            page.goto(url, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            # Dismiss cookie consent dialog if present
            try:
                accept_btn = page.locator('#onetrust-accept-btn-handler').first
                if accept_btn.count() > 0:
                    accept_btn.click()
                    page.wait_for_timeout(500)
            except:
                pass
            
            # Try to remove the cookie overlay entirely
            try:
                page.evaluate("""() => {
                    const overlay = document.querySelector('#onetrust-consent-sdk');
                    if (overlay) overlay.remove();
                }""")
            except:
                pass
            
            # Click Change button
            print("Opening date selector...", file=sys.stderr)
            try:
                change_btn = page.locator('button.DateMealFilterButton').first
                if change_btn.count() > 0:
                    change_btn.click(force=True)
                else:
                    # Fallback to text search
                    change_btn = page.get_by_text("Change").first
                    if change_btn.count() > 0:
                        change_btn.click()
                page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Change button issue: {e}", file=sys.stderr)
            
            # Click the Today button to open calendar
            print("Opening calendar...", file=sys.stderr)
            try:
                # Find button that contains "Today" text
                today_btns = page.locator('button').all()
                for btn in today_btns:
                    try:
                        text = btn.text_content()
                        if text and "Today" in text:
                            btn.click(force=True)
                            break
                    except:
                        continue
                page.wait_for_timeout(1500)
            except Exception as e:
                print(f"Today button issue: {e}", file=sys.stderr)
            
            # Select the date
            print(f"Selecting day {target_day}...", file=sys.stderr)
            try:
                # Try to find the date option in the calendar
                date_options = page.locator('[role="option"]').all()
                for opt in date_options:
                    try:
                        if opt.text_content().strip() == target_day:
                            opt.click(force=True)
                            break
                    except:
                        continue
                page.wait_for_timeout(1000)
            except Exception as e:
                print(f"Date selection issue: {e}", file=sys.stderr)
            
            # Switch from Breakfast to Lunch in the MEAL dropdown
            print("Switching to Lunch...", file=sys.stderr)
            try:
                # The MEAL field is a react-select dropdown
                # First, click on the meal dropdown to open it
                meal_dropdown = page.locator('#aria-meal-input').first
                if meal_dropdown.count() > 0:
                    # Click the dropdown container to open options
                    dropdown_container = page.locator('[id="aria-meal-input"]').locator('xpath=../..').first
                    dropdown_container.click()
                    page.wait_for_timeout(1000)
                    
                    # Look for "Lunch" option in the dropdown
                    lunch_option = page.get_by_text("Lunch", exact=True).first
                    if lunch_option.count() > 0:
                        lunch_option.click(force=True)
                        print("Selected Lunch from dropdown", file=sys.stderr)
                        page.wait_for_timeout(1000)
                    else:
                        # Try searching for it
                        meal_dropdown.fill("Lunch")
                        page.wait_for_timeout(500)
                        lunch_option = page.get_by_text("Lunch", exact=True).first
                        if lunch_option.count() > 0:
                            lunch_option.click(force=True)
                            page.wait_for_timeout(1000)
                else:
                    print("Meal dropdown not found", file=sys.stderr)
            except Exception as e:
                print(f"Meal switch issue: {e}", file=sys.stderr)
            
            # Click Done button
            print("Clicking Done...", file=sys.stderr)
            try:
                done_btn = page.get_by_text("Done", exact=True).first
                if done_btn.count() > 0:
                    done_btn.click(force=True)
                page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Done button issue: {e}", file=sys.stderr)
            
            # Extract menu items
            menu_items = []
            
            # Get all sections (h2 headers)
            sections = page.locator('h2').all()
            
            for section in sections:
                section_title = section.text_content().strip()
                # Common section names
                if section_title in ['Entree', 'Vegetable', 'Vegetables', 'Fruit', 'Fruits', 'Grain', 'Grains', 'Milk', 'Beverage', 'Side', 'Pre-K', 'Deli', 'Field Trip/Sack Lunch', 'Condiments', 'Daily Serve Entree']:
                    try:
                        # Navigate up and then to sibling list
                        parent = section.locator('xpath=..')
                        # The next sibling should contain the food items
                        next_sibling = parent.locator('xpath=following-sibling::*[1]')
                        if next_sibling.count() > 0:
                            food_items = next_sibling.locator('h3').all()
                            for item in food_items:
                                food_name = item.text_content().strip()
                                if food_name and len(food_name) > 2:
                                    menu_items.append(f"{section_title}: {food_name}")
                    except:
                        pass
            
            # Fallback: get all h3 elements
            if not menu_items:
                h3_elements = page.locator('h3').all()
                for h3 in h3_elements:
                    text = h3.text_content().strip()
                    if text and len(text) > 2 and 'Meal Calculator' not in text:
                        menu_items.append(text)
            
            browser.close()
            
            if menu_items:
                return {
                    "success": True,
                    "school": school_slug,
                    "date": date_str,
                    "menu_type": "Lunch",
                    "menu_items": menu_items
                }
            else:
                return {
                    "success": False,
                    "error": f"No menu items found for {date_str}",
                    "school": school_slug,
                    "date": date_str,
                    "direct_link": url
                }
                
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "school": school_slug,
            "date": date_str
        }


def get_next_school_day(date_str):
    """
    Get the next school day (skips weekends, but not holidays).
    Returns the date string of the next school day.
    """
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date_obj.weekday()  # 0=Monday, 6=Sunday
    
    # If it's Saturday (5), next school day is Monday
    if weekday == 5:
        next_day = date_obj + timedelta(days=2)
        return next_day.strftime("%Y-%m-%d")
    # If it's Sunday (6), next school day is tomorrow (Monday)
    elif weekday == 6:
        next_day = date_obj + timedelta(days=1)
        return next_day.strftime("%Y-%m-%d")
    else:
        # It's a weekday, just return the same date
        return date_str


def is_weekend(date_str):
    """Check if the given date is a weekend."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.weekday() >= 5  # Saturday=5, Sunday=6


def main():
    school = sys.argv[1] if len(sys.argv) > 1 else "rowelaneelementaryschool"
    date_str = sys.argv[2] if len(sys.argv) > 2 else None
    skip_weekends = sys.argv[3] if len(sys.argv) > 3 else "false"
    
    # If no date specified, use today
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # If user types "tomorrow", calculate tomorrow's date
    if date_str == "tomorrow":
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%Y-%m-%d")
        print(f"Fetching menu for tomorrow: {date_str}", file=sys.stderr)
    
    # Handle weekend skipping mode
    if skip_weekends.lower() == "true" or skip_weekends.lower() == "skip":
        original_date = date_str
        date_str = get_next_school_day(date_str)
        if original_date != date_str:
            print(f"Weekend detected ({original_date}), fetching next school day instead: {date_str}", file=sys.stderr)
    
    result = fetch_lunch_menu(school, date_str)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
