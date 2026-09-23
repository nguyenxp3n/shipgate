# Technical Specification Template

## System topology
Define runtime components, module/service boundaries, dependency direction, synchronous/asynchronous interaction types, authoritative stores, derived stores, external providers, and trust boundaries.

## Ownership
Map each durable business entity, public interface, background responsibility, and operational responsibility to exactly one owner where singular ownership is required.

## Reliability and failure boundaries
For each component/dependency define timeout, retry/degradation/fail-closed posture, idempotency/reconciliation needs, observability, and recovery expectations.

## Deployment and change compatibility
Define build/runtime artifacts, configuration model, compatibility windows, migration/deployment ordering, rollback/forward-fix posture, and operational gates without changing frozen product behavior.
