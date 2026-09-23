# Checksum Policy

`SHA256SUMS.txt` inventories every regular staged file except itself, sorted by POSIX relative path. The ZIP archive digest is stored only in an external `<archive>.sha256` sidecar to avoid self-reference. Release verification recalculates file digests after a fresh extraction rather than trusting the inventory alone.
