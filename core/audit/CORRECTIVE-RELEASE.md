# Corrective Release

Every finding receives exactly one terminal disposition: `FIXED`, `ALREADY_FIXED`, `DEFERRED`, `NOT_APPLICABLE`, or `REJECTED`. `FIXED` and `ALREADY_FIXED` require resolution and verification references. A deferred Critical or High finding remains a release blocker by default. Corrections update canonical authority first, then regenerate derived artifacts and re-run affected validators.
