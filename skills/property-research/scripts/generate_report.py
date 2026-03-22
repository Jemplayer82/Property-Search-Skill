#!/usr/bin/env python3
"""
Generate comprehensive property research PDF report.
Requires: weasyprint, pillow
"""

import argparse
import base64
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
    """Convert image to base64 for embedding in HTML"""
    if not image_path or not Path(image_path).exists():
        return None
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def generate_html_report(data, street_view_b64=None, map_view_b64=None):
    """Generate HTML for PDF conversion"""
    
    # Get current date
    today = datetime.now().strftime("%B %d, %Y")
    
    # Images HTML
    images_html = ""
    if street_view_b64:
        images_html += f'<img src="data:image/jpeg;base64,{street_view_b64}" class="property-image" alt="Street View">'
    if map_view_b64:
        images_html += f'<img src="data:image/jpeg;base64,{map_view_b64}" class="property-image" alt="Map View">'
    
    # Google/Apple Maps links
    address_encoded = data.get('address', '').replace(' ', '+')
    google_maps_url = f"https://www.google.com/maps/search/?api=1\u0026query={address_encoded}"
    apple_maps_url = f"http://maps.apple.com/?q={address_encoded}"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Property Report - {data.get('address', 'Unknown')}</title>
    <style>
        @page {{
            size: letter;
            margin: 0.75in;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 10pt;
            line-height: 1.4;
            color: #333;
        }}
        h1 {{
            font-size: 18pt;
            color: #1a1a1a;
            margin-bottom: 4pt;
            page-break-after: avoid;
        }}
        h2 {{
            font-size: 12pt;
            color: #333;
            border-bottom: 1px solid #ddd;
            padding-bottom: 4pt;
            margin-top: 16pt;
            margin-bottom: 8pt;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 10pt;
            color: #444;
            margin-top: 12pt;
            margin-bottom: 4pt;
            page-break-after: avoid;
        }}
        .subtitle {{
            font-size: 11pt;
            color: #666;
            margin-bottom: 16pt;
        }}
        .date-block {{
            background: #f5f5f5;
            padding: 8pt 12pt;
            border-radius: 4pt;
            margin: 12pt 0;
            font-size: 9pt;
            color: #666;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 8pt 0;
            font-size: 9pt;
            page-break-inside: avoid;
        }}
        th, td {{
            text-align: left;
            padding: 6pt 8pt;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f8f8;
            font-weight: 600;
            width: 35%;
        }}
        tr:last-child td {{
            border-bottom: 2px solid #ddd;
        }}
        .property-image {{
            width: 100%;
            max-height: 4in;
            object-fit: contain;
            margin: 8pt 0;
            border: 1px solid #ddd;
            border-radius: 4pt;
        }}
        .map-buttons {{
            margin: 12pt 0;
            text-align: center;
        }}
        .map-button {{
            display: inline-block;
            padding: 8pt 16pt;
            margin: 0 4pt;
            background: #4285f4;
            color: white;
            text-decoration: none;
            border-radius: 4pt;
            font-size: 9pt;
        }}
        .map-button.apple {{
            background: #007aff;
        }}
        .section {{
            page-break-inside: avoid;
        }}
        .footer {{
            margin-top: 24pt;
            padding-top: 12pt;
            border-top: 1px solid #ddd;
            font-size: 8pt;
            color: #999;
            text-align: center;
        }}
        ul {{
            margin: 4pt 0;
            padding-left: 16pt;
        }}
        li {{
            margin: 2pt 0;
        }}
    </style>
