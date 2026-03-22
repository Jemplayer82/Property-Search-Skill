# TCAD Property Lookup Guide

## Travis Central Appraisal District (TCAD)

**Website:** https://travis.prodigycad.com

## Property Search

### Method 1: By Address
1. Go to https://travis.prodigycad.com/property-search
2. Enter street address (e.g., "3524 Winding Shore")
3. Select from autocomplete or search results
4. Click PropID to view details

### Method 2: By PropID
1. If you know the PropID, append to URL:
   `https://travis.prodigycad.com/property/[PropID]`
2. Example: `https://travis.prodigycad.com/property/550733`

## Data Points to Extract

| Field | Location on Page |
|-------|------------------|
| PropID | Top of page, in URL |
| Owner Name | "Owner" section |
| Mailing Address | Below owner name |
| Legal Description | "Property Details" |
| Geographic ID | "Property Details" |
| Year Built | "Characteristics" |
| Square Footage | "Characteristics" (GLA) |
| Lot Size | "Characteristics" (Acres) |
| Bedrooms/Bathrooms | "Characteristics" |
| 2025 Appraised Value | "Appraised Value" table |
| Land Value | Value breakdown |
| Improvement Value | Value breakdown |
| Value History | Historical table |
| Deed History | Recent transfers |

## CRITICAL: Use Print Button

**Before doing ANY data entry, click the printer icon.**

The TCAD print button generates a PDF containing:
- All property details
- Owner information
- Appraisal values
- Value history
- Taxing units
- Deed history

**Why this matters:**
- Official format from TCAD
- Contains ALL data in one document
- Faster than manual extraction
- Serves as authoritative reference

## Screenshot Fallback

If print button fails:
```bash
browser open "https://travis.prodigycad.com/property/[PropID]"
browser screenshot --fullPage --output tcad_[PropID].png
```

## tccsearch.org (Travis County Clerk)

**Website:** https://tccsearch.org

### Workflow (SLOW - JavaScript Heavy)

This site uses ASP.NET postbacks. Work methodically:

1. Open https://tccsearch.org
2. **Wait** for disclaimer page to load
3. Click "Click here to acknowledge the disclaimer"
4. **Wait** for main menu
5. Click "Real Estate" to expand submenu
6. **Wait** for submenu
7. Click "Search Real Estate Index"
8. **Wait** for search form
9. Fill search criteria (instrument #, name, or address)
10. Click Search
11. **Wait** for results
12. Click "View" to see document

### Document Types

| Code | Type | Notes |
|------|------|-------|
| WD | Warranty Deed | Primary ownership evidence |
| DTD | Deed of Trust | Mortgage/lien |
| QCD | Quit Claim Deed | Transfer without warranty |

### Downloading Deed PDFs

The document viewer loads in an iframe:

1. Look for download button in viewer
2. If available: Click to save PDF
3. If not available: Use browser print-to-PDF:
   ```bash
   browser print --pdf deed_[instrument].pdf
   ```

## Common Issues

### No Results Found
- Try searching by PropID
- Check alternate spellings (St vs Street, Rd vs Road)
- Verify address is in Travis County

### Multiple Properties
- Some addresses have multiple units/lots
- Check PropID matches expected property
- Note if condo/townhome (different PropIDs per unit)

### Page Won't Load
- TCAD occasionally has maintenance windows
- Try again in a few minutes
- Check travis.prodigycad.com/status if available

## File Naming Conventions

```
TCAD_[PropID].pdf              # TCAD property report (from print button)
deod_[instrument_number].pdf   # Deed document from tccsearch.org
Owner_Contact_Info.gdoc         # Google Doc with contact details
Comps_Analysis_[date].md        # Comparable properties analysis
[Address]_Property_Report.pdf   # Comprehensive combined report
```
