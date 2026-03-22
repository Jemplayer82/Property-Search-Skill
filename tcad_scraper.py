from scrapling.fetchers import StealthyFetcher
from bs4 import BeautifulSoup
import time

# URL of the TCAD property search
url = 'https://traviscad.org/propertysearch'

print("Fetching the property search page...")
# Use StealthyFetcher to get the page with JavaScript rendering
response = StealthyFetcher.fetch(
    url=url,
    headless=True,
    block_images=True,
    wait_for_networkidle=True,
    delay=3,
    wait_timeout=10000
)

print(f"Status code: {response.status_code}")
if response.status_code != 200:
    print("Failed to fetch the page.")
    exit(1)

# Parse the initial page to see the form
soup = BeautifulSoup(response.text, 'html.parser')
print("Page title:", soup.title.string if soup.title else "No title")

# Look for the search input field
# Based on earlier inspection, the input might have placeholder "Search..."
search_input = soup.find('input', {'placeholder': 'Search...'})
if not search_input:
    # Try to find any input of type text or search
    search_input = soup.find('input', {'type': ['text', 'search']})
if not search_input:
    # Try to find by name or id
    search_input = soup.find('input', {'name': lambda x: x and 'search' in x.lower()})
if not search_input:
    # As a last resort, find all inputs and print them for debugging
    inputs = soup.find_all('input')
    print("Found inputs:")
    for inp in inputs:
        print(f"  - {inp}")
    exit(1)

print(f"Found search input: {search_input}")

# Now we need to interact with the page to fill the form and submit.
# Since StealthyFetcher is for static fetching, we need to use the Playwright-like interface.
# Actually, scrapling's StealthyFetcher returns a response object that we can use for further interaction?
# Looking at the scrapling documentation, we might need to use the Spider or the async interface.

# Let's try a different approach: use the StealthyFetcher to get the page, then simulate the form submission
# by extracting the form details and making a POST request.

# Find the form containing the search input
form = search_input.find_parent('form')
if not form:
    print("Could not find a form containing the search input.")
    exit(1)

print("Found form.")

# Extract form details
action = form.get('action', url)
method = form.get('method', 'get').lower()
print(f"Form action: {action}, method: {method}")

# Build the form data
form_data = {}
for inp in form.find_all('input'):
    name = inp.get('name')
    if not name:
        continue
    value = inp.get('value', '')
    # If it's a text or search input, we want to override with our search term
    if inp.get('type') in ['text', 'search', None]:
        value = '3424 Winding Shore Lane, Pflugerville, TX 78660'
    form_data[name] = value
    print(f"Form field: {name} = {value}")

# Also include textarea and select if needed
for textarea in form.find_all('textarea'):
    name = textarea.get('name')
    if name:
        form_data[name] = textarea.get_text()
        print(f"Textarea: {name} = {form_data[name]}")

for select in form.find_all('select'):
    name = select.get('name')
    if name:
        # Get the selected option
        selected = select.find('option', selected=True)
        if selected:
            form_data[name] = selected.get('value', selected.get_text())
        else:
            # Default to first option
            first = select.find('option')
            if first:
                form_data[name] = first.get('value', first.get_text())
        print(f"Select: {name} = {form_data[name]}")

print(f"Form data to submit: {form_data}")

# Make the request to submit the form
print("Submitting the form...")
session_response = StealthyFetcher.fetch(
    url=action,
    method=method.upper(),
    data=form_data if method == 'post' else None,
    params=form_data if method == 'get' else None,
    headless=True,
    block_images=True,
    wait_for_networkidle=True,
    delay=3,
    wait_timeout=15000
)

print(f"Response status after form submission: {session_response.status_code}")
if session_response.status_code != 200:
    print("Failed to submit the form.")
    exit(1)

# Save the response for debugging
with open('/home/landon/.openclaw/workspace/tcad_results.html', 'w') as f:
    f.write(session_response.text)
print("Saved results to tcad_results.html")

# Parse the results page to find owner information
results_soup = BeautifulSoup(session_response.text, 'html.parser')

# Look for common patterns of owner name
# Often, owner name is in a table or a div with labels like "Owner Name", "Property Owner", etc.
owner_keywords = ['owner', 'property owner', 'owner name', 'owned by']
owner_info = []

# Search through all text
text = results_soup.get_text()
lines = [line.strip() for line in text.split('\n') if line.strip()]
for i, line in enumerate(lines):
    line_lower = line.lower()
    for keyword in owner_keywords:
        if keyword in line_lower:
            print(f"Found potential owner info at line {i}: {line}")
            # Capture this line and the next few lines
            for j in range(i, min(i+5, len(lines))):
                owner_info.append(lines[j])
            break

if owner_info:
    print("\nPossible owner information:")
    for info in owner_info:
        print(info)
else:
    print("Could not find owner information by keyword search.")
    # Try to find tables
    tables = results_soup.find_all('table')
    print(f"Found {len(tables)} tables in the results.")
    for idx, table in enumerate(tables):
        # Check if the table contains owner-related text
        if any(keyword in table.get_text().lower() for keyword in owner_keywords):
            print(f"Table {idx} might contain owner info:")
            print(table.get_text()[:500])
            # Try to extract rows
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                cols_text = [col.get_text(strip=True) for col in cols]
                if any('owner' in col.lower() for col in cols_text):
                    print(f"  Row: {cols_text}")

# If still not found, let's look for any mention of a name that looks like a person's name
# This is a heuristic: look for patterns like two words capitalized, possibly with a comma
import re
# Look for patterns like "Last, First" or "First Last"
name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)?)\b'
potential_names = re.findall(name_pattern, text)
if potential_names:
    print(f"\nFound {len(set(potential_names))} potential names (first 10):")
    for name in list(set(potential_names))[:10]:
        print(f"  {name}")

# Let's also check if there's a direct link to the property details that we might need to follow
# Sometimes the search results show a list of properties and you need to click on the address
# Look for links that contain the address or property ID
links = results_soup.find_all('a', href=True)
for link in links:
    href = link['href']
    text = link.get_text(strip=True)
    if '3424' in text or 'Winding' in text or 'Shore' in text:
        print(f"Found link with address snippet: {text} -> {href}")
        # We could follow this link, but let's first see if we have the owner info already.

print("\nDone.")