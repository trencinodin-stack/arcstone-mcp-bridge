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
arcstone-mcp-bridge --profile profiles/digital_assets.yaml
