#!/usr/bin/env python3
"""
Generate comprehensive property research PDF report.
Requires: weasyprint, pillow
"""

import argparse
import base64
import json
from datetime import datetime
from pathlib import Path

try:
    from weasyprint import HTML, CSS
except ImportError:
    print("Error: weasyprint not installed. Run: pip install weasyprint")
    raise

try:
    from PIL import Image
except ImportError:
    print("Warning: pillow not installed. Image conversion may fail.")


def image_to_base64(image_path):
    if not image_path or not Path(image_path).exists():
        return None
    with open(image_path, 'rb') as f:
        data = f.read()
    ext = Path(image_path).suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return base64.b64encode(data).decode(), mime


def row(label, value):
    if not value or value in ("N/A", "None", "none"):
        return ""
    return f"<tr><th>{label}</th><td>{value}</td></tr>"


def generate_html_report(data, map_view=None, street_view=None, comps=None):
    today = datetime.now().strftime("%B %d, %Y")
    address = data.get('address', 'Unknown Address')
    address_encoded = address.replace(' ', '+')
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={address_encoded}"
    apple_maps_url = f"http://maps.apple.com/?q={address_encoded}"

    # Images
    map_html = ""
    if map_view:
        b64, mime = map_view
        map_html = f'<img src="data:{mime};base64,{b64}" class="map-image" alt="Map View">'

    street_html = ""
    if street_view:
        b64, mime = street_view
        street_html = f'<img src="data:{mime};base64,{b64}" class="street-image" alt="Street View">'

    # Hero stats
    stats = []
    if data.get('total_value'):
        stats.append(("Appraised Value", data['total_value'], "#1a6b3c"))
    if data.get('sqft'):
        stats.append(("Square Feet", data['sqft'], "#1a3a6b"))
    if data.get('year_built'):
        stats.append(("Year Built", data['year_built'], "#4a1a6b"))
    if data.get('prop_id'):
        stats.append(("CAD ID", data['prop_id'], "#6b4a1a"))

    stats_html = "".join(f"""
        <div class="stat-box" style="border-top: 4px solid {color}">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>""" for label, value, color in stats)

    # Value history
    value_history_rows = ""
    for year, key in [("2025", "total_value"), ("2024", "value_2024"), ("2023", "value_2023"), ("2022", "value_2022")]:
        val = data.get(key)
        if val and val not in ("N/A", "None"):
            value_history_rows += f"<tr><th>{year}</th><td>{val}</td></tr>"

    # Owner section
    owner_rows = (
        row("Primary Owner", data.get('owner1_name')) +
        row("Secondary Owner", data.get('owner2_name')) +
        row("Mailing Address", data.get('mailing_address'))
    )

    # Property details
    detail_rows = (
        row("Legal Description", data.get('legal_desc')) +
        row("Geographic ID", data.get('geo_id')) +
        row("Subdivision", data.get('subdivision')) +
        row("Neighborhood", data.get('neighborhood')) +
        row("Property Type", data.get('prop_type'))
    )

    # Characteristics
    char_rows = (
        row("Year Built", data.get('year_built')) +
        row("Square Footage", data.get('sqft')) +
        row("Lot Size", data.get('lot_size')) +
        row("Bedrooms", data.get('bedrooms')) +
        row("Bathrooms", data.get('bathrooms'))
    )

    # Appraisal
    appr_rows = (
        row("Land Value", data.get('land_value')) +
        row("Improvement Value", data.get('improvement_value')) +
        row("Total Appraised Value", f"<strong>{data.get('total_value', '')}</strong>" if data.get('total_value') else None)
    )

    # Deed history
    deed_rows = (
        row("Instrument Number", data.get('deed_instrument')) +
        row("Deed Type", data.get('deed_type')) +
        row("Recording Date", data.get('deed_date')) +
        row("Previous Owner", data.get('previous_owner'))
    )

    # Comps
    comps_html = ""
    if comps:
        comp_rows = ""
        for i, c in enumerate(comps.get("comps", []), 1):
            pct = c.get("diff_pct", "")
            diff_val = c.get("diff", "")
            if pct.startswith("+"):
                diff_class = "diff-pos"
            elif pct.startswith("-"):
                diff_class = "diff-neg"
            else:
                diff_class = "diff-zero"
            comp_rows += f"""<tr>
                <td>{i}</td>
                <td>{c.get('address','')}</td>
                <td>{c.get('cad_id','')}</td>
                <td><strong>{c.get('value','')}</strong></td>
                <td class="{diff_class}">{diff_val} ({pct})</td>
                <td class="notes">{c.get('notes','')}</td>
            </tr>"""

        s = comps.get("summary", {})
        summary_html = ""
        for label, key in [("Average", "avg"), ("High", "high"), ("Low", "low"), ("Median", "median"), ("vs Average", "variance")]:
            val = s.get(key)
            if val:
                summary_html += f'<div class="comp-stat"><div class="comp-stat-label">{label}</div><div class="comp-stat-value">{val}</div></div>'

        comps_html = f"""
        <div class="section">
            <h2>Comparable Properties (2025 Appraised Values)</h2>
            <table class="comps-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Address</th>
                        <th>CAD ID</th>
                        <th>Value</th>
                        <th>vs Subject</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>{comp_rows}</tbody>
            </table>
            {"<div class='comps-summary'>" + summary_html + "</div>" if summary_html else ""}
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Property Report - {address}</title>
    <style>
        @page {{
            size: letter;
            margin: 0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 9.5pt;
            line-height: 1.5;
            color: #222;
            background: #fff;
        }}

        /* HEADER */
        .header {{
            background: #0f2137;
            color: white;
            padding: 22pt 30pt 18pt;
        }}
        .header-label {{
            font-size: 7.5pt;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #7aa8cc;
            margin-bottom: 4pt;
        }}
        .header-address {{
            font-size: 20pt;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 6pt;
        }}
        .header-meta {{
            font-size: 8.5pt;
            color: #aac4dd;
        }}
        .header-links {{
            margin-top: 10pt;
            display: flex;
            gap: 8pt;
        }}
        .header-link {{
            display: inline-block;
            padding: 5pt 12pt;
            background: rgba(255,255,255,0.12);
            color: white;
            text-decoration: none;
            border-radius: 3pt;
            font-size: 8pt;
            border: 1px solid rgba(255,255,255,0.25);
        }}

        /* STATS ROW */
        .stats-row {{
            display: flex;
            border-bottom: 2px solid #e8edf2;
        }}
        .stat-box {{
            flex: 1;
            padding: 12pt 16pt;
            border-right: 1px solid #e8edf2;
        }}
        .stat-box:last-child {{ border-right: none; }}
        .stat-label {{
            font-size: 7pt;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #888;
            margin-bottom: 3pt;
        }}
        .stat-value {{
            font-size: 14pt;
            font-weight: 700;
            color: #0f2137;
        }}

        /* MAP */
        .map-container {{
            width: 100%;
            max-height: 220pt;
            overflow: hidden;
            border-bottom: 2px solid #e8edf2;
        }}
        .map-image {{
            width: 100%;
            display: block;
            object-fit: cover;
            max-height: 220pt;
        }}
        .street-image {{
            width: 100%;
            display: block;
            max-height: 180pt;
            object-fit: cover;
            border-bottom: 2px solid #e8edf2;
        }}

        /* CONTENT */
        .content {{
            padding: 18pt 30pt;
        }}

        /* TWO COLUMN */
        .two-col {{
            display: flex;
            gap: 20pt;
            margin-bottom: 16pt;
        }}
        .col {{ flex: 1; }}

        /* SECTIONS */
        .section {{
            margin-bottom: 16pt;
            page-break-inside: avoid;
        }}
        h2 {{
            font-size: 8pt;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #0f2137;
            border-bottom: 2px solid #0f2137;
            padding-bottom: 4pt;
            margin-bottom: 8pt;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 8.5pt;
        }}
        th {{
            text-align: left;
            padding: 5pt 8pt;
            background: #f4f7fa;
            color: #555;
            font-weight: 600;
            width: 42%;
            border-bottom: 1px solid #e0e6ed;
        }}
        td {{
            padding: 5pt 8pt;
            border-bottom: 1px solid #e0e6ed;
            color: #222;
        }}
        tr:last-child th, tr:last-child td {{ border-bottom: none; }}

        /* VALUE HISTORY */
        .value-table th {{ width: 30%; }}
        .value-highlight td {{ font-weight: 700; color: #1a6b3c; }}

        /* COMPS TABLE */
        .comps-table th {{
            width: auto;
            white-space: nowrap;
        }}
        .comps-table td {{ white-space: nowrap; }}
        .comps-table td.notes {{ white-space: normal; color: #666; font-size: 8pt; }}
        .diff-pos {{ color: #c0392b; font-weight: 600; }}
        .diff-neg {{ color: #1a6b3c; font-weight: 600; }}
        .diff-zero {{ color: #555; font-weight: 600; }}
        .comps-summary {{
            display: flex;
            gap: 0;
            margin-top: 10pt;
            border: 1px solid #e0e6ed;
            border-radius: 4pt;
            overflow: hidden;
        }}
        .comp-stat {{
            flex: 1;
            padding: 8pt 10pt;
            border-right: 1px solid #e0e6ed;
            text-align: center;
        }}
        .comp-stat:last-child {{ border-right: none; }}
        .comp-stat-label {{
            font-size: 6.5pt;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #999;
            margin-bottom: 2pt;
        }}
        .comp-stat-value {{
            font-size: 10pt;
            font-weight: 700;
            color: #0f2137;
        }}

        /* FOOTER */
        .footer {{
            margin-top: 18pt;
            padding: 10pt 0 0;
            border-top: 1px solid #dde3ea;
            font-size: 7.5pt;
            color: #aaa;
            text-align: center;
        }}
    </style>
</head>
<body>

    <div class="header">
        <div class="header-label">Property Research Report</div>
        <div class="header-address">{address}</div>
        <div class="header-meta">Generated {today} &nbsp;·&nbsp; OpenClaw</div>
        <div class="header-links">
            <a href="{google_maps_url}" class="header-link">Google Maps</a>
            <a href="{apple_maps_url}" class="header-link">Apple Maps</a>
        </div>
    </div>

    {"<div class='stats-row'>" + stats_html + "</div>" if stats_html else ""}

    {"<div class='map-container'>" + map_html + "</div>" if map_html else ""}
    {street_html}

    <div class="content">

        <div class="two-col">
            {"<div class='col'><div class='section'><h2>Owner Information</h2><table>" + owner_rows + "</table></div></div>" if owner_rows else ""}
            {"<div class='col'><div class='section'><h2>Property Details</h2><table>" + detail_rows + "</table></div></div>" if detail_rows else ""}
        </div>

        {"<div class='section'><h2>Property Characteristics</h2><table>" + char_rows + "</table></div>" if char_rows else ""}

        {"<div class='section'><h2>Appraisal Values (2025)</h2><table>" + appr_rows + "</table></div>" if appr_rows else ""}

        {"<div class='section'><h2>Value History</h2><table class='value-table'>" + value_history_rows + "</table></div>" if value_history_rows else ""}

        {"<div class='section'><h2>Deed History</h2><table>" + deed_rows + "</table></div>" if deed_rows else ""}

        {comps_html if comps_html else "<div class='section'><h2>Comparable Properties</h2><p style='color:#555;font-size:8.5pt'>See <em>Comps_Analysis.md</em> in Google Drive folder for detailed comparable property analysis.</p></div>"}

        {('<div class="section"><h2>Notes</h2><p style="color:#555;font-size:8.5pt">' + data['notes'] + '</p></div>') if data.get('notes') else ''}

        <div class="footer">
            Generated by Property Research Skill &nbsp;·&nbsp; OpenClaw &nbsp;·&nbsp; {today}
        </div>

    </div>
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser(description='Generate property research PDF report')
    parser.add_argument('--address', '-a', required=True)
    parser.add_argument('--prop-id', '-p')
    parser.add_argument('--owner1')
    parser.add_argument('--owner2')
    parser.add_argument('--mailing-address', '-m')
    parser.add_argument('--legal-desc')
    parser.add_argument('--geo-id')
    parser.add_argument('--subdivision')
    parser.add_argument('--neighborhood')
    parser.add_argument('--prop-type')
    parser.add_argument('--year')
    parser.add_argument('--sqft')
    parser.add_argument('--lot-size')
    parser.add_argument('--bedrooms')
    parser.add_argument('--bathrooms')
    parser.add_argument('--land-value')
    parser.add_argument('--improvement-value')
    parser.add_argument('--total-value', '-v')
    parser.add_argument('--value-2024')
    parser.add_argument('--value-2023')
    parser.add_argument('--value-2022')
    parser.add_argument('--deed-instrument')
    parser.add_argument('--deed-type')
    parser.add_argument('--deed-date')
    parser.add_argument('--previous-owner')
    parser.add_argument('--notes')
    parser.add_argument('--comps-file', help='Path to comps JSON file')
    parser.add_argument('--street-view')
    parser.add_argument('--map-view')
    parser.add_argument('--output', '-o', required=True)

    args = parser.parse_args()

    data = {
        'address': args.address,
        'prop_id': args.prop_id,
        'owner1_name': args.owner1,
        'owner2_name': args.owner2,
        'mailing_address': args.mailing_address,
        'legal_desc': args.legal_desc,
        'geo_id': args.geo_id,
        'subdivision': args.subdivision,
        'neighborhood': args.neighborhood,
        'prop_type': args.prop_type,
        'year_built': args.year,
        'sqft': args.sqft,
        'lot_size': args.lot_size,
        'bedrooms': args.bedrooms,
        'bathrooms': args.bathrooms,
        'land_value': args.land_value,
        'improvement_value': args.improvement_value,
        'total_value': args.total_value,
        'value_2024': args.value_2024,
        'value_2023': args.value_2023,
        'value_2022': args.value_2022,
        'deed_instrument': args.deed_instrument,
        'deed_type': args.deed_type,
        'deed_date': args.deed_date,
        'previous_owner': args.previous_owner,
        'notes': args.notes,
    }

    map_view = image_to_base64(args.map_view) if args.map_view else None
    street_view = image_to_base64(args.street_view) if args.street_view else None
    comps = json.loads(Path(args.comps_file).read_text()) if args.comps_file else None

    html_content = generate_html_report(data, map_view, street_view, comps)
    HTML(string=html_content).write_pdf(args.output)
    print(f"PDF generated: {args.output}")


if __name__ == '__main__':
    main()
