#!/usr/bin/env python3
"""
Travis CAD property lookup — scrapes property data and saves PDF to Drive.
Usage: python3 tcad_lookup.py "3524 Winding Shore Lane" [--pid 550733] [--drive-folder <id>]

Requires: requests, websocket-client, gog (Drive upload)
"""
import argparse, base64, json, os, subprocess, sys, time, urllib.request
import websocket

CDP_HTTP = "http://127.0.0.1:18792"
BASE_URL = "https://travis.prodigycad.com"
SEARCH_URL = f"{BASE_URL}/property-search"

def get_ws_url(auth_token):
    req = urllib.request.Request(f"{CDP_HTTP}/json",
                                  headers={"Authorization": f"Bearer {auth_token}"})
    tabs = json.loads(urllib.request.urlopen(req).read())
    pages = [t for t in tabs if t["type"] == "page"]
    if not pages:
        raise RuntimeError("No browser tab found.")
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
                if "error" in msg:
                    raise RuntimeError(f"CDP error: {msg['error']}")
                return msg.get("result", {})
        except websocket.WebSocketTimeoutException:
            pass
    raise TimeoutError(f"Timeout waiting for {method}")

def js(ws, expr, timeout=15):
    r = cdp(ws, "Runtime.evaluate", {
        "expression": expr, "awaitPromise": True, "returnByValue": True
    }, timeout)
    return r.get("result", {}).get("value")

def navigate_and_wait(ws, url, settle=3):
    cdp(ws, "Page.navigate", {"url": url})
    time.sleep(settle)

def search_by_address(ws, address):
    """Search TCAD by address, return PID."""
    print(f"  Searching TCAD for: {address}")
    navigate_and_wait(ws, SEARCH_URL, settle=4)

    # Fill search box and submit
    js(ws, f"""
        var inputs = document.querySelectorAll('input[type="text"], input[type="search"], input:not([type])');
        var inp = Array.from(inputs).find(i => i.placeholder && /address|search|account/i.test(i.placeholder));
        if (!inp) inp = inputs[0];
        if (inp) {{
            inp.value = {json.dumps(address)};
            inp.dispatchEvent(new Event('input', {{bubbles: true}}));
            inp.dispatchEvent(new Event('change', {{bubbles: true}}));
        }}
    """)
    time.sleep(1)

    # Hit enter or click search button
    js(ws, """
        var btn = Array.from(document.querySelectorAll('button')).find(b => /search/i.test(b.textContent));
        if (btn) btn.click();
        else document.querySelector('input[type="search"], input[type="text"]')?.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', keyCode:13, bubbles:true}));
    """)
    time.sleep(4)

    # Get the first result's PID from URL or from result list
    pid = js(ws, """
        // Try URL first
        var m = window.location.href.match(/property-detail\/(\d+)/);
        if (m) return m[1];
        // Try result links
        var link = document.querySelector('a[href*="property-detail"]');
        if (link) { var lm = link.href.match(/property-detail\/(\d+)/); if (lm) return lm[1]; }
        return null;
    """)

    if not pid:
        # May need to click first result
        js(ws, """
            var link = document.querySelector('a[href*="property-detail"]');
            if (link) link.click();
        """)
        time.sleep(3)
        pid = js(ws, "window.location.href.match(/property-detail\\/(\\d+)/)?.[1] || null")

    return pid

