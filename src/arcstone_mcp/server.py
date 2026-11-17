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


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def _default_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_profile_path(raw: str | Path) -> Path:
    candidate = Path(raw).expanduser()
    if candidate.is_file():
        return candidate.resolve()
    bundled_by_name = _package_dir() / "profiles" / candidate.name
    if bundled_by_name.is_file():
        return bundled_by_name.resolve()
    repo_relative = _default_root() / candidate
    if repo_relative.is_file():
        return repo_relative.resolve()
    raise FileNotFoundError(f"Domain Profile Pack not found: {raw}")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML profile structure in {path}")
    return data


def _load_pins(root: Path) -> dict[str, Any]:
    for pins_path in (root / "PINS.lock", _package_dir() / "PINS.lock"):
        if pins_path.exists():
            return json.loads(pins_path.read_text(encoding="utf-8"))
    return {"spec_id": SPEC_ID, "master_anchor": MASTER_ANCHOR, "upstream_kernels": {}}


def build_server(profile_path: Path | str) -> FastMCP:
    root = _default_root()
    resolved_profile = _resolve_profile_path(profile_path)
    profile = _load_yaml(resolved_profile)
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
        return f"""Run a synthetic conformance audit for {profile['display_name']} ({profile['profile_id']}):
1. Inspect `arcstone://kernel/attestation` and clone `{crate}` (`{profile['upstream_kernel']['version']}`).
2. Call `verify_kernel_integrity` on the cloned repository path to confirm `cargo test --locked` passes.
3. Call `simulate_permit_lifecycle` with a sample payload, a mutated retry payload, and `simulate_timeout=True` to verify `DISPATCH_RESERVED -> UNKNOWN_RECONCILE -> LOCKED_MANUAL` fail-closed isolation."""

    @mcp.prompt(name="map-downstream-integration")
    def map_downstream_integration() -> str:
        """Walk institutional platform engineers through wiring OpID minting and CAS around the 96B permit."""
        return f"""Map downstream integration for {profile['display_name']}:
1. Read `arcstone://profile/wire-map` to identify volatile retry fields to strip prior to `H_admitted` hashing.
2. Call `audit_tc_boundary` with the institution's proposed OpID minter, CAS store, and HSM/KMS topology.
3. Call `generate_validation_memo` for the target rail to produce an ARB/ORM sign-off package."""

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="Arcstone Multi-Domain MCP Bridge")
    default_profile = os.environ.get(
        "ARCSTONE_MCP_PROFILE",
        "banking_treasury.yaml",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default=default_profile,
        help="Path or bundled name of Domain Profile Pack YAML (default: banking_treasury.yaml)",
    )
    args = parser.parse_args()
    server = build_server(args.profile)
    server.run()


if __name__ == "__main__":
    main()