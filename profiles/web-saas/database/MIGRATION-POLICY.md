# Migration Policy

Production schema change follows **expand → migrate → contract** when compatibility or data backfill is involved. Expand introduces backward-compatible structure; migrate/backfill moves data with bounded operations and observability; contract removes obsolete structure only after all readers/writers are compatible.

The default recovery posture is **forward-fix** unless the project documents a verified rollback path. Every risky migration states lock/statement timeout policy, deployment ordering, compatibility window, data verification and failure recovery. Destructive/irreversible changes are protected decisions.
