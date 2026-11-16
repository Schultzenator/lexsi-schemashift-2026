# SchemaShift benchmark contract

The environment is deterministic and non-sensitive. The four tool families are
`lookup_ticket`, `update_ticket`, `search_kb`, and `create_escalation`.

`v1` is the stable baseline. `v2` changes names, types, and required fields.
`v3a` changes the operation graph through a split. `v3b` changes ordering and
preconditions. Every version has independent train, dev, and sealed-final data.

Corrective examples may be mined only from observed train/dev failure classes. The
sealed-final files are frozen and hash-recorded before training.

