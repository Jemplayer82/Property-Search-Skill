#!/usr/bin/env python3
"""
tccsearch.org deed search — pulls all docs for an address and downloads PDFs.
Usage: python3 deed_search.py "3524 Winding Shore" --drive-folder <folderID>
Requires: requests, websocket-client, gog (for Drive upload)
"""
import argparse, json, os, subprocess, sys, time, urllib.parse
import requests, websocket

CDP_URL = "http://127.0.0.1:18800"  # OpenClaw browser relay CDP port

def get_tab():
    tabs = requests.get(f"{CDP_URL}/json").json()
    pages = [t for t in tabs if t["type"] == "page"]
    if not pages:
        raise RuntimeError("No browser tab found. Make sure Chrome relay is active.")
    tab = pages[0]
    tab["wsUrl"] = tab.get("webSocketDebuggerUrl", tab.get("wsUrl"))
    return tab

def cdp(ws, method, params=None, timeout=15):
    msg_id = int(time.time() * 1000) % 99999
    ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    deadline = time.time() + timeout
    while time.time() < deadline:
        raw = ws.recv()
        msg = json.loads(raw)
        if msg.get("id") == msg_id:
            if "error" in msg:
                raise RuntimeError(f"CDP error: {msg['error']}")
            return msg.get("result", {})
    raise TimeoutError(f"CDP timeout waiting for {method}")

def js(ws, expr, timeout=15):
    r = cdp(ws, "Runtime.evaluate", {"expression": expr, "awaitPromise": True, "returnByValue": True}, timeout)
    val = r.get("result", {})
    if val.get("type") == "undefined":
        return None
    return val.get("value")

def navigate(ws, url, wait=2):
    cdp(ws, "Page.navigate", {"url": url})
    time.sleep(wait)

def search_address(ws, address):
    """Full search flow — returns list of {instrument, doc_type, date, global_id}"""
    print(f"[1/4] Navigating to tccsearch.org...")
    navigate(ws, "https://tccsearch.org/RealEstate/SearchEntry.aspx", wait=3)

    # Click Address tab
    print(f"[2/4] Switching to Address search...")
    js(ws, "Array.from(document.querySelectorAll('a,span,td')).find(el => el.textContent.trim() === 'Address')?.click()")
    time.sleep(1)

    # Fill address
    print(f"[3/4] Filling address: {address}")
    js(ws, f"""
        var inp = document.getElementById('cphNoMargin_f_txtLDStreetAddress');
        if (!inp) inp = document.querySelector('input[id*=\"StreetAddress\"]');
        inp.value = {json.dumps(address)};
        inp.dispatchEvent(new Event('change', {{bubbles: true}}));
    """)
    time.sleep(0.5)

    # Click search (Legal Description section button)
    js(ws, """
        var btns = Array.from(document.querySelectorAll('input[value="Search"]'));
        (btns[1] || btns[0])?.click();
    """)
    print(f"[4/4] Waiting for results...")
    time.sleep(4)

    # Parse results
    rows = js(ws, """
        JSON.stringify(Array.from(document.querySelectorAll('table tr')).slice(1).map(tr => {
            var cells = tr.querySelectorAll('td');
            if (cells.length < 5) return null;
            var link = tr.querySelector('a');
            var href = link ? link.href : '';
            var global_id = href.match(/global_id=([^&]+)/)?.[1] || '';
            return {
                instrument: cells[0]?.textContent?.trim(),
                doc_type: cells[2]?.textContent?.trim(),
                date: cells[1]?.textContent?.trim(),
                global_id: global_id
            };
        }).filter(r => r && r.global_id));
    """)
    return json.loads(rows) if rows else []

def download_pdf(ws, global_id, out_path):
    """Navigate to doc image page, click Get Image Now, save PDF."""
    navigate(ws, f"https://tccsearch.org/RealEstate/SearchImage.aspx?global_id={global_id}&type=img", wait=3)

    # Click Get Image Now inside iframe
    js(ws, """
        var doc = document.querySelector('iframe')?.contentDocument;
        if (doc) {
            var btn = doc.getElementById('btnProcessNow');
            if (btn) { btn.disabled = false; btn.click(); }
        }
    """)
    time.sleep(4)

    # Now on printHelper page — use CDP Page.printToPDF
    result = cdp(ws, "Page.printToPDF", {
        "printBackground": True,
        "paperWidth": 8.5,
        "paperHeight": 11,
    }, timeout=30)
    import base64
    pdf_bytes = base64.b64decode(result["data"])
    with open(out_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"  Saved {len(pdf_bytes)//1024}KB → {out_path}")
    return out_path

def upload_to_drive(pdf_path, name, folder_id):
    """Upload PDF to Google Drive folder via gog."""
    result = subprocess.run(
        ["gog", "drive", "upload", pdf_path,
         "--name", name,
         "--parent", folder_id,
         "--mime-type", "application/pdf",
         "--plain"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"gog upload failed: {result.stderr}")
    # Parse link from output
    for line in result.stdout.splitlines():
        if "drive.google.com" in line:
            return line.split()[-1]
    return result.stdout.strip()

def main():
    parser = argparse.ArgumentParser(description="tccsearch.org deed PDF downloader")
    parser.add_argument("address", help="Street address to search (e.g. '3524 Winding Shore')")
    parser.add_argument("--drive-folder", help="Google Drive folder ID to upload PDFs")
    parser.add_argument("--doc-types", default="Deed of Trust,Warranty Deed",
                        help="Comma-separated doc types to grab (default: Deed of Trust,Warranty Deed)")
    parser.add_argument("--out-dir", default="/tmp", help="Local output directory")
    args = parser.parse_args()

    want_types = {t.strip().lower() for t in args.doc_types.split(",")}

    tab = get_tab()
    ws_url = tab["wsUrl"]
    print(f"Connected to tab: {tab['title']} ({tab['url']})")

    ws = websocket.create_connection(ws_url, timeout=20)
    cdp(ws, "Page.enable")

    try:
        rows = search_address(ws, args.address)
        print(f"\nFound {len(rows)} results total.")

        matches = [r for r in rows if r["doc_type"].lower() in want_types]
        print(f"Matching doc types: {len(matches)}\n")

        for r in matches:
            safe_name = f"{r['doc_type'].replace(' ','_')}_{r['instrument']}_{args.address.replace(' ','_')}.pdf"
            out_path = os.path.join(args.out_dir, safe_name)
            print(f"Downloading: {r['doc_type']} | {r['instrument']} | {r['date']}")
            try:
                download_pdf(ws, r["global_id"], out_path)
                if args.drive_folder:
                    link = upload_to_drive(out_path, safe_name, args.drive_folder)
                    print(f"  Uploaded → {link}")
            except Exception as e:
                print(f"  ERROR: {e}")

    finally:
        ws.close()

if __name__ == "__main__":
    main()
