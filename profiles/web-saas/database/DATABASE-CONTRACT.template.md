# Database Contract Template

Record engine/version, identifiers/timestamps, entity/table ownership, primary/foreign keys, UNIQUE/CHECK/NOT NULL constraints, tenant key and enforcement where applicable, delete behavior, retention, indexes/hot queries, transaction ownership, migration compatibility and backup/restore expectations. Physical migrations own physical schema; data semantics remain in the canonical data model.
