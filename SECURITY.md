# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, subprocess sandboxing flaw, YAML profile parsing defect, or boundary isolation bypass affecting `arcstone-mcp-bridge`, please **do not open a public issue**.

Submit reports through either of the following private channels:

1. **GitHub Private Vulnerability Reporting (Recommended):**
   - Go to the **Security** tab of this repository (`trencinodin-stack/arcstone-mcp-bridge`).
   - Click **Report a vulnerability**.
   - Fill out the form to submit a private report directly to maintainers.

2. **Email:**
   - Contact us at **security@arcstoneos.com**.

---

## What to Include

Please include, where applicable:
- A concise description of the vulnerability or conformance simulation defect.
- Minimal reproduction steps or test input demonstrating the issue.
- The affected release tag (e.g., `v0.1.0`), active profile (`profiles/*.yaml`), or upstream anchor (`A-77-DELTA-SHIELD-LOCKED`).
- Whether the issue involves:
  - Subprocess command injection or path traversal in `verify_kernel_integrity(repo_path)`;
  - Unsafe deserialization or arbitrary code execution via malformed Domain Profile Packs (`profiles/*.yaml`);
  - Volatile retry field stripping bypass or deterministic SHA-256 receipt collision in `simulate_permit_lifecycle`;
  - POSIX status code identifier or 7-state CAS transition mapping mismatch (`DISPATCH_RESERVED → UNKNOWN_RECONCILE → LOCKED_MANUAL`);
  - Violation of read-only / zero-actuation isolation (`I3`: `untrusted producer != protected resource`).

---

## Upstream Core Immutability & Errata Protocol

`arcstone-mcp-bridge` operates as a thin, read-only conformance and evaluation wrapper under a strict Locked Protocol Policy ($C_{\text{ops}} = 0$).

- **Zero Upstream Kernel Mutation:** Reporting a bridge defect does not authorize modifying frozen upstream Rust crates (`arcstone-treasury-bind`, `domain-projection-spec`, `arcstone-continuity-core`) or Coq `8.18.0` transition proofs.
- **Canonical Errata Governance:** Any defect traceable to upstream predicate thresholds, POSIX status identifiers, or lattice dominance rules requires a formal update to **ARC-ERR-2026-001** (Master Canonical Errata, DOI `10.5281/zenodo.23069559`).

---

## Scope & Bounded Claims

`arcstone-mcp-bridge` is an offline/sandbox conformance, simulation, and institutional diligence shell (`ARC-SPEC-2026-MCP-01`). Its security guarantees are limited strictly to read-only profile grounding, deterministic sandbox permit simulation, and local `cargo test --locked` receipt generation.

The repository explicitly does **not** claim:
- Live runtime MCP tool-call gating or single-use capability consumption (handled downstream in `arcstone-mcp-sidecar`);
- Production hardware or eBPF microkernel enforcement (hosted in `Arcstone OS`);
- Production HSM/KMS key custody, durable linearizable CAS persistence, or certified live rail actuation (customer-owned TCB responsibilities);
- Non-deterministic candidate proposal containment (handled in `arcstone-adaptive-producer-lab`).

---

## Response Timeline

We will acknowledge receipt within **48 hours** and work with you on a coordinated resolution and disclosure timeline.
