"""Deterministic conformance tests for arcstone-mcp-bridge (ARC-SPEC-2026-MCP-01)."""

from pathlib import Path
import json
import unittest
import yaml

from arcstone_mcp import kernel_runner
from arcstone_mcp.receipt_signer import MASTER_ANCHOR, SPEC_ID

ROOT = Path(__file__).resolve().parents[1]


class TestArcstoneMcpBridge(unittest.TestCase):
    def test_pins_lock_matches_anchor(self) -> None:
        pins = json.loads((ROOT / "PINS.lock").read_text(encoding="utf-8"))
        self.assertEqual(pins["spec_id"], SPEC_ID)
        self.assertEqual(pins["master_anchor"], MASTER_ANCHOR)
        self.assertEqual(pins["operational_drag"], "C_ops = 0")

    def test_all_three_profiles_load_and_simulate(self) -> None:
        profiles = [
            "banking_treasury.yaml",
            "energy_grid.yaml",
            "clinical_actuation.yaml",
            "digital_assets.yaml",
        ]
        for filename in profiles:
            with self.subTest(profile=filename):
                profile = yaml.safe_load((ROOT / "profiles" / filename).read_text(encoding="utf-8"))
                self.assertEqual(profile["upstream_kernel"]["master_anchor"], MASTER_ANCHOR)

                volatile_key = profile["domain_vocabulary"]["volatile_retry_fields"][0]

                # 1. Verify idempotent replay suppression when only volatile transport field rotates
                receipt = kernel_runner.simulate_permit_lifecycle(
                    profile=profile,
                    intent_payload={"amount": 1000, volatile_key: "ID-1"},
                    retry_payload={"amount": 1000, volatile_key: "ID-2"},
                    simulate_timeout=True,
                )
                self.assertEqual(receipt["status"], "PASS")
                self.assertEqual(receipt["details"]["execution_permit_96b"]["permit_size_bytes"], 96)
                self.assertEqual(receipt["details"]["execution_permit_96b"]["m_alloc_bytes"], 0)
                states = [t["state"] for t in receipt["details"]["cas_transitions"]]
                self.assertEqual(
                    states,
                    [
                        "DISPATCH_RESERVED",
                        "IDEMPOTENT_REPLAY_SUPPRESSED",
                        "UNKNOWN_RECONCILE",
                        "LOCKED_MANUAL",
                    ],
                )

                # 2. Verify regeneration drift is blocked when canonical business payload mutates
                drift_receipt = kernel_runner.simulate_permit_lifecycle(
                    profile=profile,
                    intent_payload={"amount": 1000, volatile_key: "ID-1"},
                    retry_payload={"amount": 2500, volatile_key: "ID-2"},
                    simulate_timeout=False,
                )
                drift_states = [t["state"] for t in drift_receipt["details"]["cas_transitions"]]
                self.assertEqual(
                    drift_states,
                    [
                        "DISPATCH_RESERVED",
                        "REGENERATION_DRIFT_BLOCKED",
                        "SETTLED_COMMITTED",
                    ],
                )

    def test_tcb_boundary_audit_and_memo(self) -> None:
        profile = yaml.safe_load((ROOT / "profiles" / "banking_treasury.yaml").read_text(encoding="utf-8"))
        audit = kernel_runner.audit_tc_boundary(
            profile=profile,
            downstream_stack_config={
                "trusted_opid_minter": True,
                "durable_cas_store": True,
                "hsm_kms_key_custody": True,
                "fail_closed_gateway_enclave": True,
            },
        )
        self.assertEqual(audit["status"], "READY")

        memo = kernel_runner.generate_validation_memo(profile, "FedNow")
        self.assertIn("A-77-DELTA-SHIELD-LOCKED", memo)
        self.assertIn("FedNow", memo)


    def test_digital_assets_psbt_rbf_retry_storm(self) -> None:
        try:
            from arcstone_mcp.server import _resolve_profile_path

            resolved = _resolve_profile_path("digital_assets")
            self.assertEqual(resolved.name, "digital_assets.yaml")
        except ModuleNotFoundError:
            self.assertTrue((ROOT / "src" / "arcstone_mcp" / "profiles" / "digital_assets.yaml").is_file())

        profile = yaml.safe_load((ROOT / "profiles" / "digital_assets.yaml").read_text(encoding="utf-8"))
        self.assertEqual(profile["profile_id"], "arcstone-digital-assets-v1")
        vectors = profile["simulation_vectors"]

        receipt = kernel_runner.simulate_permit_lifecycle(
            profile=profile,
            intent_payload=vectors["intent_payload"],
            retry_payload=vectors["retry_payload"],
            simulate_timeout=True,
        )
        self.assertEqual(receipt["status"], "PASS")
        states = [t["state"] for t in receipt["details"]["cas_transitions"]]
        self.assertEqual(
            states,
            [
                "DISPATCH_RESERVED",
                "IDEMPOTENT_REPLAY_SUPPRESSED",
                "UNKNOWN_RECONCILE",
                "LOCKED_MANUAL",
            ],
        )


if __name__ == "__main__":
    unittest.main()
