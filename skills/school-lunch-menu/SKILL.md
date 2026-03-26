---
name: school-lunch-menu
description: Fetch school lunch menus from SchoolDish for Pflugerville ISD (PfISD) schools. Use when the user asks about what lunch is being served at Rowe Lane Elementary or any other PfISD school, wants to check today's or tomorrow's cafeteria menu, or needs to know what food is available for school meals. Supports viewing menus for specific dates. Supports all PfISD schools through the SchoolDish platform.
---

# School Lunch Menu Skill

Fetch lunch menus from SchoolDish for PfISD schools. Supports today's menu, tomorrow's menu, or any specific date.

## Important Note

**Lunch vs Breakfast:** The SchoolDish page defaults to showing **breakfast** early in the day. The script attempts to switch to lunch, but if the lunch menu hasn't been posted yet, it will show breakfast items. This is normal — lunch menus are typically posted later in the morning.

## Supported Schools

All Pflugerville ISD schools on SchoolDish:

- **Rowe Lane Elementary:** `rowelaneelementaryschool`
- Other schools: Find the slug from the SchoolDish URL (e.g., `https://pflugerville.schooldish.com/en/schoolmenus/{SCHOOL-SLUG}/`)

## Usage

### Fetch Today's Menu

```bash
python3 scripts/get_lunch.py [school-slug]
```

Examples:
```bash
# Rowe Lane Elementary
python3 scripts/get_lunch.py rowelaneelementaryschool
```

### Fetch Tomorrow's Menu

```bash
python3 scripts/get_lunch.py [school-slug] tomorrow
```

Example:
```bash
python3 scripts/get_lunch.py rowelaneelementaryschool tomorrow
```

### Fetch Menu for a Specific Date

```bash
python3 scripts/get_lunch.py [school-slug] YYYY-MM-DD
```

Example:
```bash
python3 scripts/get_lunch.py rowelaneelementaryschool 2026-03-30
```

### Python API

```python
from scripts.get_lunch import fetch_lunch_menu
from datetime import datetime, timedelta

# Today's menu
result = fetch_lunch_menu("rowelaneelementaryschool")

# Tomorrow's menu
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
result = fetch_lunch_menu("rowelaneelementaryschool", tomorrow)

# Specific date
result = fetch_lunch_menu("rowelaneelementaryschool", "2026-03-30")

if result["success"]:
    print(f"Menu for {result['date']}:")
    for item in result["menu_items"]:
        print(f"- {item}")
```

## Output Format

```json
{
  "success": true,
  "school": "rowelaneelementaryschool",
  "date": "2026-03-27",
  "menu_type": "Lunch",
  "menu_items": [
    "Entree: Cheese Pizza",
    "Entree: Pepperoni Pizza",
    "Entree: BBQ Pork Riblet Sandwich",
    "Deli: Turkey & Cheese Sub",
    "Fruit: Fresh Apple Wedges",
    "Fruit: Apricot Halves",
    "Milk: 1% Milk",
    "Vegetable: Fresh Cucumber Slices"
  ]
}
```

## Direct Links

Users can also view menus directly at:
- SchoolDish: `https://pflugerville.schooldish.com/en/schoolmenus/{school-slug}/`
- Nutrislice (requires manual "View Menus" click): `https://pfisd.nutrislice.com/menu/{school-slug}/lunch`

## Menu Categories

Typical menu sections:
- **Entree** - Main dish
- **Vegetable** / **Vegetables** - Veggie sides
- **Fruit** / **Fruits** - Fruit options
- **Grain** / **Grains** - Bread, rice, pasta
- **Milk** / **Beverage** - Drinks
- **Side** - Additional sides
- **Pre-K** - Pre-Kindergarten specific items

## Technical Details

- Uses Playwright to navigate SchoolDish website
- Supports date selection via calendar picker
- Attempts to switch from breakfast to lunch via UI interaction
- Falls back to showing available menu if lunch isn't posted yet
- Filters out breakfast-specific items (cereal, bacon, eggs, etc.) when possible
- Supports all PfISD schools that use SchoolDish platform
