#!/usr/bin/env python3
"""
Full property research runner — TCAD + Deed search + Comps in one shot.
Usage: python3 run_research.py "3524 Winding Shore Lane" --drive-parent <id>
       python3 run_research.py "3524 Winding Shore Lane" --drive-folder <id>

Runs:
  1. tcad_lookup.py   → TCAD tax/appraisal PDF → Drive
  2. deed_search.py   → Deed of Trust + Warranty Deed PDFs → Drive
  3. comps.py         → Comps report → Drive
  4. owner_lookup.py  → Owner contact info → Drive

If --drive-parent is given, a subfolder named after the address is auto-created.
If --drive-folder is given, files are uploaded directly to that folder.

Temp files are written to a dedicated working directory and cleaned up after
all uploads complete.
"""
import argparse, os, shutil, subprocess, sys, tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run(script, args_list):
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, script)] + args_list
    print(f"\n{'='*60}")
    print(f"Running: {script}")
    print(f"{'='*60}")
    result = subprocess.run(cmd)
    return result.returncode == 0

def create_drive_folder(name, parent_id=None):
    """Create a Google Drive folder and return its ID."""
    cmd = ["gog", "drive", "mkdir", name, "--plain"]
    if parent_id:
        cmd += ["--parent", parent_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create Drive folder: {result.stderr}")
    for line in result.stdout.splitlines():
        if line.startswith("id\t"):
            return line.split("\t")[1].strip()
    raise RuntimeError(f"Could not parse folder ID from: {result.stdout}")

def main():
    parser = argparse.ArgumentParser(description="Full property research suite")
    parser.add_argument("address", help="Full street address (e.g. '3524 Winding Shore Lane')")
    parser.add_argument("--pid", help="TCAD Property ID (skips TCAD search)")
    parser.add_argument("--drive-folder", help="Existing Google Drive folder ID to upload into")
    parser.add_argument("--drive-parent", help="Parent Drive folder ID — auto-creates a subfolder named after the address")
    parser.add_argument("--subdivision", default="Park at Blackhawk",
                        help="Subdivision for comps (default: Park at Blackhawk)")
    parser.add_argument("--owner", help="Owner name for contact lookup (e.g. 'Ferguson Landon Jennifer')")
    parser.add_argument("--skip-comps", action="store_true")
    parser.add_argument("--skip-deeds", action="store_true")
    parser.add_argument("--skip-tcad", action="store_true")
    parser.add_argument("--skip-owner", action="store_true")
    args = parser.parse_args()

    if not args.drive_folder and not args.drive_parent:
        parser.error("Provide --drive-folder (existing folder) or --drive-parent (auto-creates subfolder)")

    if args.drive_parent and not args.drive_folder:
        print(f"\nCreating Drive folder: {args.address}")
        args.drive_folder = create_drive_folder(args.address, args.drive_parent)
        print(f"  Folder ID: {args.drive_folder}")
        print(f"  https://drive.google.com/drive/folders/{args.drive_folder}")

    # Create a clean working directory for this run
    slug = args.address.replace(" ", "_").replace(",", "")[:40]
    work_dir = tempfile.mkdtemp(prefix=f"openclaw_{slug}_")
    print(f"\nWorking directory: {work_dir}")

    # Street-only for deed search (no city/state)
    street = " ".join(args.address.split()[:4])

    results = {}

    try:
        if not args.skip_tcad:
            tcad_args = [args.address, "--drive-folder", args.drive_folder, "--out-dir", work_dir]
            if args.pid:
                tcad_args += ["--pid", args.pid]
            results["tcad"] = run("tcad_lookup.py", tcad_args)

        if not args.skip_deeds:
            deed_args = [street, "--drive-folder", args.drive_folder, "--out-dir", work_dir]
            results["deeds"] = run("deed_search.py", deed_args)

        if not args.skip_comps:
            comp_args = ["--subdivision", args.subdivision,
                         "--drive-folder", args.drive_folder,
                         "--out-dir", work_dir]
            if args.pid:
                comp_args += ["--subject-pid", args.pid]
            results["comps"] = run("comps.py", comp_args)

        if not args.skip_owner and args.owner:
            owner_args = [args.owner, args.address,
                          "--drive-folder", args.drive_folder,
                          "--out-dir", work_dir]
            results["owner"] = run("owner_lookup.py", owner_args)

    finally:
        # Clean up working directory regardless of success/failure
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir)
            print(f"\nCleaned up: {work_dir}")

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for k, v in results.items():
        print(f"  {k}: {'✅ OK' if v else '❌ FAILED'}")
    if args.drive_folder:
        print(f"\n  Drive: https://drive.google.com/drive/folders/{args.drive_folder}")

if __name__ == "__main__":
    main()
