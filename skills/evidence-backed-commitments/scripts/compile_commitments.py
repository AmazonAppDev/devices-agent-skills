#!/usr/bin/env python3
"""Compile spoken text into typed commitment candidates (zero dependencies, Python 3.9+).

Examples:
  python compile_commitments.py "I'll call Mom tonight. Also, I'll pay the electricity bill by Friday."
  python compile_commitments.py --now 2026-10-20T08:15:00+05:30 "Remind me to send the report by noon"
  python compile_commitments.py --completion "I called Mom"

Output is JSON. Candidates are proposals: a caller must still persist them as contracts, keep hedged
or third-party requests in NEEDS_CONFIRMATION, and never mark anything VERIFIED from text.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commitments as nl  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?", help="utterance (reads stdin when omitted)")
    ap.add_argument("--now", help="ISO time with offset used to resolve 'tonight', 'Friday', ... (default: now)")
    ap.add_argument("--request", action="store_true", help="speaker is someone else asking ('can you ...')")
    ap.add_argument("--completion", action="store_true", help="classify as a completion claim instead")
    args = ap.parse_args(argv)
    text = args.text if args.text is not None else sys.stdin.read()
    now = datetime.fromisoformat(args.now) if args.now else datetime.now().astimezone()
    if now.tzinfo is None:
        ap.error("--now needs a UTC offset, e.g. 2026-10-20T08:15:00+05:30")
    if args.completion:
        claim = nl.completion_claim(text)
        print(json.dumps({"completion_claim": bool(claim), "tokens": sorted(nl.tokens(claim)) if claim else []}))
        return 0
    out = []
    for c in nl.parse(text, now, request=args.request):
        c = dict(c)
        if c.get("due_local") is not None:
            c["due_local"] = c["due_local"].isoformat()
        c["status_if_persisted"] = (
            "NEEDS_CONFIRMATION" if c.get("negated") is None and (args.request or c.get("hedged")) else "ACTIVE"
        )
        if c.get("negated"):
            c["status_if_persisted"] = "NO_OBLIGATION"
        out.append(c)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
