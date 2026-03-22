#!/usr/bin/env python3
"""
Quick site availability check — call assert_site_up() before scraping to avoid
hammering sites that are down or in maintenance mode.

Usage:
    from site_check import assert_site_up, check_site

    assert_site_up("Travis CAD", "https://travis.prodigycad.com")  # exits on failure
    up, reason = check_site("https://tccsearch.org")                # non-fatal check
"""
import requests

MAINTENANCE_PATTERNS = [
    "down for maintenance",
    "temporarily unavailable",
    "we'll be back",
    "we are currently down",
    "system maintenance",
    "under maintenance",
    "scheduled maintenance",
    "site is temporarily",
    "planned maintenance",
    "service disruption",
    "503 service",
    "502 bad gateway",
]

_STATUS_MESSAGES = {
    429: "rate limited (HTTP 429) — back off and try later",
    500: "internal server error (HTTP 500)",
    502: "bad gateway (HTTP 502) — likely down or behind a broken proxy",
    503: "service unavailable (HTTP 503) — maintenance or overloaded",
    504: "gateway timeout (HTTP 504)",
}

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0 Safari/537.36",
}


def check_site(url, timeout=6):
    """
    Quick availability check — one streaming GET, reads first 4KB only.
    Returns (is_up: bool, reason: str).
    """
    try:
        r = requests.get(url, headers=_HEADERS, timeout=timeout,
                         allow_redirects=True, stream=True)

        if r.status_code in _STATUS_MESSAGES:
            return False, _STATUS_MESSAGES[r.status_code]
        if r.status_code >= 500:
            return False, f"server error (HTTP {r.status_code})"

        # Peek at first 4KB for maintenance page text
        if r.status_code == 200:
            try:
                chunk = next(r.iter_content(4096), b"").decode("utf-8", errors="ignore").lower()
                for pattern in MAINTENANCE_PATTERNS:
                    if pattern in chunk:
                        return False, f"maintenance page detected ('{pattern}')"
            except Exception:
                pass  # body check is best-effort

        return True, "ok"

    except requests.exceptions.ConnectionError:
        return False, "connection refused — site appears to be down"
    except requests.exceptions.Timeout:
        return False, f"no response in {timeout}s — site not responding"
    except Exception as e:
        return False, f"check failed: {e}"


def assert_site_up(name, url, timeout=6):
    """
    Check a site and raise SystemExit with a clear message if it's unavailable.
    Prints a one-line status so callers can see what's happening.

    Call at the top of each script before any real work starts.
    """
    print(f"  Checking {name} ... ", end="", flush=True)
    up, reason = check_site(url, timeout=timeout)
    if up:
        print("ok")
    else:
        print(f"DOWN")
        raise SystemExit(
            f"\n[SKIP] {name} ({url}) is not available:\n"
            f"  {reason}\n"
            f"Not proceeding — will not hammer an unavailable site."
        )
    return True
