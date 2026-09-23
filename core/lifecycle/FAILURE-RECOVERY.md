# Failure Recovery

State writes are atomic. Failed or interrupted work does not replace the last valid state. Partial outputs remain untrusted until a validated completion record exists.
