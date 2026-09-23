# Health and Readiness

**Liveness** answers only whether the process is alive enough to be restarted if it is not. It must not flap merely because a dependency is temporarily unavailable.

**Readiness** answers whether the instance may receive traffic. It may incorporate required dependency/bootstrap state without leaking internal credentials/topology in a public response. Deployment orchestration removes an instance from traffic when readiness fails.
