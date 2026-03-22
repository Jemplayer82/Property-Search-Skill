---
name: property-research
version: 2.0.0
description: Research property ownership, appraisal values, deed history, comparable sales, and owner contact info. Runs a full automated pipeline — CAD lookup, deed search, comps analysis, owner contact lookup, and a formatted PDF report — all uploaded to Google Drive. Use when the user asks about a property address, wants property details, owner contact info, or a Drive research folder.
---

# Property Research Skill

Automated pipeline for real estate research. One command pulls CAD appraisal data, deed history, comparable properties, and owner contact info — and generates a formatted PDF report — all organized into a Google Drive folder.

---

## Quick Start

```bash
# Full run — auto-creates Drive subfolder under a parent
python3 ~/.openclaw/workspace/skills/property-research/scripts/run_research.py \
  "1234 Main St, Austin TX 78701" \
  --drive-parent <parent_folder_id> \
  --owner "Smith John Jane"

# Full run — into an existing Drive folder
python3 ~/.openclaw/workspace/skills/property-research/scripts/run_research.py \
  "1234 Main St, Austin TX 78701" \
  --drive-folder <folder_id> \
  --owner "Smith John Jane" \
  --subdivision "Example Subdivision"

# Skip steps you don't need
python3 ... --skip-comps --skip-deeds

# Already know the CAD ID — skip the search step
python3 ... --pid 123456
```

### Google Maps API Setup

To enable automatic map/street view image fetching (Step 5), add your API key to `.api-config`:

```bash
echo "GOOGLE_MAPS_API_KEY=your_actual_key_here" > ~/.openclaw/workspace/skills/property-research/.api-config
```

Or set as environment variable: `export GOOGLE_MAPS_API_KEY="your_key"`

---

`run_research.py` does a **pre-flight site check** on all target websites before starting any work. If a site is down or in maintenance it skips that step cleanly instead of hammering it.

---

## Pipeline Steps

| Step | Script | What It Does |
|------|--------|-------------|
| 1. TCAD lookup | `tcad_lookup.py` | Searches Travis CAD by address, saves full property detail PDF to Drive |
| 2. Deed search | `deed_search.py` | Pulls Deed of Trust + Warranty Deed PDFs from tccsearch.org → Drive |
| 3. Comps | `comps.py` | Pulls comparable properties from TCAD by subdivision → markdown report → Drive |
| 4. Owner contact | `owner_lookup.py` | SearXNG + public records scrape for phone/email → markdown report → Drive |
| 5. Fetch images | `fetch_images.py` | Downloads map + street view images from Google Maps API → Drive |
| 6. PDF report | `generate_report.py` | Generates a formatted property research PDF with images, stats, comps table → Drive |

---

### Google Maps API Setup

To enable automatic map/street view image fetching (Step 5), add your API key to `.api-config`:

```bash
echo "GOOGLE_MAPS_API_KEY=your_actual_key_here" > ~/.openclaw/workspace/skills/property-research/.api-config
```

Or set as environment variable: `export GOOGLE_MAPS_API_KEY="your_key"`

---

---

## Scripts Reference

### `run_research.py` — Full Pipeline Orchestrator

```
python3 run_research.py <address> [options]

Required (one of):
  --drive-folder <id>   Existing Drive folder ID — upload directly here
  --drive-parent <id>   Parent Drive folder ID — auto-creates subfolder named after address

Options:
  --pid <id>            CAD Property ID (skips address search)
  --owner <name>        Owner name for contact lookup (e.g. "Ferguson Landon Jennifer")
  --subdivision <name>  Subdivision for comps (default: "Park at Blackhawk")
  --skip-tcad           Skip TCAD lookup
  --skip-deeds          Skip deed search
  --skip-comps          Skip comps analysis
  --skip-owner          Skip owner contact lookup

```

### `fetch_images.py` — Google Maps Image Fetcher

Fetches Google Maps images (map view + street view) using Google Maps API.

```bash
python3 fetch_images.py "1234 Main St, Austin, TX 78701" \
  --output-dir /tmp --map-size 1200x800 --street-size 1200x800
```

**API Key:** Set `GOOGLE_MAPS_API_KEY` in `.api-config` file or environment variable.

**Output files:**
- `{address}_Map.png` - Static map image
- `{address}_Street.png` - Street view image

**Requires:** Google Maps Static API and Street View Image API enabled

### `tcad_lookup.py` — Travis CAD Property Data

Searches `travis.prodigycad.com` for a property by address or PID. Uses CDP browser automation to render the JavaScript SPA, then prints the full detail page to PDF.

```bash
python3 tcad_lookup.py "1234 Main St" \
  --drive-folder <id> --out-dir /tmp
```

**Requires:** Running Chrome instance with CDP relay on `http://127.0.0.1:18792`

### `deed_search.py` — Deed History

Searches `tccsearch.org` for deed documents by street address. Downloads Deed of Trust and Warranty Deed PDFs.

```bash
python3 deed_search.py "1234 Main" \
  --drive-folder <id> --out-dir /tmp
```

**Note:** Pass only the street portion of the address (no city/state). `run_research.py` does this automatically.

### `comps.py` — Comparable Properties (Travis County)

Searches TCAD by subdivision, scrapes comparable properties, outputs a markdown comps report.

