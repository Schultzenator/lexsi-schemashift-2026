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

SCHEMAS = {
    "v1": {
        "lookup_ticket": {"required": ["ticket_id"], "types": {"ticket_id": "string"}},
        "update_ticket": {"required": ["ticket_id", "priority"], "types": {"ticket_id": "string", "priority": "string"}},
        "search_kb": {"required": ["query"], "types": {"query": "string"}},
        "create_escalation": {"required": ["ticket_id"], "types": {"ticket_id": "string"}},
    },
    "v2": {
        "lookup_ticket": {"required": ["case_id"], "types": {"case_id": "string"}},
        "update_ticket": {"required": ["case_id", "priority"], "types": {"case_id": "string", "priority": "integer"}},
        "search_kb": {"required": ["query"], "types": {"query": "string"}},
        "create_escalation": {"required": ["case_id", "reason"], "types": {"case_id": "string", "reason": "string"}},
    },
    "v3a": {
        "lookup_ticket": {"required": ["case_id"], "types": {"case_id": "string"}},
        "patch_ticket": {"required": ["case_id", "priority"], "types": {"case_id": "string", "priority": "integer"}},
        "close_ticket": {"required": ["case_id", "resolution"], "types": {"case_id": "string", "resolution": "string"}},
        "search_kb": {"required": ["query"], "types": {"query": "string"}},
        "create_escalation": {"required": ["case_id", "reason"], "types": {"case_id": "string", "reason": "string"}},
    },
    "v3b": {
        "lookup_ticket": {"required": ["case_id"], "types": {"case_id": "string"}},
        "update_ticket": {"required": ["case_id", "priority"], "types": {"case_id": "string", "priority": "integer"}},
        "search_kb": {"required": ["query"], "types": {"query": "string"}},
        "create_escalation": {"required": ["case_id", "reason", "approved"], "types": {"case_id": "string", "reason": "string", "approved": "boolean"}},
    },
}

def digest(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def task(version, split, i):
    seed = f"schemashift:{version}:{split}:{i}"
    ticket = f"T-{hashlib.sha256(seed.encode()).hexdigest()[:8]}"
    family = TOOLS[i % len(TOOLS)]
    if version == "v3a" and family == "update_ticket":
        family = "patch_ticket" if i % 2 == 0 else "close_ticket"
    schema = SCHEMAS[version][family]
    args = {}
    for name, typ in schema["types"].items():
        if name in ("ticket_id", "case_id"):
            args[name] = ticket
        elif typ == "integer":
            args[name] = (i % 3) + 1
        elif typ == "boolean":
            args[name] = True
        elif name == "reason":
            args[name] = "customer-impact"
        elif name == "resolution":
            args[name] = "resolved"
        else:
            args[name] = f"support query {ticket}"
    row = {
        "id": f"{version}-{split}-{i:03d}",
        "version": version,
        "split": split,
        "input": f"Resolve support request {ticket} using the available tools.",
        "expected": {"tool_family": family, "ticket": ticket, "arguments": args},
        "schema": {"tools": SCHEMAS[version]},
    }
    if version == "v3b" and family == "search_kb":
        row["expected"]["precondition"] = "lookup_ticket must precede search_kb"
    if version == "v3b" and family == "create_escalation":
        row["expected"]["precondition"] = "approved=true is required"
    return row

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

