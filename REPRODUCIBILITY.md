# Reproducibility Protocol

## Research question

Can a governed, hash-committed evidence-passport prototype detect controlled byte changes, enforce an explicit review lifecycle, preserve review lineage, and do so with measurable local overhead?

## Frozen artifact

The Git tag and release identify the frozen source. Dependency versions are locked in `package-lock.json`. Do not substitute a newer dependency set when reproducing the reported run.

## Procedure

1. Use Node.js 24 and Python 3.12 or later.
2. Run `npm ci`.
3. Run `npm test` and confirm a zero exit code.
4. Run `python3 tools/research_evaluation.py`.
5. Preserve the generated JSON and test transcript with the machine, operating-system, Python, Node.js, npm, and commit identifiers.
6. Compare the qualitative invariants below; treat timing values as machine-specific.

## Qualitative invariants

- Every controlled single-bit mutation changes the SHA-256 digest in the generated corpus.
- The reference lifecycle accepts only the four declared transitions.
- Contract tests reject unauthorized operations and issuer self-review.
- Validated records preserve reviewer evidence and explicit supersession lineage.

## Quantitative outputs

- mutation cases and detections;
- hashing median latency, 95th percentile latency, and throughput;
- lifecycle state-pair counts and forbidden acceptances; and
- smart-contract test count, exit code, and duration.

## Interpretation limits

The mutation experiment is not a proof of collision resistance or semantic truth. The reference lifecycle model is not a formal verification of EVM bytecode. Passing tests do not replace an independent security audit. Performance on one machine does not establish production scalability. No human-subject, field-deployment, legal-compliance, token-market, or economic outcome is measured.

## Independent extension

Future work should add property-based testing, symbolic execution, formal state-transition proofs, third-party contract audit, cross-organization interoperability trials, and an approved human-subject study where applicable.
