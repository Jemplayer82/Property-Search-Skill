#!/usr/bin/env python3
"""
Owner contact info lookup via SearXNG + page scraping.
Usage: python3 owner_lookup.py "Ferguson Landon Jennifer" "3524 Winding Shore Lane Pflugerville TX"
         [--drive-folder <id>] [--out-dir /tmp]

Strategy:
  1. Search SearXNG for owner name + city → get result URLs
  2. Prioritize people-search sites (Spokeo, Whitepages, Veripages, FastPeopleSearch, etc.)
  3. Scrape each for phone/email/address
  4. De-dupe and score by confidence
  5. Output markdown report → optionally upload to Drive

Requires: requests, beautifulsoup4, gog
"""
import argparse, json, os, re, subprocess, sys, time
from datetime import date
from urllib.parse import quote_plus

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4",
                    "-q", "--break-system-packages"])
    import requests
    from bs4 import BeautifulSoup

SEARXNG = "http://192.168.7.17:8888"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# People-search sites we know how to parse (priority order)
PEOPLE_SITES = [
    "fastpeoplesearch.com",
    "whitepages.com",
    "spokeo.com",
    "veripages.com",
    "truepeoplesearch.com",
    "beenverified.com",
    "intelius.com",
    "peoplefinders.com",
    "radaris.com",
    "411.com",
]

