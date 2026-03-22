# TCAD Property Lookup Guide

## TCAD Website Navigation

### Property Search
1. Go to https://travis.prodigycad.com
2. Use "Property Search" to find by address or PropID
3. Property page shows:
   - **Owner Name**: Primary owner(s) on record
   - **Property ID**: Unique identifier (e.g., 550733)
   - **Appraised Value**: Current year taxable value
   - **Land/Improvement Values**: Breakdown
   - **Property Details**: Square footage, year built, lot size

### Key Data Points
- **PropID**: Use this for all references (stable ID)
- **Geographic ID**: Legal description
- **Owner Name**: Exactly as recorded
- **Mailing Address**: May differ from property address
- **Exemptions**: Homestead, over-65, etc.

## Screenshot Best Practices

1. Navigate to property page
2. Use `browser screenshot --fullPage` to capture entire page
3. Save to `/home/landon/.openclaw/media/browser/`
4. Upload to Drive with naming: `TCAD_[PropID].png`

## Common Issues

### No Results Found
- Try searching by PropID if known
- Check alternate spellings (Rd vs Road, etc.)
- Verify the address is in Travis County

### Multiple Properties
- Some addresses have multiple units/lots
- Check PropID to ensure correct property
- Note if it's a condo, townhome, etc.

## Deed Search (tccsearch.org)

1. Go to https://tccsearch.org
2. Search by name or instrument number
3. Look for:
   - **Warranty Deed** (primary ownership transfer)
   - **Deed of Trust** (mortgage/lien)
   - **Quit Claim Deed** (transfer without warranty)

### Document Types
- **WD**: Warranty Deed (best ownership evidence)
- **DTD**: Deed of Trust
- **QCD**: Quit Claim Deed

## File Naming Conventions

```
TCAD_[PropID].pdf          # TCAD property page
Owner_Contact_Info.gdoc    # Google Doc with contact info
deod_[instrument].pdf     # Deed document
Comps_[date].md            # Comparable analysis
```
