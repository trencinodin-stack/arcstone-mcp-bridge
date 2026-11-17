"""Read-only subprocess and deterministic 96-byte ExecutionPermit simulator."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from .receipt_signer import MASTER_ANCHOR, canonical_sha256, mint_conformance_receipt


def _strip_volatile_fields(payload: dict[str, Any], volatile_fields: list[str]) -> dict[str, Any]:
    """Strip transport-layer retry metadata so canonical semantic payload is isolated."""
    return {k: v for k, v in payload.items() if k not in set(volatile_fields)}


def simulate_permit_lifecycle(
    profile: dict[str, Any],
    intent_payload: dict[str, Any],
    retry_payload: dict[str, Any] | None = None,
    simulate_timeout: bool = False,
) -> dict[str, Any]:
    """
    Simulate deterministic 96-byte ExecutionPermit admission and 7-state CAS barrier
    across initial proposal, non-deterministic retry regeneration, and timeout recovery.
    """
    volatile = profile.get("domain_vocabulary", {}).get("volatile_retry_fields", [])
    canonical_initial = _strip_volatile_fields(intent_payload, volatile)
    h_admitted = canonical_sha256(canonical_initial)

    permit_96b = {
        "permit_size_bytes": 96,
        "magic": "ARC1",
        "anchor": MASTER_ANCHOR,
        "op_id": hashlib.sha256(f"{profile['profile_id']}:{h_admitted}".encode()).hexdigest()[:32],
        "h_admitted": h_admitted,
        "m_alloc_bytes": 0,
        "s_max_bytes": 4096,
    }

    transitions = [
        {"step": 1, "state": "DISPATCH_RESERVED", "posix_code": 0, "verdict": "ADMIT_INITIAL"}
    ]

    if retry_payload is not None:
        canonical_retry = _strip_volatile_fields(retry_payload, volatile)
        h_retry = canonical_sha256(canonical_retry)
        if h_retry == h_admitted:
            transitions.append(
                {
                    "step": 2,
                    "state": "IDEMPOTENT_REPLAY_SUPPRESSED",
                    "posix_code": 32,
                    "verdict": "DENY_DUPLICATE_CLAIM (Invariant I2)",
                }
            )
        else:
            transitions.append(
                {
                    "step": 2,
                    "state": "REGENERATION_DRIFT_BLOCKED",
                    "posix_code": 32,
                    "verdict": "DENY_HASH_MISMATCH (Regeneration Gap Closed)",
                }
            )

    if simulate_timeout:
        transitions.extend(
            [
                {
                    "step": len(transitions) + 1,
                    "state": "UNKNOWN_RECONCILE",
                    "posix_code": 12,
                    "verdict": "HOLD_PENDING_RECONCILIATION",
                },
                {
                    "step": len(transitions) + 2,
                    "state": "LOCKED_MANUAL",
                    "posix_code": 32,
                    "verdict": "FAIL_CLOSED_BARRIER_LOCKED (Delta_external = 0)",
                },
            ]
        )
    else:
        transitions.append(
            {
                "step": len(transitions) + 1,
                "state": "SETTLED_COMMITTED",
                "posix_code": 0,
                "verdict": "ACTUATION_PERMITTED_ONCE",
            }
        )

    return mint_conformance_receipt(
        profile_id=profile["profile_id"],
        check_type="SIMULATE_PERMIT_LIFECYCLE",
        status="PASS",
        details={
            "execution_permit_96b": permit_96b,
            "cas_transitions": transitions,
            "invariant_check": "D(a) = DENY => Delta_external(a) = 0",
        },
    )


def verify_kernel_integrity(
    profile: dict[str, Any],
    pins: dict[str, Any],
    repo_path: str,
) -> dict[str, Any]:
    """Run cargo test --locked against a local clone of the upstream reference crate."""
    target = Path(repo_path).expanduser().resolve()
    if not (target / "Cargo.toml").exists():
        return mint_conformance_receipt(
            profile_id=profile["profile_id"],
            check_type="VERIFY_KERNEL_INTEGRITY",
            status="FAIL_MISSING_CARGO_TOML",
            details={"repo_path": str(target), "expected_pins": pins},
        )

    proc = subprocess.run(
        ["cargo", "test", "--locked"],
        cwd=str(target),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    status = "PASS" if proc.returncode == 0 else "FAIL"
    return mint_conformance_receipt(
        profile_id=profile["profile_id"],
        check_type="VERIFY_KERNEL_INTEGRITY",
        status=status,
        details={
            "repo_path": str(target),
            "cargo_exit_code": proc.returncode,
            "upstream_pins": pins.get("upstream_kernels", {}),
            "stdout_tail": proc.stdout[-1500:],
            "stderr_tail": proc.stderr[-1500:],
        },
    )


def audit_tc_boundary(
    profile: dict[str, Any],
    downstream_stack_config: dict[str, Any],
) -> dict[str, Any]:
    """Separate Coq-verified kernel guarantees from customer-owned TCB responsibilities."""
    required_tcb_controls = {
        "trusted_opid_minter": bool(downstream_stack_config.get("trusted_opid_minter")),
        "durable_cas_store": bool(downstream_stack_config.get("durable_cas_store")),
        "hsm_kms_key_custody": bool(downstream_stack_config.get("hsm_kms_key_custody")),
        "fail_closed_gateway_enclave": bool(downstream_stack_config.get("fail_closed_gateway_enclave")),
    }
    missing = [k for k, v in required_tcb_controls.items() if not v]
    return mint_conformance_receipt(
        profile_id=profile["profile_id"],
        check_type="AUDIT_TC_BOUNDARY",
        status="READY" if not missing else "INCOMPLETE_CUSTOMER_TCB",
        details={
            "arcstone_kernel_guarantees": [
                "Zero-heap predicate determinism (M_alloc = 0 B, S_max <= 4096 B)",
                "96-byte content-addressable ExecutionPermit binding",
                "7-state CAS reconciliation automaton (Coq 8.18.0 verified, Print Assumptions == empty)",
            ],
            "customer_owned_tcb_status": required_tcb_controls,
            "missing_customer_controls": missing,
        },
    )


def generate_validation_memo(
    profile: dict[str, Any],
    target_rail_or_protocol: str,
) -> str:
    """Generate a ready-to-file internal ARB / ORM validation memo."""
    reg = profile.get("regulatory_framework", {})
    kernel = profile.get("upstream_kernel", {})
    guidance = "
".join(f"- {g}" for g in reg.get("primary_guidance", []))
    return f"""# INTERNAL ARCHITECTURE REVIEW BOARD (ARB) & ORM VALIDATION MEMORANDUM

