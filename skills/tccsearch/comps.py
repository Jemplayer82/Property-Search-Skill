#!/usr/bin/env python3
"""
Pull comparable sales from Travis CAD for a given subdivision/neighborhood.
Usage: python3 comps.py --subdivision "Park at Blackhawk" [--drive-folder <id>] [--subject-pid 550733]

Scrapes the TCAD property search filtered by subdivision, extracts recent sales,
and outputs a markdown comps report uploaded to Drive.

Requires: websocket-client, gog
"""
import argparse, json, os, subprocess, sys, time, urllib.request
import websocket

CDP_HTTP = "http://127.0.0.1:18792"
BASE_URL = "https://travis.prodigycad.com"

def get_ws_url():
    tabs = json.loads(urllib.request.urlopen(f"{CDP_HTTP}/json").read())
    pages = [t for t in tabs if t["type"] == "page"]
    if not pages:
        raise RuntimeError("No tab found. Is Chrome relay active?")
    return pages[0]["wsUrl"]

def cdp(ws, method, params=None, timeout=20):
    mid = int(time.time() * 1000) % 99999
    ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
    deadline = time.time() + timeout
    while time.time() < deadline:
        ws.settimeout(min(2, deadline - time.time()))
        try:
            msg = json.loads(ws.recv())
            if msg.get("id") == mid:
                return msg.get("result", {})
        except websocket.WebSocketTimeoutException:
            pass
    raise TimeoutError(f"Timeout: {method}")

def js(ws, expr, timeout=15):
    r = cdp(ws, "Runtime.evaluate", {
        "expression": expr, "awaitPromise": True, "returnByValue": True
    }, timeout)
    return r.get("result", {}).get("value")

def navigate(ws, url, settle=4):
    cdp(ws, "Page.navigate", {"url": url})
    time.sleep(settle)

def search_subdivision(ws, subdivision):
    """Search TCAD by subdivision name, return list of property records."""
    print(f"  Searching subdivision: {subdivision}")
    navigate(ws, f"{BASE_URL}/property-search", settle=5)

    # Switch to subdivision search if available, else use general search
    switched = js(ws, f"""
        var tabs = Array.from(document.querySelectorAll('button, a, [role="tab"]'));
        var subdTab = tabs.find(t => /subdivision/i.test(t.textContent));
        if (subdTab) {{ subdTab.click(); return true; }}
        return false;
    """)
    if switched:
        time.sleep(1)

    js(ws, f"""
        var inputs = Array.from(document.querySelectorAll('input'));
        var inp = inputs.find(i => /subdivision|search/i.test(i.placeholder || i.id || i.name));
        if (!inp) inp = inputs[0];
        if (inp) {{
            inp.value = {json.dumps(subdivision)};
            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            inp.dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
    """)
    time.sleep(1)

    js(ws, """
        var btn = Array.from(document.querySelectorAll('button')).find(b => /search/i.test(b.textContent));
        if (btn) btn.click();
        else document.querySelector('input')?.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter',keyCode:13,bubbles:true}));
    """)
    time.sleep(5)

    # Collect results (up to 100 rows)
    rows_json = js(ws, """
        JSON.stringify(Array.from(document.querySelectorAll('table tr, [class*="row"], [class*="result"]')).slice(1, 101).map(row => {
            var cells = row.querySelectorAll('td, [class*="cell"]');
            var link = row.querySelector('a[href*="property-detail"]');
            var pid = link ? link.href.match(/property-detail\/(\d+)/)?.[1] : null;
            if (cells.length < 2 && !pid) return null;
            return {
                pid: pid,
                text: row.textContent.trim().substring(0, 300),
                href: link ? link.href : null
            };
        }).filter(r => r && r.pid))
    """)

    return json.loads(rows_json) if rows_json else []

def fetch_property_data(ws, pid):
    """Load a single property detail page and extract comps-relevant data."""
    navigate(ws, f"{BASE_URL}/property-detail/{pid}", settle=4)

    data = js(ws, """
        var text = document.body.innerText;
        // Extract key fields from rendered page text
        function extract(pattern) {
            var m = text.match(pattern);
            return m ? m[1].trim() : null;
        }
        JSON.stringify({
            pid: window.location.href.match(/property-detail\/(\d+)/)?.[1],
            address: document.querySelector('[class*="situs"],[class*="address"],h1')?.textContent?.trim(),
            owner: extract(/Owner[:\s]+([^\n]+)/i),
            appraisedValue: extract(/Appraised Value[:\s]+\$?([\d,]+)/i),
            marketValue: extract(/Market Value[:\s]+\$?([\d,]+)/i),
            landValue: extract(/Land Value[:\s]+\$?([\d,]+)/i),
            sqft: extract(/(?:Living Area|Sq ?Ft)[:\s]+([\d,]+)/i),
            yearBuilt: extract(/Year Built[:\s]+(\d{4})/i),
            bedrooms: extract(/Bed(?:rooms?)?[:\s]+(\d+)/i),
            bathrooms: extract(/Bath(?:rooms?)?[:\s]+(\d+)/i),
            subdivision: extract(/Subdivision[:\s]+([^\n]+)/i),
            saleDate: extract(/Sale Date[:\s]+([^\n]+)/i),
            salePrice: extract(/Sale Price[:\s]+\$?([\d,]+)/i),
            url: window.location.href
        })
    """)
    return json.loads(data) if data else {"pid": pid}

