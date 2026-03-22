---
name: property-research
description: Research Texas property ownership, appraisal values, and owner contact information. Use when the user asks about a property address, wants to find property details, owner information, or create organized research folders in Google Drive. Handles Travis County CAD (TCAD) lookups, owner contact searches, comps analysis, and Google Drive document creation with property photos.
---

# Property Research

Research Texas property ownership, appraisal values, and owner contact information. Creates organized Google Drive folders with property data, owner contact info, and street view photos. Currently optimized for Travis County (TCAD) but adaptable to other counties.

## Workflow Overview

**PRE-CHECK (ALWAYS RUN FIRST for ANY website):**
1. **Site Status Check** - Run `web_fetch` on target URL to verify:
   - HTTP 200 status (implied if fetch succeeds)
   - NO maintenance/error message in response
   - Site is actually responsive
2. **Only then proceed** with browser automation or data extraction

2. **Check Drive** - Search for existing folder by property address
3. **CAD Status Check** - Open CAD site and verify it's operational (not under maintenance)
4. **CAD Lookup** - Get property data from CAD site
5. **PDF Download** - Use Chrome headless to download full detail PDF from CAD site
6. **PDF Report Generation** - Use `generate_report.py` to create comprehensive PDF report
7. **Deed Search** - Check tccsearch.org for instrument history (if applicable)
8. **Owner Contact** - Find phone/email via people-finder databases
9. **Comps Analysis** - Pull comparable sales (3-5 properties, same area, 3-6 months)
10. **Create Folder** - Organize all documents in Google Drive
11. **Spell Check** - Review and correct all generated documents before finalizing

## Communication Requirements

**Send status update at the start of each section:**
- "Starting [Section Name]..."
- Brief context of what this step does

**Notify immediately on failure:**
- If a step fails or is blocked, report it right away
- Explain what failed and why
- Offer alternatives or next steps
- Do not proceed silently past failures without user awareness

**IMPORTANT - Site Status Check Required:**
- For ANY new website (TCAD, tccsearch.org, people-finders, etc.): ALWAYS run `web_fetch` first
- If site is down/maintenance: STOP and report immediately
- Do NOT start browser automation without verifying site responsiveness

## Quick Reference

### File Naming
```
Property Address Folder/
├── [Address]_Property_Report.pdf    # Comprehensive PDF report
├── TCAD_[PropID].pdf                # TCAD print/download (PRIMARY)
├── Owner_Contact_Info.gdoc           # Contact info with photo
├── Google_Maps_Street_View.png       # Street view image
└── Comps_Analysis.md                 # Comparable properties
```

### CAD Document Download (CRITICAL - DO NOT SKIP)

**⚠️ NEVER rely solely on scraped webpage data. Always get the official CAD PDF document.**

The official PDF contains complete property records including:
- All property details and characteristics
- Complete value history
- Full deed history
- Building/land breakdowns
- Taxing jurisdictions
- Legal descriptions

#### For ANY CAD Website - Print Full Detail View PDF

**IMPORTANT - Use system print-to-PDF for complete documents:**
- Many CAD sites use dynamic JavaScript menus that prevent direct PDF downloads
- Browser automation cannot trigger system print dialogs
- **Use Chrome headless mode to generate proper printouts**

```bash
google-chrome --headless --print-to-pdf="/path/to/output.pdf" --no-sandbox "https://target-site.com/property-url" 2>&1
```

**For TCAD (Travis County):**
1. **Run pre-check first**: `web_fetch url="https://travis.prodigycad.com"`
2. **Only if pre-check passes**, open property page: `https://travis.prodigycad.com/property/[propId]`
3. **Print using Chrome headless** (full detail view includes all sections):
```bash
google-chrome --headless --print-to-pdf="TCAD_[PropID].pdf" --no-sandbox "https://travis.prodigycad.com/property/[propId]" 2>&1
```
4. **Verify PDF downloaded** - check file size is reasonable (>50KB)
5. Upload to Drive as `TCAD_[PropID].pdf`