def load_property_detail(ws, pid):
    """Navigate to property detail page and extract key data."""
    print(f"  Loading property detail for PID {pid}...")
    navigate_and_wait(ws, f"{BASE_URL}/property-detail/{pid}", settle=5)

    data = js(ws, """
        JSON.stringify({
            address: (document.querySelector('[class*="situs"], [class*="address"], h1, h2') || {}).textContent?.trim(),
            owner: Array.from(document.querySelectorAll('*')).find(el => el.textContent.includes('Owner') && el.children.length < 3)?.nextElementSibling?.textContent?.trim(),
            appraisal: (() => {
                var els = Array.from(document.querySelectorAll('*'));
                var appr = els.find(el => /appraised|total value/i.test(el.textContent) && el.children.length < 3);
                return appr?.nextElementSibling?.textContent?.trim() || 
                       document.body.innerText.match(/\$[\d,]+/)?.join(', ');
            })(),
            pid: window.location.href.match(/property-detail\/(\d+)/)?.[1],
            url: window.location.href,
            title: document.title,
            bodyText: document.body.innerText.substring(0, 3000)
        })
    """)
    return json.loads(data) if data else {}

def save_pdf(ws, pid, out_path):
    """Print property detail page to PDF."""
    result = cdp(ws, "Page.printToPDF", {
        "printBackground": True,
        "paperWidth": 8.5,
        "paperHeight": 11,
        "marginTop": 0.4,
        "marginBottom": 0.4,
    }, timeout=30)
    pdf_bytes = base64.b64decode(result["data"])
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"  Saved PDF: {out_path} ({len(pdf_bytes)//1024}KB)")
    return out_path

def upload_to_drive(pdf_path, name, folder_id):
    result = subprocess.run(
        ["gog", "drive", "upload", pdf_path,
         "--name", name,
         "--parent", folder_id,
         "--mime-type", "application/pdf",
         "--plain"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Upload failed: {result.stderr}")
    for line in result.stdout.splitlines():
        if "drive.google.com" in line:
            return line.split()[-1]
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="Travis CAD property lookup + PDF to Drive")
    parser.add_argument("address", nargs="?", help="Street address")
    parser.add_argument("--pid", help="Known TCAD Property ID (skips search)")
    parser.add_argument("--drive-folder", help="Google Drive folder ID")
    parser.add_argument("--out-dir", default="/tmp")
    parser.add_argument("--auth-token", default=os.environ.get("OPENCLAW_TOKEN", ""),
                        help="OpenClaw gateway auth token ($OPENCLAW_TOKEN)")
    args = parser.parse_args()

    if not args.address and not args.pid:
        parser.error("Provide an address or --pid")

    ws_url = get_ws_url(args.auth_token) if args.auth_token else _get_ws_url_direct()
    ws = websocket.create_connection(ws_url, timeout=20)
    cdp(ws, "Page.enable")

    try:
        pid = args.pid
        if not pid:
            pid = search_by_address(ws, args.address)
            if not pid:
                print("ERROR: Could not find property. Check the address.")
                sys.exit(1)
            print(f"  Found PID: {pid}")

        detail = load_property_detail(ws, pid)
        print(f"\n--- Property Detail ---")
        print(f"  Address  : {detail.get('address', 'N/A')}")
        print(f"  Owner    : {detail.get('owner', 'N/A')}")
        print(f"  Appraisal: {detail.get('appraisal', 'N/A')}")
        print(f"  URL      : {detail.get('url', '')}")

        # Save PDF
        label = args.address or f"PID_{pid}"
        safe_label = label.replace(" ", "_").replace("/", "-")
        pdf_name = f"TCAD_{safe_label}_PID{pid}.pdf"
        pdf_path = os.path.join(args.out_dir, pdf_name)
        save_pdf(ws, pid, pdf_path)

        if args.drive_folder:
            link = upload_to_drive(pdf_path, pdf_name, args.drive_folder)
            print(f"  Uploaded → {link}")

        return detail

    finally:
        ws.close()

def _get_ws_url_direct():
    """Fallback: hit relay without auth (local-only)."""
    tabs = json.loads(urllib.request.urlopen(f"{CDP_HTTP}/json").read())
    pages = [t for t in tabs if t["type"] == "page"]
    if not pages:
        raise RuntimeError("No browser tab found.")
    return pages[0]["wsUrl"]

if __name__ == "__main__":
    main()
