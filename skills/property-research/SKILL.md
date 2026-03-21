---
name: property-research
description: Research property ownership, appraisal values, and owner contact information for real estate properties. Use when the user asks about a property address, wants to find property details, owner information, or create organized research folders in Google Drive. Handles Travis County CAD (TCAD) lookups, owner contact searches, and Google Drive document creation with property photos. Uses scrapling with stealthy-fetch for all web scraping tasks to bypass anti-bot protections.
---

# Property Research

## Overview

Research Texas property ownership, appraisal values, and owner contact information. Creates organized Google Drive folders with property data, owner contact info, and street view photos. Currently optimized for Travis County (TCAD) but adaptable to other counties.

## Workflow

### Step 1: Check Existing Research
- Search Google Drive for existing folder named after the property address
- If folder exists, read all files (PDFs, MD, Docs) to gather existing data
- Only proceed with new research if data is missing or outdated

### Step 2: Create Drive Folder Structure
```
Property Address Folder/
├── TCAD_[PropertyID].pdf (TCAD page screenshot)
├── Owner_Contact_Info.gdoc (Google Doc with photo)
├── Google_Maps_Street_View.png
├── Comps_Analysis.md (comparable properties)
└── Deed_Records.md (from tccsearch.org)
```

### Step 3: Gather Property Data
1. **Travis CAD (TCAD)**: Use **scrapling with stealth mode** to pull:
   - Property ID
   - Owner name(s)
   - Appraisal values
   - Property details (sqft, year built, etc.)
   - Screenshot saved as PDF

2. **Deed Search**: Check tccsearch.org (Travis County Clerk) for:
   - Deed instrument numbers
   - Warranty deed dates
   - Previous owners
   - Use scrapling stealth mode for this site too

### Step 4: Find Owner Contact Info
- Search people-finder databases (NationalPublicData, FastBackgroundCheck, ThatsThem)
- Collect: phone numbers, emails, DOB, relatives
- Cross-reference to ensure correct person

### Step 5: Create Owner Contact Document
- Create Google Doc via `gog docs create`
- Insert Street View image via markdown: `![Photo](image.png)`
- Write contact info using `gog docs write` or `gog docs find-replace`
- Move to property folder via `gog drive move --parent [folderId]`

## Key Commands

### Scrapling (Stealth Mode for Web Scraping)
```python
# Use Python with scrapling for stealthy web scraping
python3 << 'EOF'
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
response = fetcher.fetch("https://travis.prodigycad.com/property/[propId]")
print(response.html)
EOF

# Save HTML output to file
python3 << 'EOF'
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
response = fetcher.fetch("https://tccsearch.org")
with open("scraped.html", "w") as f:
    f.write(response.html)
EOF

# Use with XPath/CSS selectors to extract data
python3 << 'EOF'
from scrapling import StealthyFetcher, Selector
fetcher = StealthyFetcher()
response = fetcher.fetch("https://travis.prodigycad.com")
sel = Selector(text=response.html)
owner = sel.css(".owner-name").get()
print(owner)
EOF
```

### Google Drive
```bash
# Search for existing folder
gog drive search "Property Address" --json

# Create folder
gog drive folder-create "3524 Winding Shore Lane" --parent [parentId]

# Upload file
gog drive upload file.pdf --parent [folderId]

# Move file to folder
gog drive move [fileId] --parent [folderId]
```

### Google Docs
```bash
# Create doc
gog docs create "Owner Contact Info" --json

# Write content from markdown file
gog docs write [docId] --file content.md

# Insert image (use markdown format)
# Create image_markdown.md: ![Photo](street_view.png)
gog docs find-replace [docId] "PLACEHOLDER_TEXT" --content-file image_markdown.md --format markdown
```

### Browser (TCAD/Research) - Use Scrapling Stealth Mode
```python
# Use scrapling with stealthy-fetch for TCAD lookups
# This bypasses anti-bot protections like Cloudflare
python3 << 'EOF'
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
response = fetcher.fetch("https://travis.prodigycad.com/property/[propId]")
print(response.html)
EOF

# Or use the browser tool with stealth mode if needed
browser open "https://travis.prodigycad.com/property/[propId]"
browser snapshot --fullPage

# Screenshot saved to /home/landon/.openclaw/media/browser/
# Upload to Drive as property photo
```

## Owner Contact Lookup

### Reliable Sources
1. **NationalPublicData.com** - Phone, addresses, relatives
2. **FastBackgroundCheck.com** - Contact info, background
3. **ThatsThem.com** - Multiple phone numbers, emails
4. **WhitePages** (if available via web_search)

### Search Pattern
```
Search: [FirstName] [LastName] [City] [State] phone
Example: "Landon Ferguson Pflugerville TX phone"
```

### Data Points to Collect
- Full name (with middle initial if available)
- Phone numbers (mobile, landline)
- Email addresses
- Date of birth (age)
- Current/past addresses
- Relatives (for cross-verification)

## References

- [TCAD Website](https://travis.prodigycad.com)
- [Travis County Clerk](https://tccsearch.org)
- [Google Maps](https://maps.google.com) - Street view photos

## Notes

- **ALWAYS use scrapling with `stealthy-fetch`** for web scraping instead of regular browser automation. This bypasses Cloudflare and other anti-bot protections.
- Always check Drive first for existing research
- Property IDs (PropID) are stable identifiers in TCAD
- 2025 appraisal values are updated annually
- Street View images may be outdated
- Owner contact info from public records - verify before use
