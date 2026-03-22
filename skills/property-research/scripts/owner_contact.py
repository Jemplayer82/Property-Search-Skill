#!/usr/bin/env python3
"""
Generate owner contact document from research data.
Creates markdown content for Google Docs.
"""

import sys
import json
import re

def sanitize_filename(text):
    """Create safe filename from address"""
    return re.sub(r'[^\w\s-]', '', text).strip().replace(' ', '_')

def generate_markdown_contact(owner1, owner2=None, property_address=None, prop_id=None,
                               appraisal_value=None, year_built=None, sqft=None):
    """Generate markdown content for owner contact document"""
    
    # Build Google Maps search URL
    maps_query = property_address.replace(' ', '+') if property_address else ''
    
    content = f"""# Owner Contact Information

## {property_address or 'Property Address'}

*Generated via Property Research Skill*

---

## Property Photo
![Street View](PLACEHOLDER_STREET_VIEW_IMAGE)

**[View on Google Maps](https://www.google.com/maps/search/{maps_query})**

---

## Property Owners
**{owner1.get('name', 'Unknown')}**{f" & **{owner2.get('name', 'Unknown')}**" if owner2 and owner2.get('name') else ""}

---

## Contact Information

### {owner1.get('name', 'Primary Owner')}{f" (Age {owner1.get('age')})" if owner1.get('age') else ""}
"""
    
    # Owner 1 phones
    if owner1.get('phones'):
        for i, phone in enumerate(owner1['phones'][:3], 1):
            label = "Mobile" if i == 1 else f"Alternate {i-1}"
            content += f"- **Phone ({label}):** {phone}\n"
    else:
        content += "- *No phone numbers found*\n"
    
    # Owner 1 emails
    if owner1.get('emails'):
        for email in owner1['emails'][:3]:
            content += f"- **Email:** {email}\n"
    
    # Owner 1 addresses
    if owner1.get('addresses'):
        content += "\n**Known Addresses:**\n"
        for addr in owner1['addresses'][:3]:
            content += f"- {addr}\n"
    
    # Owner 2
    if owner2 and owner2.get('name'):
        content += f"\n### {owner2['name']}{f" (Age {owner2.get('age')})" if owner2.get('age') else ""}\n\n"
        
        if owner2.get('phones'):
            for i, phone in enumerate(owner2['phones'][:2], 1):
                content += f"- **Phone:** {phone}\n"
        
        if owner2.get('emails'):
            for email in owner2['emails'][:2]:
                content += f"- **Email:** {email}\n"
    
    content += f"""
---

## Property Summary

| Field | Value |
|-------|-------|
| **Address** | {property_address or 'N/A'} |
| **TCAD PropID** | {prop_id or 'N/A'} |
| **2025 Appraisal** | {appraisal_value or 'N/A'} |
| **Year Built** | {year_built or 'N/A'} |
| **Square Footage** | {sqft or 'N/A'} |

---

## Search Sources
- [ ] NationalPublicData.com
- [ ] FastBackgroundCheck.com  
- [ ] ThatsThem.com
- [ ] WhitePages.com
- [ ] Texas Voter Records

---

## Notes
*Add research notes here...*

---

*Document generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    
    return content

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate owner contact document')
    parser.add_argument('owner1_name', help='Primary owner name')
    parser.add_argument('--owner2', '-o2', help='Secondary owner name')
    parser.add_argument('--address', '-a', help='Property address')
    parser.add_argument('--prop-id', '-p', help='TCAD PropID')
    parser.add_argument('--appraisal', help='Appraisal value')
    parser.add_argument('--year', '-y', help='Year built')
    parser.add_argument('--sqft', '-s', help='Square footage')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    # Build owner dicts
    owner1 = {"name": args.owner1_name}
    owner2 = {"name": args.owner2} if args.owner2 else None
    
    # Generate markdown
    markdown = generate_markdown_contact(
        owner1=owner1,
        owner2=owner2,
        property_address=args.address,
        prop_id=args.prop_id,
        appraisal_value=args.appraisal,
        year_built=args.year,
        sqft=args.sqft
    )
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(markdown)
        print(f"Saved to {args.output}")
    else:
        print(markdown)

if __name__ == "__main__":
    main()
