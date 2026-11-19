# SchemaShift benchmark contract

The environment is deterministic and non-sensitive. The four tool families are
`lookup_ticket`, `update_ticket`, `search_kb`, and `create_escalation`.

`v1` is the stable baseline: `ticket_id`, scalar `priority`, and one
`update_ticket` operation. `v2` renames `ticket_id` to `case_id`, changes
`priority` to an integer, and adds required `reason` to escalation. `v3a` splits
`update_ticket` into `patch_ticket`/`close_ticket`. `v3b` adds ordering and
approval preconditions. Each row embeds its version's tool contract and the
expected typed arguments, so the drift is executable rather than a label-only
annotation. Every version has independent train, dev, and sealed-final data.

Corrective examples may be mined only from observed train/dev failure classes. The
sealed-final files are frozen and hash-recorded before training.