**For Hays CAD (Hays County):**
1. **Run pre-check first**: `web_fetch url="https://esearch.hayscad.com"`
2. **Only if pre-check passes**, open property page: `https://esearch.hayscad.com/Property/View/[QuickRefID]?year=2025&ownerId=[OwnerID]`
3. **Print using Chrome headless** (full detail view includes all sections):
```bash
google-chrome --headless --print-to-pdf="HaysCAD_[QuickRefID].pdf" --no-sandbox "https://esearch.hayscad.com/Property/View/[QuickRefID]?year=2025&ownerId=[OwnerID]" 2>&1
```
4. **Verify PDF downloaded** - check file size is reasonable (>50KB)
5. Upload to Drive as `HaysCAD_[QuickRefID].pdf`

**For ANY other CAD website:**
1. **Run pre-check first**: `web_fetch url="https://target-cad-site.com"`
2. **Open the property detail page URL in Chrome headless**:
```bash
google-chrome --headless --print-to-pdf="CAD_[Site]_[ID].pdf" --no-sandbox "https://target-cad-site.com/property/[specificPath]" 2>&1
```
3. **Verify PDF downloaded** - check file size is reasonable (>50KB)
4. Upload to Drive as `CAD_[Site]_[ID].pdf`

**Note:** The "Appraisal Notice" or similar summary links download incomplete documents. Always use Chrome headless print-to-PDF for the complete detailed view.

### Document Verification Checklist

Before proceeding, verify you have:
- [ ] Official PDF downloaded and saved
- [ ] File size >50KB (ensures complete document)
- [ ] PDF opens and displays property data
- [ ] PDF uploaded to Google Drive
- [ ] All sections visible (Property Details, Values, Deed History, etc.)

### ⚠️ Common Mistakes to Avoid

**DON'T:**
- Scrape individual fields from the webpage and skip the PDF
- Use only the "Appraisal Notice" summary (may be incomplete)
- Assume data from webpage search results is sufficient
- Start browser automation without first verifying site is up (HTTP 200 and not maintenance page)

**DO:**
- Always get the full detailed print view
- Verify PDF contains all sections before closing browser
- Use the PDF as the primary data source for the report
- Run pre-check: `web_fetch` on CAD homepage to confirm HTTP 200 and no maintenance message before starting automation

### Handling CAD Maintenance

If CAD site is under maintenance:
- Document the maintenance status in research notes
- Try again later (usually resolved within hours)
- Consider using cached/previous year data if available

### Pre-Check: Verify ANY Site Before Automation

**ALWAYS run this before starting browser automation on a new website:**

```bash
web_fetch url="https://target-site.com" extractMode="text"
```

**Check for:**
- HTTP 200 status (implied if fetch succeeds)
- NO "under maintenance" or error message in response
- Normal page title/content

**If site is down/maintenance:**
- STOP automation immediately
- Report: "[Site] is under maintenance - cannot proceed"
- Suggest trying again later or using alternative method

### Downloading Documents from ANY Website Using Chrome Headless

When a website requires full-page PDF downloads but doesn't provide direct download links:
1. Open the target URL in Chrome headless mode
2. Use `--print-to-pdf` flag to save as PDF

```bash
google-chrome --headless --print-to-pdf="/path/to/output.pdf" --no-sandbox "https://target-website.com/page" 2>&1
```

**Requirements:**
- Google Chrome must be installed
- The `--no-sandbox` flag is required for headless mode
- Output path should be an absolute path
- Check exit code and file size to verify success

### PDF Report Generation (GENERIC)

After downloading the CAD PDF, generate a comprehensive property research report:

