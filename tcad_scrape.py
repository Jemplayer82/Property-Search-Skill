import requests
from bs4 import BeautifulSoup
import urllib.parse

# Try to access the TCAD property search
url = 'https://traviscad.org/propertysearch'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    # First, get the page to see if there are any tokens or cookies needed
    session = requests.Session()
    response = session.get(url, headers=headers, timeout=10)
    print(f'Initial page status: {response.status_code}')
    
    # Parse the form
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form')
    if form:
        print('Form found')
        # Look for input fields
        inputs = form.find_all('input')
        for inp in inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            print(f'  Input: {name} = {value}')
        
        # Prepare search data
        search_data = {}
        for inp in inputs:
            name = inp.get('name')
            if name:
                # If it's a text input, we'll put our search term
                if inp.get('type') in ['text', 'search', None]:
                    search_data[name] = '3424 Winding Shore Lane, Pflugerville, TX 78660'
                else:
                    search_data[name] = value
        
        print(f'Search data: {search_data}')
        
        # Submit the form
        action = form.get('action', url)
        if not action.startswith('http'):
            action = urllib.parse.urljoin(url, action)
        
        print(f'Submitting to: {action}')
        
        # Try POST
        response = session.post(action, data=search_data, headers=headers, timeout=10)
        print(f'Response status: {response.status_code}')
        print(f'Response length: {len(response.text)}')
        
        # Save response for debugging
        with open('/home/landon/.openclaw/workspace/tcad_response.html', 'w') as f:
            f.write(response.text)
        print('Saved response to tcad_response.html')
        
        # Parse the response for owner information
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for common patterns of owner name
        text = soup.get_text()
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if 'owner' in line.lower() and i < len(lines)-1:
                print(f'Found owner context: {line}')
                # Print next few lines
                for j in range(i+1, min(i+4, len(lines))):
                    print(f'  {lines[j].strip()}')
        
        # Alternatively, look for a table with property details
        tables = soup.find_all('table')
        print(f'Found {len(tables)} tables')
        for i, table in enumerate(tables):
            # Check if this table contains owner information
            table_text = table.get_text().lower()
            if 'owner' in table_text:
                print(f'Table {i} might contain owner info:')
                print(table.get_text()[:500])
                
    else:
        print('No form found on page')
        # Save the page for inspection
        with open('/home/landon/.openclaw/workspace/tcad_page.html', 'w') as f:
            f.write(response.text)
        print('Saved page to tcad_page.html')
        
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()