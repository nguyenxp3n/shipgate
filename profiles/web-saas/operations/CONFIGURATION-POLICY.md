# Configuration Policy

Configuration is typed, documented, validated at startup, and environment-scoped. Secrets/key material are separated from ordinary configuration. Unknown or unsafe values fail closed where they can compromise security/data integrity. Configuration referenced by code and required by deployment must be represented in the environment contract.
