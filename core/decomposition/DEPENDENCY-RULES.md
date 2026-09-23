# Dependency Rules

Domain-module dependencies form a directed acyclic graph. A cycle is a design error unless an explicitly classified non-module runtime dependency is outside the module DAG. Direct writes to another module's owned data are forbidden.
