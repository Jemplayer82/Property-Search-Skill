---
name: property-research
version: 2.0.0
description: Research Texas property ownership, appraisal values, deed history, comparable sales, and owner contact info. Runs a full automated pipeline — CAD lookup, deed search, comps analysis, owner contact lookup, and a formatted PDF report — all uploaded to Google Drive. Supports Travis County (TCAD), Hays County (Hays CAD), and Williamson County (WCAD). Use when the user asks about a property address, wants property details, owner contact info, or a Drive research folder.
---

# Property Research Skill

Automated pipeline for Texas real estate research. One command pulls CAD appraisal data, deed history, comparable properties, and owner contact info — and generates a formatted PDF report — all organized into a Google Drive folder.

---

## Quick Start

```bash
# Full run — auto-creates Drive subfolder under a parent
python3 ~/.openclaw/workspace/skills/property-research/scripts/run_research.py \
  "3524 Winding Shore Lane, Pflugerville TX" \
  --drive-parent <parent_folder_id> \
  --owner "Ferguson Landon Jennifer"

# Full run — into an existing Drive folder
python3 ~/.openclaw/workspace/skills/property-research/scripts/run_research.py \
  "360 Purple Martin Ave, Kyle TX 78640" \
  --drive-folder <folder_id> \
  --owner "Ferguson Landon Jennifer" \
  --subdivision "Meadows at Kyle Phase Two"

# Skip steps you don't need
python3 ... --skip-comps --skip-deeds

# Already know the CAD ID — skip the search step
python3 ... --pid 550733
```

`run_research.py` does a **pre-flight site check** on all target websites before starting any work. If a site is down or in maintenance it skips that step cleanly instead of hammering it.

---

## Pipeline Steps

| Step | Script | What It Does |
|------|--------|-------------|
| 1. TCAD lookup | `tcad_lookup.py` | Searches Travis CAD by address, saves full property detail PDF to Drive |
| 2. Deed search | `deed_search.py` | Pulls Deed of Trust + Warranty Deed PDFs from tccsearch.org → Drive |
| 3. Comps | `comps.py` | Pulls comparable properties from TCAD by subdivision → markdown report → Drive |
| 4. Owner contact | `owner_lookup.py` | SearXNG + public records scrape for phone/email → markdown report → Drive |
| 5. PDF report | `generate_report.py` | Generates a formatted property research PDF with maps, stats, comps table → Drive |

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

### `tcad_lookup.py` — Travis CAD Property Data

Searches `travis.prodigycad.com` for a property by address or PID. Uses CDP browser automation to render the JavaScript SPA, then prints the full detail page to PDF.

```bash
python3 tcad_lookup.py "3524 Winding Shore Lane" \
  --drive-folder <id> --out-dir /tmp
```

**Requires:** Running Chrome instance with CDP relay on `http://127.0.0.1:18792`

### `deed_search.py` — Deed History

Searches `tccsearch.org` for deed documents by street address. Downloads Deed of Trust and Warranty Deed PDFs.

```bash
python3 deed_search.py "3524 Winding Shore" \
  --drive-folder <id> --out-dir /tmp
```

**Note:** Pass only the street portion of the address (no city/state). `run_research.py` does this automatically.

### `comps.py` — Comparable Properties (Travis County)

Searches TCAD by subdivision, scrapes comparable properties, outputs a markdown comps report.

```bash
python3 comps.py \
  --subdivision "Park at Blackhawk" \
  --subject-pid 550733 \
  --drive-folder <id> --out-dir /tmp
```

### `owner_lookup.py` — Owner Contact Info

Searches SearXNG (local instance at `http://192.168.7.17:8888`) for owner contact info via public records people-search sites.

```bash
python3 owner_lookup.py "Ferguson Landon Jennifer" "3524 Winding Shore Lane, Pflugerville TX" \
  --drive-folder <id> --out-dir /tmp
```

**Owner name format:** CAD format is `LastName FirstName Spouse` — pass as-is; the script builds name variants automatically.

### `generate_report.py` — PDF Report Generator

Generates a formatted property research PDF using WeasyPrint. Includes Google/Apple Maps links, stats bar, stacked map+street view images, owner info, property details, value history, deed history, and comps table.

```bash
python3 generate_report.py \
  --address "360 Purple Martin Ave, Kyle, TX 78640" \
  --prop-id R142280 \
  --owner1 "Landon S Ferguson" \
  --owner2 "Jennifer M Ferguson" \
  --mailing-address "9600 Escarpment Blvd Ste 745, Austin, TX 78749" \
  --year 2015 \
  --sqft 1500 \
  --land-value '$69,380' \
  --improvement-value '$199,790' \
  --total-value '$269,170' \
  --value-2024 '$303,120' \
  --value-2023 '$333,560' \
  --deed-instrument 2021221583 \
  --deed-type "Warranty Deed" \
  --deed-date "2021-08-15" \
  --previous-owner "Prior Owner Name" \
  --subdivision "Meadows at Kyle Phase Two" \
  --neighborhood "MEAK" \
  --prop-type "Residential" \
  --legal-desc "Lot 14, Block 3" \
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
      "address": "261 Purple Martin Ave",
      "cad_id": "R140221",
      "value": "$265,611",
      "diff": "-$3,559",
      "diff_pct": "-1.3%",
      "notes": "Same street, very close in value"
    }
  ],
  "summary": {
    "avg": "$289,554",
    "high": "$337,288",
    "low": "$265,611",
    "median": "$281,890",
    "variance": "-$20,384 (-7.0%)"
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
