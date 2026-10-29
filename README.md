# Sampling Sigma Evidence Passports

Sampling Sigma is an experimental cybersecurity assurance prototype for recording privacy-preserving evidence commitments, independent review state, revocation, and supersession lineage. This repository is the reproducibility package for the manuscript **“Sampling Sigma: Governed Evidence Passports for Cybersecurity Assurance.”**

## What this repository demonstrates

- SHA-256 commitments detect byte-level changes in a controlled mutation corpus.
- A fail-closed lifecycle restricts records to explicit submitted, validated, rejected, revoked, and superseded states.
- Issuer and reviewer roles are separated, and self-review is rejected.
- Scope, limitations, subject identity, reviewer organization, conflict disclosure, and review evidence are committed without placing confidential source material on-chain.
- A fixed-supply experimental ERC-20 contract is included because it is part of the complete prototype test suite.

## What it does not prove

This repository does **not** prove that submitted evidence is true, that an assessment is sufficient, that the contracts are independently audited, that the system satisfies any law or regulation, or that the token is approved for production, sale, or exchange listing. The paper reports controlled prototype evidence only.

## Reproduce the reported evaluation

Requirements:

- Node.js 24 (see `.nvmrc`)
- npm
- Python 3.12 or later

Run:

```bash
npm ci
npm test
python3 tools/research_evaluation.py
```

The script writes fresh machine-readable evidence to `evaluation/actual-prototype-results.json` and the complete contract-test transcript to `evaluation/hardhat-test-output.txt`.

## Repository map

- `contracts/` — Solidity research prototypes
- `test/` — complete Hardhat test suite
- `tools/research_evaluation.py` — reproducible mutation, hashing, lifecycle, and contract evaluation
- `evaluation/` — measured results used by the manuscript
- `paper/` — submission-candidate manuscript PDF
- `REPRODUCIBILITY.md` — protocol, expected outputs, and interpretation boundaries
- `SECURITY.md` — responsible disclosure and production-use warning

## Current evidence snapshot

The included 2026-10-29 run reports:

- 5,000 of 5,000 controlled single-bit mutations detected;
- 25 lifecycle state pairs exhaustively checked, with 21 forbidden pairs rejected;
- 15 of 15 smart-contract tests passing; and
- SHA-256 performance measured on the disclosed test machine.

Performance values are environment-specific and should be regenerated on each system.

## Citation

Use `CITATION.cff`. The public release and commit hash identify the exact research artifact.

## License

Code is released under the MIT License. The manuscript remains © 2026 Sri Sai Lakshmi Ganesh Murukutla and is included for scholarly review and citation.
