#!/usr/bin/env python3
"""CLI utility to scan Hindi poetry lines with the deterministic meter engine."""

import argparse
import sys
from pathlib import Path

# Ensure root dir is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.meter.scanner import scan_charan  # noqa: E402
from app.meter.templates import get_template  # noqa: E402


def main():
    parser = argparse.ArgumentParser(
        description="Chhand CLI - Scans Hindi poetry lines with deterministic Pingala meter engine."
    )
    parser.add_argument("line", type=str, help="Devanagari Hindi poetry line to scan")
    parser.add_argument(
        "meter",
        type=str,
        nargs="?",
        default="doha",
        help="Meter name: 'doha', 'chaupai', or 'custom' (default: doha)",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=None,
        help="Explicit target matra count (overrides meter defaults)",
    )
    parser.add_argument(
        "--charan",
        type=int,
        default=0,
        help="Charan index (0-based, default: 0)",
    )
    parser.add_argument(
        "--mode",
        choices=["orthographic", "phonetic", "manual"],
        default="orthographic",
        help="Pronunciation mode (default: orthographic)",
    )

    args = parser.parse_args()

    # Determine target matra count
    if args.target:
        target = args.target
    else:
        tmpl = get_template(args.meter, custom_pattern=[12] if args.meter == "custom" else None)
        target = tmpl.charan_targets[args.charan % len(tmpl.charan_targets)]

    result = scan_charan(
        text=args.line,
        target_matras=target,
        charan_index=args.charan,
        meter_name=args.meter,
        pronunciation_mode=args.mode,
    )

    print("\n" + "=" * 50)
    print(f"CHHAND METER SCANSION: {args.line}")
    print("=" * 50)
    print(f"Meter:          {args.meter} (Charan {args.charan + 1})")
    print(f"Target Matras:  {result.target_matras}")
    print(f"Actual Matras:  {result.actual_matras}")
    print(f"Difference:     {'+' if result.difference > 0 else ''}{result.difference}")
    print(f"Status:         {result.status.upper()}")
    print("-" * 50)
    print("Syllables & Weights:")
    for s in result.syllables:
        mark = "— (guru)" if s.classification == "guru" else "• (laghu)"
        print(f"  {s.text:<10} weight={s.weight} [{mark}] ({s.reason})")
    print("-" * 50)
    print("Diagnostics:")
    for d in result.diagnostics:
        print(f"  • {d}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
