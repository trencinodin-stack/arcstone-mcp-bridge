"""Universal thin MCP server driven by declarative Domain Profile Packs."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import yaml
from mcp.server.fastmcp import FastMCP

from . import kernel_runner
from .receipt_signer import MASTER_ANCHOR, SPEC_ID


def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML profile structure in {path}")
    return data


def _load_pins(root: Path) -> dict[str, Any]:
    pins_path = root / "PINS.lock"
    if pins_path.exists():
        return json.loads(pins_path.read_text(encoding="utf-8"))
    return {"spec_id": SPEC_ID, "master_anchor": MASTER_ANCHOR, "upstream_kernels": {}}


def build_server(profile_path: Path) -> FastMCP:
    root = _default_root()
    profile = _load_yaml(profile_path)
    pins = _load_pins(root)

    mcp = FastMCP(
        name=f"arcstone-mcp-bridge ({profile['profile_id']})",
    )

    @mcp.resource("arcstone://profile/spec")
    def get_profile_spec() -> str:
        """Canonical protocol specification, Zenodo DOI anchors, and formal invariants (I1-I3)."""
        return json.dumps(
            {
                "spec_id": SPEC_ID,
                "master_anchor": MASTER_ANCHOR,
                "profile_id": profile["profile_id"],
                "display_name": profile["display_name"],
                "upstream_kernel": profile["upstream_kernel"],
                "invariants": {
                    "I1": "D(a) = DENY => Delta_external(a) = 0",
                    "I2": "1 valid claim => <= 1 actuation",
                    "I3": "untrusted producer != protected resource",
                },
            },
            indent=2,
        )

    @mcp.resource("arcstone://profile/wire-map")
    def get_wire_map() -> str:
        """Domain message schemas mapped onto OpID extraction, CAS H_admitted, and 96B ExecutionPermit."""
        return json.dumps(
            {
                "profile_id": profile["profile_id"],
                "domain_vocabulary": profile["domain_vocabulary"],
                "permit_contract": {
                    "wire_size_bytes": 96,
                    "memory_envelope_bytes": 4096,
                    "heap_allocations": 0,
                },
            },
            indent=2,
        )

    @mcp.resource("arcstone://profile/regulatory-matrix")
    def get_regulatory_matrix() -> str:
        """Structured supervisory compliance mapping and commercial boundary."""
        return json.dumps(
            {
                "profile_id": profile["profile_id"],
                "regulatory_framework": profile["regulatory_framework"],
                "commercial_boundary": profile["commercial_boundary"],
            },
            indent=2,
        )

    @mcp.resource("arcstone://kernel/attestation")
    def get_kernel_attestation() -> str:
        """Live verification receipt derived from PINS.lock and upstream kernel anchors."""
        return json.dumps(pins, indent=2)

    @mcp.tool()
    def simulate_permit_lifecycle(
        intent_payload: dict[str, Any],
        retry_payload: dict[str, Any] | None = None,
        simulate_timeout: bool = False,
    ) -> dict[str, Any]:
        """Execute two-attempt regeneration and timeout simulation against the active domain profile."""
        return kernel_runner.simulate_permit_lifecycle(
            profile=profile,
            intent_payload=intent_payload,
            retry_payload=retry_payload,
            simulate_timeout=simulate_timeout,
        )

    @mcp.tool()
    def verify_kernel_integrity(repo_path: str) -> dict[str, Any]:
        """Run cargo test --locked and validate local source against PINS.lock."""
        return kernel_runner.verify_kernel_integrity(
            profile=profile,
            pins=pins,
            repo_path=repo_path,
        )

    @mcp.tool()
    def audit_tc_boundary(downstream_stack_config: dict[str, Any]) -> dict[str, Any]:
        """Separate Coq-verified kernel guarantees from customer-owned TCB responsibilities."""
        return kernel_runner.audit_tc_boundary(
            profile=profile,
            downstream_stack_config=downstream_stack_config,
        )

    @mcp.tool()
    def generate_validation_memo(target_rail_or_protocol: str) -> str:
        """Generate a ready-to-file internal ARB / ORM validation memo."""
        return kernel_runner.generate_validation_memo(
            profile=profile,
            target_rail_or_protocol=target_rail_or_protocol,
        )

    @mcp.prompt(name="run-synthetic-conformance-audit")
    def run_synthetic_conformance_audit() -> str:
        """Step-by-step evaluator workflow for verifying PINS.lock and adversarial CAS edge cases."""
        crate = profile["upstream_kernel"]["crate"]
        return (
            f"Run a synthetic conformance audit for {profile['display_name']} ({profile['profile_id']}):
"
            f"1. Inspect `arcstone://kernel/attestation` and clone `{crate}` (`{profile['upstream_kernel']['version']}`).
"
            f"2. Call `verify_kernel_integrity` on the cloned repository path to confirm `cargo test --locked` passes.
"
            f"3. Call `simulate_permit_lifecycle` with a sample payload, a mutated retry payload, and `simulate_timeout=True` "
            f"to verify `DISPATCH_RESERVED -> UNKNOWN_RECONCILE -> LOCKED_MANUAL` fail-closed isolation."
        )

    @mcp.prompt(name="map-downstream-integration")
    def map_downstream_integration() -> str:
        """Walk institutional platform engineers through wiring OpID minting and CAS around the 96B permit."""
        return (
            f"Map downstream integration for {profile['display_name']}:
"
            f"1. Read `arcstone://profile/wire-map` to identify volatile retry fields to strip prior to `H_admitted` hashing.
"
            f"2. Call `audit_tc_boundary` with the institution's proposed OpID minter, CAS store, and HSM/KMS topology.
"
            f"3. Call `generate_validation_memo` for the target rail to produce an ARB/ORM sign-off package."
        )

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="Arcstone Multi-Domain MCP Bridge")
    default_profile = os.environ.get(
        "ARCSTONE_MCP_PROFILE",
        str(_default_root() / "profiles" / "banking_treasury.yaml"),
    )
    parser.add_argument(
        "--profile",
        type=Path,
        default=Path(default_profile),
        help="Path to declarative Domain Profile Pack YAML",
    )
    args = parser.parse_args()
    server = build_server(args.profile.expanduser().resolve())
    server.run()


if __name__ == "__main__":
    main()