def generate_markdown_report(subject, comps, subdivision):
    """Generate a comps analysis markdown report."""
    from datetime import date
    today = date.today().strftime("%Y-%m-%d")

    lines = [
        f"# Comps Analysis — {subdivision}",
        f"**Generated:** {today}",
        "",
    ]

    if subject:
        lines += [
            "## Subject Property",
            f"- **Address:** {subject.get('address', 'N/A')}",
            f"- **PID:** {subject.get('pid', 'N/A')}",
            f"- **Owner:** {subject.get('owner', 'N/A')}",
            f"- **Appraised Value:** {subject.get('appraisedValue') or subject.get('marketValue', 'N/A')}",
            f"- **Living Area:** {subject.get('sqft', 'N/A')} sqft",
            f"- **Year Built:** {subject.get('yearBuilt', 'N/A')}",
            f"- **URL:** {subject.get('url', '')}",
            "",
        ]

    lines += [
        f"## Comparable Properties ({len(comps)} found)",
        "",
        "| PID | Address | Appraised | Market | Sqft | Yr Built | Sale Date | Sale Price |",
        "|-----|---------|-----------|--------|------|----------|-----------|------------|",
    ]

    for c in comps:
        lines.append(
            f"| {c.get('pid','?')} "
            f"| {(c.get('address') or 'N/A')[:40]} "
            f"| {c.get('appraisedValue') or '-'} "
            f"| {c.get('marketValue') or '-'} "
            f"| {c.get('sqft') or '-'} "
            f"| {c.get('yearBuilt') or '-'} "
            f"| {c.get('saleDate') or '-'} "
            f"| {c.get('salePrice') or '-'} |"
        )

    # Summary stats
    vals = [int(c['appraisedValue'].replace(',','')) for c in comps
            if c.get('appraisedValue') and c['appraisedValue'].replace(',','').isdigit()]
    if vals:
        lines += [
            "",
            "## Summary Statistics",
            f"- **Count:** {len(vals)}",
            f"- **Min Appraised:** ${min(vals):,}",
            f"- **Max Appraised:** ${max(vals):,}",
            f"- **Avg Appraised:** ${sum(vals)//len(vals):,}",
            f"- **Median Appraised:** ${sorted(vals)[len(vals)//2]:,}",
        ]

    lines += ["", "---", f"*Source: travis.prodigycad.com | {today}*"]
    return "\n".join(lines)

def upload_to_drive(local_path, name, folder_id, mime="text/plain"):
    result = subprocess.run(
        ["gog", "drive", "upload", local_path,
         "--name", name, "--parent", folder_id,
         "--mime-type", mime, "--plain"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed: {result.stderr}")
    for line in result.stdout.splitlines():
        if "drive.google.com" in line:
            return line.split()[-1]
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="Travis CAD comps puller")
    parser.add_argument("--subdivision", default="Park at Blackhawk",
                        help="Subdivision name to search")
    parser.add_argument("--subject-pid", help="PID of subject property for comparison")
    parser.add_argument("--max-comps", type=int, default=30,
                        help="Max comparable properties to pull details for")
    parser.add_argument("--drive-folder", help="Google Drive folder ID")
    parser.add_argument("--out-dir", default="/tmp")
    parser.add_argument("--skip-detail", action="store_true",
                        help="Skip per-property detail pages (faster, less data)")
    args = parser.parse_args()

    ws = websocket.create_connection(get_ws_url(), timeout=20)
    cdp(ws, "Page.enable")

    try:
        # Get subject property if requested
        subject = None
        if args.subject_pid:
            print(f"[1/3] Loading subject property PID {args.subject_pid}...")
            subject = fetch_property_data(ws, args.subject_pid)
            print(f"  Address: {subject.get('address', 'N/A')}")

        # Search subdivision
        print(f"[2/3] Searching '{args.subdivision}'...")
        rows = search_subdivision(ws, args.subdivision)
        print(f"  Found {len(rows)} results")

        # Fetch detail for each comp (skip subject)
        comps = []
        if not args.skip_detail:
            targets = [r for r in rows if r.get('pid') != args.subject_pid][:args.max_comps]
            print(f"[3/3] Fetching detail for {len(targets)} comps...")
            for i, row in enumerate(targets, 1):
                print(f"  [{i}/{len(targets)}] PID {row['pid']}...", end=" ", flush=True)
                try:
                    detail = fetch_property_data(ws, row['pid'])
                    comps.append(detail)
                    print(detail.get('appraisedValue') or detail.get('address', 'ok'))
                except Exception as e:
                    print(f"ERROR: {e}")
                    comps.append({"pid": row['pid']})
        else:
            print(f"[3/3] Skipping detail (--skip-detail)")
            comps = [{"pid": r["pid"], "address": r.get("text", "")[:60]} for r in rows[:args.max_comps]]

        # Generate report
        report = generate_markdown_report(subject, comps, args.subdivision)
        safe_sub = args.subdivision.replace(" ", "_")
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        md_name = f"Comps_{safe_sub}_{today}.md"
        md_path = os.path.join(args.out_dir, md_name)
        with open(md_path, "w") as f:
            f.write(report)
        print(f"\nReport saved: {md_path}")

        if args.drive_folder:
            link = upload_to_drive(md_path, md_name, args.drive_folder, mime="text/plain")
            print(f"Uploaded → {link}")
        else:
            print("\n" + report[:1000])

    finally:
        ws.close()

if __name__ == "__main__":
    main()