def searxng_search(query, max_results=15):
    """Search SearXNG JSON API, return list of {title, url, snippet}."""
    try:
        r = requests.get(f"{SEARXNG}/search",
                         params={"q": query, "format": "json", "language": "en-US"},
                         headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [
            {"url": res["url"], "title": res.get("title",""), "snippet": res.get("content","")}
            for res in data.get("results", [])[:max_results]
        ]
    except Exception as e:
        print(f"  SearXNG error: {e}")
        return []

def scrape_page(url, timeout=8):
    """Fetch a page and return BeautifulSoup, or None on failure."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
    except Exception:
        pass
    return None

def extract_phones(text):
    """Extract US phone numbers from text."""
    raw = re.findall(r'\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}', text)
    normalized = []
    for p in raw:
        digits = re.sub(r'\D', '', p)
        if len(digits) == 10:
            normalized.append(f"({digits[:3]}) {digits[3:6]}-{digits[6:]}")
    return list(dict.fromkeys(normalized))  # de-dupe preserving order

def extract_emails(text):
    """Extract email addresses from text."""
    emails = re.findall(r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b', text)
    # Filter out common false positives
    skip = {'example.com', 'domain.com', 'email.com', 'test.com'}
    return list(dict.fromkeys(
        e.lower() for e in emails
        if not any(s in e.lower() for s in skip)
    ))

def extract_addresses(text):
    """Extract street addresses from text."""
    patterns = [
        r'\d{3,5}\s+[A-Z][a-zA-Z\s]+(?:Lane|Ln|Drive|Dr|Street|St|Avenue|Ave|Road|Rd|Way|Blvd|Circle|Ct|Court|Trail|Trl)\b[^,\n]{0,30}',
        r'\d{3,5}\s+[A-Z][a-zA-Z\s]{3,30}(?:,\s*[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\s*\d{5})',
    ]
    found = []
    for pat in patterns:
        found += re.findall(pat, text)
    return list(dict.fromkeys(f.strip() for f in found))[:5]

def scrape_people_site(url, soup, owner_name):
    """Generic scraper for people-search sites."""
    if not soup:
        return {}
    text = soup.get_text(separator=" ", strip=True)

    # Check if it's a paywall/signup page
    paywall_signals = ["sign up", "create account", "subscribe", "unlock", "premium", "log in to view"]
    is_paywalled = sum(1 for s in paywall_signals if s in text.lower()) >= 2

    result = {
        "url": url,
        "paywalled": is_paywalled,
        "phones": extract_phones(text),
        "emails": extract_emails(text),
        "addresses": extract_addresses(text),
        "raw_snippet": text[:500] if not is_paywalled else "[paywalled]",
    }

    # Try to pull structured data from common patterns
    # Age
    age_m = re.search(r'\b(?:age|aged?)[\s:]+(\d{2})\b', text, re.I)
    if age_m:
        result["age"] = age_m.group(1)

    # Relatives / associates
    relatives = re.findall(r'(?:Related to|Associates?|Also known as)[:\s]+([A-Z][a-zA-Z\s,]+?)(?:\.|$)', text)
    if relatives:
        result["relatives"] = relatives[0][:100]

    return result

def score_result(r):
    """Score a result by usefulness."""
    score = 0
    if r.get("phones"): score += len(r["phones"]) * 10
    if r.get("emails"): score += len(r["emails"]) * 8
    if r.get("addresses"): score += len(r["addresses"]) * 3
    if r.get("paywalled"): score -= 5
    return score

def generate_report(owner_name, address, results, search_results):
    today = date.today().strftime("%Y-%m-%d")
    lines = [
        f"# Owner Contact Research — {owner_name}",
        f"**Property:** {address}",
        f"**Generated:** {today}",
        f"**Method:** SearXNG + public records scraping",
        "",
    ]

    # Aggregate all found contact info
    all_phones = []
    all_emails = []
    all_addresses = []

    for r in results:
        all_phones += r.get("phones", [])
        all_emails += r.get("emails", [])
        all_addresses += r.get("addresses", [])

    # De-dupe
    all_phones = list(dict.fromkeys(all_phones))
    all_emails = list(dict.fromkeys(all_emails))
    all_addresses = list(dict.fromkeys(all_addresses))

    lines += ["## Contact Summary", ""]
    if all_phones:
        lines.append("### Phone Numbers")
        for p in all_phones:
            lines.append(f"- {p}")
        lines.append("")
    if all_emails:
        lines.append("### Email Addresses")
        for e in all_emails:
            lines.append(f"- {e}")
        lines.append("")
    if all_addresses:
        lines.append("### Known Addresses")
        for a in all_addresses:
            lines.append(f"- {a}")
        lines.append("")

    if not any([all_phones, all_emails, all_addresses]):
        lines.append("*No direct contact info found in public records (likely paywalled).*\n")

    # Search result links for manual follow-up
    lines += ["## Search Results (Manual Follow-up)", ""]
    for r in search_results[:15]:
        site = re.sub(r'https?://(www\.)?', '', r["url"]).split("/")[0]
        lines.append(f"- **[{r['title'][:60]}]({r['url']})**")
        if r.get("snippet"):
            lines.append(f"  > {r['snippet'][:120]}")
    lines.append("")

    # Per-source detail
    scraped = [r for r in results if not r.get("paywalled") and score_result(r) > 0]
    if scraped:
        lines += ["## Source Detail", ""]
        for r in sorted(scraped, key=score_result, reverse=True):
            lines.append(f"### {r['url'][:80]}")
            if r.get("phones"):
                lines.append(f"- Phones: {', '.join(r['phones'])}")
            if r.get("emails"):
                lines.append(f"- Emails: {', '.join(r['emails'])}")
            if r.get("addresses"):
                lines.append(f"- Addresses: {'; '.join(r['addresses'][:2])}")
            if r.get("age"):
                lines.append(f"- Age: {r['age']}")
            if r.get("relatives"):
                lines.append(f"- Associates: {r['relatives']}")
            lines.append("")

    lines += ["---", f"*Source: Public records via SearXNG | {today}*"]
    return "\n".join(lines)

def upload_to_drive(path, name, folder_id):
    result = subprocess.run(
        ["gog", "drive", "upload", path,
         "--name", name, "--parent", folder_id,
         "--mime-type", "text/plain", "--plain"],
        capture_output=True, text=True
    )
    for line in result.stdout.splitlines():
        if "drive.google.com" in line:
            return line.split()[-1]
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="Owner contact info lookup via SearXNG")
    parser.add_argument("owner", help="Owner name (e.g. 'Ferguson Landon Jennifer')")
    parser.add_argument("address", help="Property address")
    parser.add_argument("--drive-folder", help="Google Drive folder ID")
    parser.add_argument("--out-dir", default="/tmp")
    parser.add_argument("--max-scrape", type=int, default=5,
                        help="Max people-search sites to scrape (default: 5)")
    args = parser.parse_args()

    city_state = " ".join(args.address.split()[2:]) or "Texas"
    name_parts = args.owner.split()
    # TCAD owner format is "LastName FirstName Spouse" e.g. "Ferguson Landon Jennifer"
    # Build useful variants
    if len(name_parts) >= 3:
        last, first, spouse = name_parts[0], name_parts[1], name_parts[2]
        name_v1 = f"{first} {last}"          # "Landon Ferguson"
        name_v2 = f"{spouse} {last}"         # "Jennifer Ferguson"
        name_v3 = f"{first} & {spouse} {last}"  # "Landon & Jennifer Ferguson"
    elif len(name_parts) == 2:
        last, first = name_parts[0], name_parts[1]
        name_v1 = f"{first} {last}"
        name_v2 = f"{last} {first}"
        name_v3 = name_v1
    else:
        name_v1 = name_v2 = name_v3 = args.owner

    # Use the least-common name first for tighter targeting
    # If multiple names given (e.g. "Ferguson Landon Jennifer"), pick the rarest first name
    street_num = args.address.split()[0]
    street_name = args.address.split()[1] if len(args.address.split()) > 1 else ""

    city = city_state.split()[0]  # e.g. "Pflugerville"
    state = city_state.split()[1] if len(city_state.split()) > 1 else "TX"
    queries = [
        f'{name_v1} {city} {state} phone',
        f'{name_v1} {city} Texas address contact',
        f'{name_v1} {street_num} {street_name} {city}',
        f'{name_v2} {city} {state} phone',
    ]

    print(f"Owner: {args.owner}")
    print(f"Property: {args.address}")
    print(f"SearXNG: {SEARXNG}\n")

    all_search_results = []
    for q in queries:
        print(f"Searching: {q[:70]}...")
        results = searxng_search(q, max_results=10)
        print(f"  → {len(results)} results")
        all_search_results += results
        time.sleep(3)  # respect engine rate limits

    # De-dupe by URL
    seen = set()
    unique_results = []
    for r in all_search_results:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique_results.append(r)

    print(f"\nTotal unique results: {len(unique_results)}")

    # Prioritize people-search sites
    priority = [r for r in unique_results
                if any(s in r["url"] for s in PEOPLE_SITES)]
    other = [r for r in unique_results
             if not any(s in r["url"] for s in PEOPLE_SITES)]

    targets = (priority + other)[:args.max_scrape]

    # Scrape each target
    scraped = []
    print(f"\nScraping {len(targets)} pages...")
    for r in targets:
        print(f"  {r['url'][:80]}...", end=" ", flush=True)
        soup = scrape_page(r["url"])
        if soup:
            info = scrape_people_site(r["url"], soup, args.owner)
            info["title"] = r["title"]
            scraped.append(info)
            score = score_result(info)
            status = "paywalled" if info.get("paywalled") else f"score={score}"
            phones = len(info.get("phones", []))
            print(f"[{status}, {phones} phones]")
        else:
            print("[failed]")
        time.sleep(0.3)

    # Generate report
    report = generate_report(args.owner, args.address, scraped, unique_results)

    safe_owner = re.sub(r'\W+', '_', args.owner.split()[0])
    today = date.today().strftime("%Y-%m-%d")
    md_name = f"Owner_Lookup_{safe_owner}_{today}.md"
    md_path = os.path.join(args.out_dir, md_name)

    with open(md_path, "w") as f:
        f.write(report)
    print(f"\nReport saved: {md_path}")

    if args.drive_folder:
        link = upload_to_drive(md_path, md_name, args.drive_folder)
        print(f"Uploaded → {link}")

    # Print summary
    print("\n" + "="*50)
    for line in report.split("\n")[:30]:
        print(line)

if __name__ == "__main__":
    main()
