# SchemaShift: closed-loop recovery from tool-schema drift

Track 3 — Agentic Fine-tuning. This repository contains the deterministic benchmark
and the pre-submit evidence package for a proposed self-healing tool agent.

## Claim status

No performance claim is made in this snapshot. The required model training and
AuditKIT evaluation were not run because the active environment has no usable
`torch`/`transformers` stack, no installed AgentTune/AuditKIT package, and no
Hugging Face write session. Publishing invented before/after numbers would make the
submission invalid.

## Experiment contract

The benchmark generator creates four tool schemas (`v1`, `v2`, `v3a`, `v3b`) and
disjoint train/dev/sealed-final splits. Drift families are parameter rename/type and
required-field changes, tool split/merge, and ordering/precondition changes. Final
splits are hashed before any training and are never used for corrective-example
mining.

Run the generator with:

```bash
python3 benchmark/generate.py --out benchmark/generated
```

The planned measured outputs are task success, schema-valid call rate, correct-tool
selection, calls per successful task, recovery delta, and prior-version retention.
They remain `unmeasured` until genuine AgentTune training and AuditKIT scoring are
executed.

## Provenance

- Base model permitted by the live rules: `CohereLabs/tiny-aya-base`.
- AgentTune source: `Lexsi-Labs/AgentTune` (commit recorded in the private evidence).
- AuditKIT source: `Lexsi-Labs/AuditKIT` (commit recorded in the private evidence).
- Official rules: https://hackathon.lexsi.ai/

This tree intentionally contains no credentials, browser state, Factory internals,
private mail, child model homes, or infrastructure shims.