</head>
<body>
    <h1>Property Research Report</h1>
    <p class="subtitle">{data.get('address', 'Unknown Address')}</p>
    
    <div class="section">
        {images_html}
    </div>
    
    <div class="map-buttons">
        <a href="{google_maps_url}" class="map-button">Open in Google Maps</a>
        <a href="{apple_maps_url}" class="map-button apple">Open in Apple Maps</a>
    </div>
    
    <div class="date-block">
        Report Generated: {today}
    </div>
    
    <h2>Property Details</h2>
    <table>
        <tr><th>TCAD PropID</th><td>{data.get('prop_id', 'N/A')}</td></tr>
        <tr><th>Legal Description</th><td>{data.get('legal_desc', 'N/A')}</td></tr>
        <tr><th>Geographic ID</th><td>{data.get('geo_id', 'N/A')}</td></tr>
    </table>
    
    <h2>Owner Information</h2>
    <table>
        <tr><th>Primary Owner</th><td>{data.get('owner1_name', 'N/A')}</td></tr>
        <tr><th>Mailing Address</th><td>{data.get('mailing_address', 'N/A')}</td></tr>
        <tr><th>Secondary Owner</th><td>{data.get('owner2_name', 'N/A')}</td></tr>
    </table>
    
    <h2>Property Characteristics</h2>
    <table>
        <tr><th>Year Built</th><td>{data.get('year_built', 'N/A')}</td></tr>
        <tr><th>Square Footage</th><td>{data.get('sqft', 'N/A')}</td></tr>
        <tr><th>Lot Size</th><td>{data.get('lot_size', 'N/A')}</td></tr>
        <tr><th>Bedrooms</th><td>{data.get('bedrooms', 'N/A')}</td></tr>
        <tr><th>Bathrooms</th><td>{data.get('bathrooms', 'N/A')}</td></tr>
    </table>
    
    <h2>Appraisal Values (2025)</h2>
    <table>
        <tr><th>Land Value</th><td>{data.get('land_value', 'N/A')}</td></tr>
        <tr><th>Improvement Value</th><td>{data.get('improvement_value', 'N/A')}</td></tr>
        <tr><th>Total Appraised Value</th><td><strong>{data.get('total_value', 'N/A')}</strong></td></tr>
    </table>
    
    <h2>Value History</h2>
    <table>
        <tr><th>2024 Appraised</th><td>{data.get('value_2024', 'N/A')}</td></tr>
        <tr><th>2023 Appraised</th><td>{data.get('value_2023', 'N/A')}</td></tr>
        <tr><th>2022 Appraised</th><td>{data.get('value_2022', 'N/A')}</td></tr>
    </table>
    
    <h2>Deed History</h2>
    <table>
        <tr><th>Latest Instrument</th><td>{data.get('deed_instrument', 'N/A')}</td></tr>
        <tr><th>Deed Type</th><td>{data.get('deed_type', 'N/A')}</td></tr>
        <tr><th>Recording Date</th><td>{data.get('deed_date', 'N/A')}</td></tr>
        <tr><th>Previous Owner</th><td>{data.get('previous_owner', 'N/A')}</td></tr>
    </table>
    
    <h2>Comparable Properties</h2>
    <p><em>See Comps_Analysis.md in Google Drive folder for detailed comparable property analysis.</em></p>
    
    <h2>Sources</h2>
    <ul>
        <li>Travis Central Appraisal District (TCAD) - travis.prodigycad.com</li>
        <li>Travis County Clerk - tccsearch.org</li>
        <li>Google Maps Street View</li>
    </ul>
    
    <h2>Notes</h2>
    <p>{data.get('notes', 'Add research notes here...')}</p>
    
    <div class="footer">
        Generated by Property Research Skill · OpenClaw
    </div>
</body>
</html>"""
    
    return html

def main():
    parser = argparse.ArgumentParser(description='Generate property research PDF report')
    parser.add_argument('--address', '-a', required=True, help='Property address')
    parser.add_argument('--prop-id', '-p', help='TCAD PropID')
    parser.add_argument('--owner1', '-o1', help='Primary owner name')
    parser.add_argument('--owner2', '-o2', help='Secondary owner name')
    parser.add_argument('--mailing-address', '-m', help='Owner mailing address')
    parser.add_argument('--year', '-y', help='Year built')
    parser.add_argument('--sqft', '-s', help='Square footage')
    parser.add_argument('--lot-size', '-l', help='Lot size')
    parser.add_argument('--bedrooms', '-b', help='Bedrooms')
    parser.add_argument('--bathrooms', '-ba', help='Bathrooms')
    parser.add_argument('--land-value', help='Land value')
    parser.add_argument('--improvement-value', help='Improvement value')
    parser.add_argument('--total-value', '-v', help='Total appraised value')
    parser.add_argument('--street-view', help='Path to street view image')
    parser.add_argument('--map-view', help='Path to map view image')
    parser.add_argument('--output', '-o', required=True, help='Output PDF path')
    
    args = parser.parse_args()
    
    # Build data dict
    data = {
        'address': args.address,
        'prop_id': args.prop_id,
        'owner1_name': args.owner1,
        'owner2_name': args.owner2,
        'mailing_address': args.mailing_address,
        'year_built': args.year,
        'sqft': args.sqft,
        'lot_size': args.lot_size,
        'bedrooms': args.bedrooms,
        'bathrooms': args.bathrooms,
        'land_value': args.land_value,
        'improvement_value': args.improvement_value,
        'total_value': args.total_value,
    }
    
    # Convert images to base64
    street_view_b64 = image_to_base64(args.street_view) if args.street_view else None
    map_view_b64 = image_to_base64(args.map_view) if args.map_view else None
    
    # Generate HTML
    html_content = generate_html_report(data, street_view_b64, map_view_b64)
    
    # Write PDF
    HTML(string=html_content).write_pdf(args.output)
    print(f"PDF generated: {args.output}")

if __name__ == '__main__':
    main()