```bash
python3 ~/.openclaw/workspace/skills/property-research/scripts/generate_report.py \
  --address "Property Address, City, State ZIP" \
  --prop-id "CAD_ID" \
  --owner1 "Owner 1 Name" \
  --owner2 "Owner 2 Name" \
  --mailing-address "Owner Mailing Address" \
  --legal-desc "Legal Description" \
  --subdivision "Subdivision Name" \
  --neighborhood "Neighborhood Code" \
  --prop-type "Property Type" \
  --year "Year Built" \
  --sqft "Living Area" \
  --land-value "Land Value" \
  --improvement-value "Improvement Value" \
  --total-value "Total Appraised Value" \
  --value-2024 "2024 Value" \
  --value-2023 "2023 Value" \
  --value-2022 "2022 Value" \
  --deed-instrument "Instrument Number" \
  --deed-type "Deed Type" \
  --deed-date "Recording Date" \
  --previous-owner "Previous Owner" \
  --notes "Research Notes" \
  --output "Output_PDF_Name.pdf"
```

**Requirements:**
- WeasyPrint must be installed: `pip install weasyprint`
- Spell checker is optional but recommended: `pip install pyspellchecker`

**Output:**
- Comprehensive PDF report with property details, value history, deed history
- Auto spell check on notes and comps
- Google Maps/Appl Maps links in header
- Property statistics row

### Owner Contact Sources
- NationalPublicData.com
- FastBackgroundCheck.com
- ThatsThem.com

Search pattern: `[FirstName] [LastName] [City] [State] phone`

### Comps Selection Rules
| Guideline | Rule |
|-----------|------|
| Location | Same neighborhood, 0.5-1 mile radius |
| Time | Last 3-6 months (90 days ideal) |
| Size | Within 20% of subject GLA |
| Age/Style | Same era and design |
| Uniformity | 3-5 similar properties |

## Tools & Commands

### Downloading Documents from ANY Website (Generic)
```bash
# Chrome headless print-to-PDF (works for any website)
google-chrome --headless --print-to-pdf="/path/to/output.pdf" --no-sandbox "https://target-site.com/page" 2>&1
```

### PDF Report Generation (Generic)
```bash
python3 ~/.openclaw/workspace/skills/property-research/scripts/generate_report.py \
  --address "Address" \
  --prop-id "CAD_ID" \
  --owner1 "Owner 1" \
  --owner2 "Owner 2" \
  --total-value "$Value" \
  --output "Report_Name.pdf"
```

### Browser Automation (TCAD/tccsearch.org)
```bash
# TCAD requires JavaScript - use browser tool
browser open "https://travis.prodigycad.com/property/[propId]"
browser snapshot --fullPage

# IMPORTANT: Chrome headless is preferred for PDF downloads (captures full detail view)
# Upload TCAD_[PropID].pdf to Drive
```

### Scrapling (Stealth for anti-bot sites)
```python
from scrapling import StealthyFetcher
fetcher = StealthyFetcher()
# First verify site is up with web_fetch before using scrapling
# web_fetch url="https://target-site.com"
response = fetcher.fetch("https://example.com")
print(response.html_content)
```

### Google Drive
```bash
# Search existing folder
gog drive search "Property Address" --json

# Create folder
gog drive folder-create "3524 Winding Shore Lane" --parent [parentId]

# Upload
gog drive upload file.pdf --parent [folderId]

# Get folder ID for upload
gog drive search "Folder Name" --json
```

### Owner Contact Script
```bash
python3 scripts/owner_contact.py "Owner Name" --address "Property Address" --prop-id [PropID] --output owner.md
```

### PDF Report Generation
```bash
python3 scripts/generate_report.py \
  --address "3524 Winding Shore Lane, Pflugerville, TX" \
  --prop-id 550733 \
  --owner1 "Landon Ferguson" \
  --total-value "$461,373" \
  --street-view street_view.jpg \
  --map-view map_view.jpg \
  --output Property_Report.pdf
```

## Detailed Guides

- **TCAD Navigation**: See [references/tcad-guide.md](references/tcad-guide.md)
- **tccsearch.org Workflow**: See references/tcad-guide.md (deed search section)

## Cleanup

**Always close browser when done:**
```bash
browser stop
```

This prevents session conflicts and releases resources.
