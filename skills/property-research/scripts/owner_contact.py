#!/usr/bin/env python3
"""
Search for owner contact information using web sources.
Generates structured contact info for property research.
"""

import sys
import json

def format_owner_info(name, age=None, phones=None, emails=None, addresses=None, relatives=None):
    """Format owner contact information in a standard way"""
    info = {
        "name": name,
        "age": age,
        "phones": phones or [],
        "emails": emails or [],
        "addresses": addresses or [],
        "relatives": relatives or []
    }
    return info

def generate_markdown_contact(owner1, owner2=None, property_address=None, prop_id=None):
    """Generate markdown content for owner contact document"""
    
    content = f"""# Owner Contact Information
## {property_address or 'Property Address'}
*Generated via Property Research Skill*

---

## Property Photo
[See Google Maps Street View image in Drive folder]

**Google Maps:** https://www.google.com/maps/search/{property_address.replace(' ', '+') if property_address else ''}

---

## Property Owners
**{owner1['name']}**{f" & **{owner2['name']}**" if owner2 else ""}

---

## Contact Information

### {owner1['name']}{f" (Age {owner1['age']})" if owner1.get('age') else ""}
"""
    
    if owner1.get('phones'):
        for i, phone in enumerate(owner1['phones'], 1):
            label = "Mobile" if i == 1 else "Alternate"
            content += f"- **Phone ({label}):** {phone}\n"
    
    if owner1.get('emails'):
        for email in owner1['emails'][:3]:  # Limit to first 3 emails
            content += f"- **Email:** {email}\n"
    
    if owner1.get('age'):
        content += f"- **Date of Birth:** {owner1['age']}\n"
    
    if owner2:
        content += f"\n### {owner2['name']}{f" (Age {owner2['age']})" if owner2.get('age') else ""}\n"
        
        if owner2.get('phones'):
            for i, phone in enumerate(owner2['phones'], 1):
                content += f"- **Phone:** {phone}\n"
        
        if owner2.get('emails'):
            for email in owner2['emails'][:2]:
                content += f"- **Email:** {email}\n"
    
    content += f"""
---

## Property Details
- **Address:** {property_address or 'N/A'}
- **TCAD PropID:** {prop_id or 'N/A'}

---

## Sources
- NationalPublicData.com
- FastBackgroundCheck.com
- ThatsThem.com
- Travis Central Appraisal District (TCAD)
"""
    
    return content

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: owner_contact.py <owner_name> [property_address] [prop_id]")
        print("Example: owner_contact.py 'Landon Ferguson' '3524 Winding Shore Lane, Pflugerville, TX' 550733")
        sys.exit(1)
    
    owner_name = sys.argv[1]
    property_address = sys.argv[2] if len(sys.argv) > 2 else None
    prop_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Create owner info structure
    owner = {"name": owner_name, "phones": [], "emails": []}
    
    # Generate markdown
    markdown = generate_markdown_contact(owner, None, property_address, prop_id)
    print(markdown)

if __name__ == "__main__":
    main()
