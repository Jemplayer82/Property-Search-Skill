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
3. **TCAD Status Check** - Open travis.prodigycad.com and verify site is operational (not under maintenance)
4. **TCAD Lookup** - Get property data from travis.prodigycad.com
5. **Deed Search** - Check tccsearch.org for instrument history
6. **Owner Contact** - Find phone/email via people-finder databases
7. **Comps Analysis** - Pull comparable sales (3-5 properties, same area, 3-6 months)
8. **Create Folder** - Organize all documents in Google Drive
9. **Spell Check** - Review and correct all generated documents before finalizing

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

#### For TCAD (Travis County):
1. **Run pre-check first**: `web_fetch url="https://travis.prodigycad.com"`
2. **Only if pre-check passes**, open https://travis.prodigycad.com/property-search
3. **Check for maintenance message** - If site shows "under maintenance", try again later
3. Search for property and click PropID for detail page
4. **Click printer icon** (top-right corner of page)
5. Select "Print" and save as PDF
6. **Verify PDF downloaded** - check file size is reasonable (>50KB)
7. Upload to Drive as `TCAD_[PropID].pdf`

#### For Hays CAD (Hays County):
1. **Run pre-check first**: `web_fetch url="https://esearch.hayscad.com"`
2. **Only if pre-check passes**, open https://esearch.hayscad.com/
2. Search for property
3. Click on Quick Ref ID to view details
4. **Click "Print" button → select "Print Detailed View"**
5. Save as PDF - this contains ALL property data
6. Upload to Drive as `HaysCAD_[QuickRefID].pdf`

**Note:** The "Appraisal Notice" link downloads a different document (summary only). Use "Print Detailed View" for complete records.

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

### Browser Automation (TCAD/tccsearch.org)
```bash
# TCAD requires JavaScript - use browser tool
browser open "https://travis.prodigycad.com/property/[propId]"
browser snapshot --fullPage

# IMPORTANT: Click print button to generate PDF
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
