# arcstone-mcp-bridge (`v0.1.0`)

**Status:** `FROZEN / PHASE 2 READY (C_ops = 0)`  
**Specification:** `ARC-SPEC-2026-MCP-01 (REV-00)` | **Suite Baseline:** `v1.4.6-EXEC`  
**Upstream Kernel Anchor:** `A-77-DELTA-SHIELD-LOCKED`

Universal read-only conformance, sandbox-simulation, and institutional diligence Model Context Protocol (MCP) shell for the Arcstone Computational Spine (`Malloc = 0 B`, `D(a) = DENY => Delta_external(a) = 0`).

---

## Architectural Separation (`C_ops = 0`)

- **Zero Upstream Mutation:** Communicates with frozen `#[no_std]` Rust reference kernels (`arcstone-treasury-bind`, `domain-projection-spec`) strictly via CLI/FFI subprocess calls or deterministic simulation bindings.
- **Zero Live Actuation (Invariant I3):** Operates strictly as an offline/sandbox evaluation and ITGC diligence shell (`untrusted producer != protected resource`). Never holds production payment rail credentials or physical actuator keys.
- **Distinct from Runtime Proxy (`arcstone-mcp-sidecar`):** Whereas `arcstone-mcp-sidecar` (`v0.1.0-canonical`) gates live runtime MCP tool invocations via atomic single-use claims (`I1-I3`), `arcstone-mcp-bridge` provides self-serve ARB/ORM evaluation and compliance mapping driven by declarative YAML Domain Profile Packs.

---

## 3-Command Quickstart (Institutional Evaluators)

```bash
# 1. Install in an isolated environment
python -m venv .venv && source .venv/bin/activate && pip install -e .

# 2. Launch MCP-Banking conformance server (ISO 20022 / FedNow / SR 26-2)
arcstone-mcp-bridge --profile profiles/banking_treasury.yaml

# 3. Or launch MCP-Grid / MCP-Clinical conformance servers
arcstone-mcp-bridge --profile profiles/energy_grid.yaml
arcstone-mcp-bridge --profile profiles/clinical_actuation.yaml
```

---

## Universal MCP Primitives

### Resources (Read-Only Grounding)
- `arcstone://profile/spec` — Canonical protocol specification, Zenodo DOI anchors, and formal invariants (`I1-I3`).
- `arcstone://profile/wire-map` — Maps domain message schemas onto trusted gateway OpID extraction, out-of-band CAS (`H_admitted`), and the 96-byte `ExecutionPermit`.
- `arcstone://profile/regulatory-matrix` — Structured compliance mapping (Federal Reserve SR 26-2 / OCC Bulletin 2026-13, NERC CIP, FDA PCCP).
- `arcstone://kernel/attestation` — Live verification receipt derived from `PINS.lock`, Zenodo DOIs, and Coq `8.18.0` status.

### Tools (Deterministic Sandbox Execution)
- `simulate_permit_lifecycle(intent_payload, retry_payload, simulate_timeout)` — Executes two-attempt regeneration and timeout simulation, returning 96-byte `ExecutionPermit` fields, POSIX dominance codes (`POSIX 0` vs `POSIX 32`), and 7-state CAS transitions (`DISPATCH_RESERVED -> UNKNOWN_RECONCILE -> LOCKED_MANUAL`).
- `verify_kernel_integrity(repo_path)` — Runs `cargo test --locked` and validates source digests against `PINS.lock` and `A-77-DELTA-SHIELD-LOCKED`.
- `audit_tc_boundary(downstream_stack_config)` — Separates Coq-verified kernel guarantees from customer-owned Trusted Computing Base (TCB) responsibilities.
- `generate_validation_memo(target_rail_or_protocol)` — Generates an internal Architecture Review Board (ARB) or Operational Risk Management (ORM) validation memo.

### Prompts (Turnkey Evaluator Workflows)
- `run-synthetic-conformance-audit`
- `map-downstream-integration`
