---
name: property-research
description: Research property ownership, appraisal values, and owner contact information for real estate properties. Use when the user asks about a property address, wants to find property details, owner information, or create organized research folders in Google Drive. Handles Travis County CAD (TCAD) lookups, owner contact searches, comps analysis, and Google Drive document creation with property photos. Uses browser automation for React-powered sites like TCAD, and scrapling with stealthy-fetch for simpler sites with anti-bot protection. MUST follow comps selection guidelines: location (0.5-1 mile radius), time frame (3-6 months), size (within 20% of GLA), age/style (same era/design), condition, and uniformity (3-5 similar properties).
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
1. **Travis CAD (TCAD)**: Use browser automation via OpenClaw's `browser` tool to pull data from the React-powered site:
   - Property ID
   - Owner name(s)
   - Appraisal values
   - Property details (sqft, year built, etc.)
   - Screenshot saved as PDF

2. **Deed Search**: Check tccsearch.org (Travis County Clerk) for:
   - Deed instrument numbers
   - Warranty deed dates
   - Previous owners
   - May need browser automation for JavaScript-heavy interactions

### Step 4: Find Owner Contact Info
- Search people-finder databases (NationalPublicData, FastBackgroundCheck, ThatsThem)
- Collect: phone numbers, emails, DOB, relatives
- Cross-reference to ensure correct person

### Step 5: Find Comps (Comparables) - MUST FOLLOW THESE RULES
1. **Location**: Homes within same neighborhood, typically 0.5-1 mile radius. Avoid major barriers (highways, rivers).
2. **Time Frame**: Use sales from last 3-6 months (ideally 90 days) to reflect current market.
3. **Size (GLA)**: Comps must be within 20% of subject property's square footage.
4. **Age/Style**: Select homes built within same era with similar design (e.g., ranch vs. two-story).
5. **Condition**: Factor in renovations, upgrades, and maintenance levels when evaluating value.
6. **Status**: Prefer closed sales, but active/pending listings can show current competition.
7. **Uniformity**: Aim for 3-5 similar properties for a strong value range.
8. **Weighting**: Closer sales in time and distance are weighted more heavily.
9. **Adjustments**: Make value adjustments for differences (e.g., garage, square footage, condition).

### Step 6: Create Owner Contact Document
- Create Google Doc via `gog docs create`
- Insert Street View image via markdown: `![Photo](image.png)`
- Write contact info using `gog docs write` or `gog docs find-replace`
- Move to property folder via `gog drive move --parent [folderId]`

### Key Guidelines for Selecting Comps

| Guideline | Rule |
|-----------|------|
| **Location** | Same neighborhood, 0.5-1 mile radius. Avoid highways, rivers. |
| **Time Frame** | Last 3-6 months (ideally 90 days) for current market. |
| **Size (GLA)** | Within 20% of subject property's square footage. |
| **Age/Style** | Same era and design (e.g., ranch vs. two-story). |
| **Condition** | Factor in renovations, upgrades, maintenance. |
| **Status** | Prefer closed sales; active/pending show competition. |
| **Uniformity** | Aim for 3-5 similar properties. |
| **Weighting** | Closer sales in time/distance weighted more heavily. |
| **Adjustments** | Make value adjustments for differences (garage, sqft, condition). |

### Scrapling (Stealth Mode for Web Scraping)
```python
# Use Python with scrapling for stealthy web scraping on sites with anti-bot protection
# For JavaScript-heavy sites like TCAD, use browser automation instead

# Basic stealthy fetch (for non-JS pages)
python3 << 'EOF'
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
response = fetcher.fetch("https://example.com/non-js-page")
print(response.html_content)
EOF

# Save HTML output to file
python3 << 'EOF'
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
response = fetcher.fetch("https://example.com/page")
with open("scraped.html", "w") as f:
    f.write(response.html_content)
EOF

# Use with XPath/CSS selectors to extract data
python3 << 'EOF'
from scrapling import StealthyFetcher, Selector
fetcher = StealthyFetcher()
response = fetcher.fetch("https://example.com")
sel = Selector(text=response.html_content)
owner = sel.css(".owner-name").get()
print(owner)
EOF
```

### Browser Automation (JavaScript-heavy sites like TCAD)
```bash
# For sites that require JavaScript execution (like TCAD's React app)
browser open "https://travis.prodigycad.com/property/[propId]"
browser snapshot --fullPage

# Screenshot saved to /home/landon/.openclaw/media/browser/
# Upload to Drive as property photo
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

### Browser (TCAD/Research) - Use Browser Automation for JavaScript-heavy Sites
```bash
# TCAD is a React-powered site that requires JavaScript execution
# Use OpenClaw's browser tool for full page rendering
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

- **JavaScript-heavy sites (TCAD):** Use the `browser` tool for full page rendering. TCAD's React app requires JavaScript execution.
- **Sites with anti-bot protection (non-JS):** Use scrapling with `stealthy-fetch` to bypass Cloudflare and similar protections.
- Always check Drive first for existing research
- Property IDs (PropID) are stable identifiers in TCAD
- 2025 appraisal values are updated annually
- Street View images may be outdated
- Owner contact info from public records - verify before use
