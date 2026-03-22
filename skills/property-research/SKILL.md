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

### Step 1b: Scan for Print/PDF Options (CRITICAL)
- **Always check for print/download buttons FIRST** before doing any data entry
- TCAD: Look for printer icon/button - use it to generate PDF
- tccsearch.org: Look for print/download options for deed records
- Any other official site with PDF generation should be used immediately
- If no print option available, then proceed with browser automation/screenshot

### Step 2: Create Drive Folder Structure
```
Property Address Folder/
├── 3516_Winding_Shore_Lane_Property_Report.pdf (Comprehensive PDF report)
├── TCAD_[PropertyID].pdf (Printer button PDF - PRIMARY DATA SOURCE)
├── Deed_Records.pdf (tccsearch.org print/download if available)
├── Owner_Contact_Info.gdoc (Google Doc with photo)
├── Google_Maps_Street_View.png
├── Comps_Analysis.md (comparable properties)
└── Deed_Records.md (from tccsearch.org if PDF not available)
```

### Step 2b: Create Comprehensive PDF Report
- Generate a single PDF report combining all research data
- **First page:** Title, street view + map view images stacked, Google Maps and Apple Maps buttons
- **Second page:** All property details, owner info, appraisal values, deed history, comps analysis
- **PDF structure:**
  - Title page (h1 + h2)
  - Property location image (street view on top, map view below)
  - Google Maps and Apple Maps buttons
  - Summary date block
  - PROPERTY DETAILS table
  - OWNER INFORMATION section
  - PROPERTY CHARACTERISTICS section
  - APPRASAL VALUES (2025) table
  - VALUE HISTORY table
  - TAXING UNITS table
  - DEED HISTORY table
  - COMPARABLE PROPERTIES ANALYSIS section
  - GOOGLE DRIVE FOLDER link
  - SOURCES list
  - NOTES section
  - Footer with generation note
- **Key formatting rules:**
  - No page breaks between headers and their content
  - Headers use `page-break-after: avoid`
  - Content sections use `page-break-inside: avoid`
  - Image fits on page with `max-height: 10in` and `object-fit: contain`

### Step 3: Gather Property Data
1. **Travis CAD (TCAD)**: Use browser automation via OpenClaw's `browser` tool to pull data from the React-powered site:
   - Property ID
   - Owner name(s)
   - Appraisal values
   - Property details (sqft, year built, etc.)
   - **PRINT TO PDF**: Always check for and use TCAD's printer button to generate a PDF of the property page. This is your primary method for capturing official property data. Upload this PDF as `TCAD_[PropertyID].pdf` to Google Drive.

2. **Deed Search**: Check tccsearch.org (Travis County Clerk) for:
   - Deed instrument numbers
   - Warranty deed dates
   - Previous owners
   - **PRINT TO PDF**: If tccsearch.org offers a print or download option, use it to capture deed records
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

### Step 7: Create Comprehensive PDF Report
Use Python with WeasyPrint to generate a professional PDF report:

```python
#!/usr/bin/env python3
"""
Create a comprehensive PDF property research report.
"""

from docx import Document
from docx.shared import Inches, Pt
from weasyprint import HTML

# Generate HTML with base64-encoded images
# Use CSS for page breaks to keep headers with content
# Images: street_view_page.jpg (top), map_page.jpg (bottom)
# Buttons: Google Maps and Apple Maps links

# HTML structure:
# - Title page (h1 + h2)
# - Property location image (street view + map stacked)
# - Google Maps and Apple Maps buttons
# - All property data tables and sections
# - No page breaks between headers and content

# Generate PDF
HTML('/tmp/property_report_base64.html').write_pdf('/home/landon/.openclaw/workspace/Property_Report.pdf')

# Upload to Google Drive
gog drive upload Property_Report.pdf --parent [folderId]
```

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

# Use TCAD's printer button to generate PDF of property page
# Upload the PDF to Google Drive as TCAD_[PropertyID].pdf
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

# Use TCAD's printer button to generate PDF of property page
# Upload the PDF to Google Drive as TCAD_[PropertyID].pdf
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
- [WeasyPrint](https://weasyprint.org) - PDF generation with CSS page breaks
- [python-docx](https://python-docx.readthedocs.io) - Word document generation

## Notes

- **ALWAYS PRINT TO PDF WHEN AVAILABLE**: Before doing anything else on property research sites, check if they offer a print or download button. Use it to capture official records. This includes:
  - TCAD's printer button (primary method)
  - tccsearch.org print/download options for deed records
  - Any other official property data sites that offer PDF generation

- **JavaScript-heavy sites (TCAD):** Use the `browser` tool for full page rendering. TCAD's React app requires JavaScript execution. **Always use the printer button on the TCAD page to generate a PDF**, not a screenshot.

- **Sites with anti-bot protection (non-JS):** Use scrapling with `stealthy-fetch` to bypass Cloudflare and similar protections.

- Always check Drive first for existing research
- Property IDs (PropID) are stable identifiers in TCAD
- 2025 appraisal values are updated annually
- Street View images may be outdated
- Owner contact info from public records - verify before use