```bash
python3 comps.py \
  --subdivision "Example Subdivision" \
  --subject-pid 123456 \
  --drive-folder <id> --out-dir /tmp
```

### `owner_lookup.py` — Owner Contact Info

Searches SearXNG (local instance at `http://192.168.7.17:8888`) for owner contact info via public records people-search sites.

```bash
python3 owner_lookup.py "Smith John Jane" "1234 Main St, Austin TX 78701" \
  --drive-folder <id> --out-dir /tmp
```

**Owner name format:** CAD format is `LastName FirstName Spouse` — pass as-is; the script builds name variants automatically.

### `generate_report.py` — PDF Report Generator

Generates a formatted property research PDF using WeasyPrint. Includes Google/Apple Maps links, stats bar, stacked map+street view images, owner info, property details, value history, deed history, and comps table.

```bash
python3 generate_report.py \
  --address "1234 Main St, Austin, TX 78701" \
  --prop-id R000000 \
  --owner1 "John Smith" \
  --owner2 "Jane Smith" \
  --mailing-address "1234 Main St, Austin, TX 78701" \
  --year 2010 \
  --sqft 1800 \
  --land-value '$50,000' \
  --improvement-value '$200,000' \
  --total-value '$250,000' \
  --value-2024 '$260,000' \
  --value-2023 '$255,000' \
  --deed-instrument 2020000000 \
  --deed-type "Warranty Deed" \
  --deed-date "2020-01-01" \
  --previous-owner "Prior Owner Name" \
  --subdivision "Example Subdivision" \
  --neighborhood "EXMP" \
  --prop-type "Residential" \
  --legal-desc "Lot 1, Block 1" \
  --map-view /tmp/map.jpg \
  --street-view /tmp/street.jpg \
  --comps-file /tmp/comps.json \
  --notes "Research notes here" \
  --output /tmp/Property_Report.pdf
```

**Comps JSON format (`--comps-file`):**
```json
{
  "comps": [
    {
      "address": "5678 Example Rd",
      "cad_id": "R000001",
      "value": "$250,000",
      "diff": "-$5,000",
      "diff_pct": "-2.0%",
      "notes": "Similar size and age"
    }
  ],
  "summary": {
    "avg": "$255,000",
    "high": "$270,000",
    "low": "$240,000",
    "median": "$252,000",
    "variance": "-$5,000 (-2.0%)"
  }
}
```

**Spell check:** `pyspellchecker` runs automatically on notes and comp notes before rendering. Skips proper nouns and domain words.

### `site_check.py` — Site Availability Utility

Pre-flight check before scraping. Performs a single streaming GET (reads first 4KB only) to detect HTTP errors and maintenance pages.

```python
from site_check import check_site, assert_site_up

# Non-fatal check
up, reason = check_site("https://travis.prodigycad.com")

# Fatal check — exits with clear message if down
assert_site_up("Travis CAD", "https://travis.prodigycad.com")
```

---

## Multi-County CAD Support

`tcad_lookup.py` and `comps.py` are Travis County specific (use CDP browser automation).

For other counties, use Chrome headless to print the detail page directly to PDF:

**Hays County (Hays CAD):**
```bash
# Find property: https://esearch.hayscad.com
# Detail URL: https://esearch.hayscad.com/Property/View/<QuickRefID>?year=2025&ownerId=<OwnerID>
google-chrome --headless --print-to-pdf="/tmp/HaysCAD_<ID>.pdf" --no-sandbox \
  "https://esearch.hayscad.com/Property/View/<QuickRefID>?year=2025&ownerId=<OwnerID>" 2>&1
```

**Williamson County (WCAD):**
```bash
# Find property: https://esearch.wcad.org/Search/Result?keywords=<address>
# Detail URL: https://esearch.wcad.org/Property/View/<id>
google-chrome --headless --print-to-pdf="/tmp/WCAD_<ID>.pdf" --no-sandbox \
  "https://esearch.wcad.org/Property/View/<id>" 2>&1
```

For non-TCAD counties, use `--skip-tcad --skip-deeds --skip-comps` and run `owner_lookup.py` + `generate_report.py` manually with the data you collected.

---

## Dependencies

```bash
# Python packages
pip install requests beautifulsoup4 websocket-client weasyprint pyspellchecker pillow \
    --break-system-packages

# gog CLI (Google Drive)
# Already installed and authenticated at ~/.config/gogcli/

# Chrome with CDP relay
# Required for tcad_lookup.py, deed_search.py, comps.py
# CDP relay at http://127.0.0.1:18792

# SearXNG
# Local instance at http://192.168.7.17:8888 (required for owner_lookup.py)
```

---

## Drive Organization

```
<Address>/
├── TCAD_<address>_PID<id>.pdf          # Travis CAD detail page (tcad_lookup.py)
├── Warranty_Deed_<instrument>.pdf       # Deed docs (deed_search.py)
├── Deed_of_Trust_<instrument>.pdf
├── Comps_<subdivision>_<date>.md       # Comps report (comps.py)
├── Owner_Lookup_<name>_<date>.md       # Owner contact (owner_lookup.py)
└── <Address>_Property_Report.pdf       # Formatted PDF (generate_report.py)
```

---

## References

- [TCAD Navigation Guide](references/tcad-guide.md) — TCAD site layout and data fields
