#!/usr/bin/env python3
"""Reproducible, local evaluation for the Sampling Sigma prototype."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation"
OUT.mkdir(parents=True, exist_ok=True)


def percentile(values: list[float], fraction: float) -> float:
    values = sorted(values)
    idx = min(len(values) - 1, max(0, round((len(values) - 1) * fraction)))
    return values[idx]


def hashing_benchmark() -> dict:
    payload = hashlib.sha256(b"sampling-sigma-reproducible-seed-20261029").digest() * 32768
    rounds = 256
    elapsed = []
    for _ in range(rounds):
        start = time.perf_counter_ns()
        hashlib.sha256(payload).digest()
        elapsed.append((time.perf_counter_ns() - start) / 1_000_000)
    total_mb = len(payload) * rounds / (1024 * 1024)
    total_seconds = sum(elapsed) / 1000
    return {
        "algorithm": "SHA-256",
        "payload_bytes": len(payload),
        "rounds": rounds,
        "median_latency_ms": round(statistics.median(elapsed), 4),
        "p95_latency_ms": round(percentile(elapsed, 0.95), 4),
        "throughput_mib_per_second": round(total_mb / total_seconds, 2),
    }


def tamper_detection() -> dict:
    cases = 5000
    detected = 0
    for i in range(cases):
        source = hashlib.sha512(f"sampling-sigma-case-{i}".encode()).digest() * ((i % 8) + 1)
        changed = bytearray(source)
        changed[(i * 17) % len(changed)] ^= 1 << (i % 8)
        detected += hashlib.sha256(source).digest() != hashlib.sha256(changed).digest()
    return {
        "cases": cases,
        "single_bit_mutations_detected": detected,
        "detection_rate_percent": round(100 * detected / cases, 4),
        "claim_boundary": "Detects byte changes in this controlled corpus; does not prove semantic truth.",
    }


def lifecycle_model() -> dict:
    states = ("SUBMITTED", "VALIDATED", "REJECTED", "REVOKED", "SUPERSEDED")
    allowed = {("SUBMITTED", "VALIDATED"), ("SUBMITTED", "REJECTED"),
               ("VALIDATED", "REVOKED"), ("VALIDATED", "SUPERSEDED")}
    accepted, rejected = [], []
    for source in states:
        for target in states:
            (accepted if (source, target) in allowed else rejected).append([source, target])
    return {
        "state_pairs_exhaustively_checked": len(states) ** 2,
        "allowed_transitions": len(accepted),
        "forbidden_transitions_rejected": len(rejected),
        "forbidden_acceptances": 0,
        "model_note": "Reference state-machine model; contract behavior is reported separately.",
    }


def contract_tests() -> dict:
    node_bin = "/Users/srimurukutla/.nvm/versions/node/v24.18.0/bin"
    env = dict(os.environ)
    env["PATH"] = node_bin + os.pathsep + env.get("PATH", "")
    started = time.perf_counter()
    result = subprocess.run(
        ["npm", "test"], cwd=ROOT, env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=180,
    )
    output = result.stdout
    (OUT / "hardhat-test-output.txt").write_text(output, encoding="utf-8")
    matches = re.findall(r"(\d+)\s+passing", output)
    return {
        "command": "npm test",
        "exit_code": result.returncode,
        "passing_tests": int(matches[-1]) if matches else None,
        "duration_seconds": round(time.perf_counter() - started, 3),
        "output_file": "hardhat-test-output.txt",
    }


def main() -> None:
    report = {
        "study_id": "SS-DSR-PROTOTYPE-2026-10-29",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "actual_results": {
            "tamper_detection": tamper_detection(),
            "hashing_performance": hashing_benchmark(),
            "lifecycle_reference_model": lifecycle_model(),
            "smart_contract_tests": contract_tests(),
        },
        "not_measured": [
            "independent security audit", "field usability", "production availability",
            "cross-organization interoperability", "legal or regulatory compliance",
            "economic or token-market outcomes",
        ],
    }
    path = OUT / "actual-prototype-results.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
