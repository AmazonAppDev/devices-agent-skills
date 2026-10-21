#!/usr/bin/env python3
"""Audit contract records against the never-fake-done rules (zero dependencies).

Usage: python check_contract.py contracts.json [evidence.json]
  contracts.json: a contract object, a list of them, or {"contracts": [...], "evidence": [...]}.
Exit code 1 when any rule is violated; findings are printed one per line.
"""

import json
import sys

POLICY = {
    "BEE_CONVERSATION_AUDIT": {"AUTHORIZED_PARTICIPATION", "USER_CONFIRMATION"},
    "AUTHORIZED_MANUAL_CONFIRMATION": {"USER_CONFIRMATION"},
    "RING_THRESHOLD_OBJECT_SCAN": {"USER_CONFIRMATION", "VISIBLE_ITEM_MATCH"},
    "RING_SPATIAL_CUSTODY": {"AUTHORIZED_TRANSFER", "AUTHORIZED_INWARD_TRANSFER"},
    "FIRE_TV_LIVE_POSE_CAMERA": {"POSE_15_CYCLES", "POSE_CYCLES"},
}
TERMINAL = {"VERIFIED", "CANCELLED", "REJECTED"}
NEVER_PROOF = {"REMINDER_SENT", "SCHEDULER_FIRED", "MODEL_ASSERTION", "COURIER_CLAIM", "SPOKEN_CLAIM"}


def audit(contracts, evidence):
    by_id = {e["evidence_id"]: e for e in evidence}
    findings = []
    for c in contracts:
        cid = c.get("contract_id", "?")
        if c.get("status") == "VERIFIED":
            allowed = POLICY.get(c.get("verification_modality"), set())
            accepted = [
                by_id[e] for e in c.get("evidence_ids", [])
                if e in by_id and by_id[e].get("decision", "VALIDATED") == "VALIDATED"
                and by_id[e].get("contract_id", cid) == cid
            ]
            if not any(e.get("kind") in allowed for e in accepted):
                findings.append(f"{cid}: VERIFIED without evidence allowed for {c.get('verification_modality')}")
            for e in accepted:
                if e.get("kind") in NEVER_PROOF:
                    findings.append(f"{cid}: evidence kind {e['kind']} can never prove completion")
                if e.get("kind") == "USER_CONFIRMATION" and e.get("provenance") not in {None, "USER_CONFIRMED"}:
                    findings.append(f"{cid}: owner confirmation must be labelled USER_CONFIRMED")
        history = [r.get("status") for r in c.get("revisions", [])]
        for before, after in zip(history, history[1:]):
            if before in TERMINAL and after != before:
                findings.append(f"{cid}: terminal state {before} regressed to {after}")
        if c.get("source_mode") not in {None, "LIVE_VERIFIED", "SIMULATED_VERIFIED", "NOT_CONNECTED", "BLOCKED"}:
            findings.append(f"{cid}: unknown source_mode {c.get('source_mode')}")
    return findings


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    data = json.load(open(argv[0], encoding="utf-8"))
    evidence = json.load(open(argv[1], encoding="utf-8")) if len(argv) > 1 else []
    if isinstance(data, dict) and "contracts" in data:
        contracts, evidence = data["contracts"], data.get("evidence", evidence)
    else:
        contracts = data if isinstance(data, list) else [data]
    findings = audit(contracts, evidence)
    for f in findings:
        print(f)
    print(f"{len(contracts)} contract(s) checked, {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
