# Transaction Policy

Each mutation names authoritative writes, same-transaction writes, post-commit events, eventual effects, and response data source. A transaction may not reach across module ownership by direct foreign-table mutation unless an approved orchestration/ownership contract explicitly permits it.
