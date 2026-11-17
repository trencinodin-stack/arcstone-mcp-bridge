"""Deterministic JSON conformance receipt generator anchored to A-77-DELTA-SHIELD-LOCKED."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


MASTER_ANCHOR = "A-77-DELTA-SHIELD-LOCKED"
SPEC_ID = "ARC-SPEC-2026-MCP-01-REV00"


def canonical_sha256(payload: Any) -> str:
    """Compute deterministic SHA-256 over canonical sorted JSON."""
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def mint_conformance_receipt(
    profile_id: str,
    check_type: str,
    status: str,
    details: dict[str, Any],
) -> dict[str, Any]:
    """Generate a deterministic, self-verifying conformance receipt."""
    body = {
        "spec_id": SPEC_ID,
        "master_anchor": MASTER_ANCHOR,
        "profile_id": profile_id,
        "check_type": check_type,
        "status": status,
        "evaluated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "details": details,
    }
    body["receipt_sha256"] = canonical_sha256(body)
    return body
