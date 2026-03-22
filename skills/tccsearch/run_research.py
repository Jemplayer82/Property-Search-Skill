#!/usr/bin/env python3
"""
Full property research runner — TCAD + Deed search + Comps in one shot.
Usage: python3 run_research.py "3524 Winding Shore Lane" --drive-folder <id>

Runs:
  1. tcad_lookup.py   → TCAD tax/appraisal PDF → Drive
  2. deed_search.py   → Deed of Trust + Warranty Deed PDFs → Drive  
  3. comps.py         → Comps report → Drive
"""
import argparse, os, subprocess, sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run(script, args_list):
    cmd = [sys.executable, os.path.join(SCRIPT_DIR, script)] + args_list
    print(f"\n{'='*60}")
    print(f"Running: {script}")
    print(f"{'='*60}")
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Full property research suite")
    parser.add_argument("address", help="Full street address (e.g. '3524 Winding Shore Lane')")
    parser.add_argument("--pid", help="TCAD Property ID (skips TCAD search)")
    parser.add_argument("--drive-folder", required=True, help="Google Drive folder ID")
    parser.add_argument("--subdivision", default="Park at Blackhawk",
                        help="Subdivision for comps (default: Park at Blackhawk)")
    parser.add_argument("--owner", help="Owner name for contact lookup (e.g. 'Ferguson Landon Jennifer')")
    parser.add_argument("--skip-comps", action="store_true")
    parser.add_argument("--skip-deeds", action="store_true")
    parser.add_argument("--skip-tcad", action="store_true")
    parser.add_argument("--skip-owner", action="store_true")
    parser.add_argument("--out-dir", default="/tmp")
    args = parser.parse_args()

    # Street-only for deed search (no city/state)
    street = " ".join(args.address.split()[:4])

    results = {}

    if not args.skip_tcad:
        tcad_args = [args.address, "--drive-folder", args.drive_folder, "--out-dir", args.out_dir]
        if args.pid:
            tcad_args += ["--pid", args.pid]
        results["tcad"] = run("tcad_lookup.py", tcad_args)

    if not args.skip_deeds:
        deed_args = [street, "--drive-folder", args.drive_folder, "--out-dir", args.out_dir]
        results["deeds"] = run("deed_search.py", deed_args)

    if not args.skip_comps:
        comp_args = ["--subdivision", args.subdivision,
                     "--drive-folder", args.drive_folder,
                     "--out-dir", args.out_dir]
        if args.pid:
            comp_args += ["--subject-pid", args.pid]
        results["comps"] = run("comps.py", comp_args)

    if not args.skip_owner and args.owner:
        owner_args = [args.owner, args.address,
                      "--drive-folder", args.drive_folder,
                      "--out-dir", args.out_dir]
        results["owner"] = run("owner_lookup.py", owner_args)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for k, v in results.items():
        print(f"  {k}: {'✅ OK' if v else '❌ FAILED'}")

if __name__ == "__main__":
    main()
