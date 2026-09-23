# Archive Integrity

Release staging rejects symlinks and excludes repository/runtime caches, worktrees, bytecode, virtual environments, and untrusted partial workflow-run output. ZIP entries are sorted and use fixed metadata so an unchanged staged tree produces a byte-stable archive on the supported runtime. Archive verification rejects absolute paths and parent-directory traversal entries before extraction.