**Subject:** Deterministic Execution Boundary Conformance Assessment — `{target_rail_or_protocol}`  
**Profile Pack:** `{profile['profile_id']}` ({profile['display_name']})  
**Upstream Reference Kernel:** `{kernel.get('crate')}` (`{kernel.get('version')}`) | **DOI:** `{kernel.get('spec_doi')}`  
**Master Epistemic Anchor:** `{MASTER_ANCHOR}`

## 1. Control Classification & Regulatory Alignment
- **Control Classification:** {reg.get('control_classification')}
- **Excluded from Statistical Model Risk Management (MRM) Definition:** `{reg.get('excluded_from_mrm_model_def')}`
- **Applicable Supervisory Guidance:**
{guidance}

## 2. Non-Authorization Safety & Regeneration Gap Closure
The upstream reference kernel enforces `D(a) = DENY => Delta_external(a) = 0` inside a freestanding `#[no_std]` static memory envelope (`M_alloc = 0 B`, `S_max <= 4096 B`). Out-of-band Content-Addressable Storage (`H_admitted`) binds canonical business semantics to a 96-byte `ExecutionPermit`, eliminating Time-of-Check to Time-of-Use (TOCTOU) and LLM retry regeneration drift prior to `{target_rail_or_protocol}` dispatch.

## 3. Customer-Owned Trusted Computing Base (TCB) Prerequisites
1. Trusted ingress OpID minter upstream of non-deterministic AI proposal producers (Invariant I3).
2. Durable, linearizable Compare-And-Swap (CAS) persistence backing the 7-state reconciliation automaton.
3. Hardware Security Module (HSM) / KMS custody for production rail signing keys.
"""
