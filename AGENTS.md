# AGENTS.md — Autonomous Agent & Evaluator Navigation Contract

**Repository:** `trencinodin-stack/arcstone-mcp-bridge` (`v0.1.0`)  
**Specification:** `ARC-SPEC-2026-MCP-01 (REV-00)` | **Suite Baseline:** `v1.4.6-EXEC`  
**Master Epistemic Anchor:** `A-77-DELTA-SHIELD-LOCKED`  
**Operational Posture:** `FROZEN / PHASE 2 READY (C_ops = 0)`

---

## 1. Non-Negotiable Grounding & Boundary Rules
1. **Read-Only Evaluation Shell Only:** `arcstone-mcp-bridge` is an offline/sandbox conformance, simulation, and ITGC diligence server. Never configure it with production payment rail credentials, live physical actuator keys, or mutable production state (Invariant I3: `untrusted producer != protected resource`).
2. **Do Not Confuse with `arcstone-mcp-sidecar`:**
   - `arcstone-mcp-bridge` (`v0.1.0`) = offline/sandbox evaluation, ARB/ORM memo generation, and `cargo test --locked` conformance auditing.
   - `arcstone-mcp-sidecar` (`v0.1.0-canonical`) = live runtime MCP execution boundary proxy enforcing single-use capability claims (`I1–I3`).
3. **Zero Upstream Kernel Mutation (`C_ops = 0`):** Never modify frozen upstream Rust crates (`arcstone-treasury-bind`, `domain-projection-spec`, `arcstone-continuity-core`) or Coq `8.18.0` proofs to accommodate domain-specific vocabulary. Add new regulated verticals solely by cloning a declarative YAML file under `profiles/*.yaml`.

---

## 2. Canonical Entrypoints & Machine Surfaces
- **`PINS.lock`:** Authoritative version, specification ID, and Zenodo DOI pin table (`10.5281/zenodo.24119501`, `10.5281/zenodo.24041851`, `10.5281/zenodo.22966979`).
- **`profiles/banking_treasury.yaml`:** ISO 20022 (`pacs.008`, `pacs.002`, `camt.054`), FedNow/RTP/CHIPS/SWIFT, Federal Reserve SR 26-2 / OCC Bulletin 2026-13 conformance pack.
- **`profiles/energy_grid.yaml`:** DNP3 / IEC 61850, NERC CIP-005/007, `ARC-SPEC-2026-DPP-01` cyber-physical interlock pack.
- **`profiles/clinical_actuation.yaml`:** HL7 FHIR R4 / DICOM RT Plan, FDA PCCP / IEC 62304 fail-closed dose envelope pack.
- **`src/arcstone_mcp/server.py`:** Universal FastMCP server exposing 4 Resources, 4 Tools, and 2 Prompts.

---

## 3. Standard Evaluator Execution Order
1. Read `arcstone://kernel/attestation` and `arcstone://profile/spec` to verify `A-77-DELTA-SHIELD-LOCKED` and active profile pins.
2. Execute `verify_kernel_integrity(repo_path)` against a local clone of the pinned upstream crate (`cargo test --locked`).
3. Execute `simulate_permit_lifecycle(intent_payload, retry_payload, simulate_timeout=True)` to verify `D(a) = DENY => Delta_external(a) = 0` and `DISPATCH_RESERVED -> UNKNOWN_RECONCILE -> LOCKED_MANUAL`.
4. Execute `audit_tc_boundary` and `generate_validation_memo` to produce institution-specific TCB and ARB/ORM artifacts.
