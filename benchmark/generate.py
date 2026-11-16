#!/usr/bin/env python3
"""Create the frozen, non-sensitive SchemaShift benchmark using only stdlib."""
import argparse, hashlib, json, pathlib

TOOLS = ["lookup_ticket", "update_ticket", "search_kb", "create_escalation"]
VERSIONS = {
    "v1": "stable names and scalar arguments",
    "v2": "rename ticket_id to case_id; priority is integer; escalation needs reason",
    "v3a": "update_ticket split into patch_ticket and close_ticket",
    "v3b": "search_kb requires lookup_ticket first; escalation requires approval flag",
}

def digest(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def task(version, split, i):
    seed = f"schemashift:{version}:{split}:{i}"
    ticket = f"T-{hashlib.sha256(seed.encode()).hexdigest()[:8]}"
    return {
        "id": f"{version}-{split}-{i:03d}",
        "version": version,
        "split": split,
        "input": f"Resolve support request {ticket} using the available tools.",
        "expected": {"tool_family": TOOLS[i % len(TOOLS)], "ticket": ticket},
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--n", type=int, default=16)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    manifest = {"generator": "stdlib-v1", "n_per_split": args.n, "final_frozen": True, "versions": {}}
    for version, drift in VERSIONS.items():
        manifest["versions"][version] = {"drift": drift, "splits": {}}
        for split in ("train", "dev", "sealed-final"):
            rows = [task(version, split, i) for i in range(args.n)]
            p = args.out / f"{version}-{split}.jsonl"
            p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
            manifest["versions"][version]["splits"][split] = {"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "rows": len(rows)}
    manifest["manifest_sha256"] = digest(manifest)
    (args.out / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(args.out / "MANIFEST.json"), "sha256": manifest["manifest_sha256"]}))

if __name__ == "__main__":
    main()

