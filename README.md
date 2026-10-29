# Sampling Sigma Protocol

Sampling Sigma is a cybersecurity assurance protocol concept with a capped ERC-20 engineering baseline. This repository supports local testing and a Base Sepolia pilot. It does not authorize a public sale, investment offering, exchange listing, or production launch.

Its core purpose is cybersecurity research and assurance. The token is an optional protocol component, not the purpose of the system.

In plain English: **Sampling Sigma helps organizations prove that cybersecurity evidence was independently reviewed and has not been secretly changed.** See `docs/PLAIN_ENGLISH_PURPOSE.md` and `docs/PLAIN_ENGLISH_BUSINESS_PLAN.md` for the non-technical explanation and proposed business model.

## Cybersecurity R&D core

`SamplingSigmaResearchCore` provides a governed, evidence-oriented registry for:

- threat research
- cryptography research
- identity security
- software supply-chain security
- incident response
- AI security

The registry stores content hashes rather than confidential research material. Research submission and independent validation use separate roles. A reviewed result cannot be silently overwritten; validated results can only be explicitly superseded with a new evidence hash. This produces an auditable research lineage without publishing sensitive findings on-chain.

See `docs/CYBERSECURITY_RND_CORE.md` for the research lifecycle, trust boundaries, required controls, and planned engineering increments.

## Evidence assurance core

`SamplingSigmaAssuranceCore` implements the protocol's evidence-passport lifecycle independently of token balances. It records commitments for the artifact, assessed subject, scope, limitations, reviewer evidence, reviewer organization, conflict disclosure, validity period, status, and supersession lineage.

The contract enforces separate issuer and reviewer roles, rejects self-review, exposes current-state verification, and supports explicit revocation and supersession. A successful check proves that recorded commitments and state match; it does not prove that the underlying cybersecurity claim is true, complete, legally sufficient, or independently audited.

The website's **Assurance Lab** can hash text or a local file, create and download an Evidence Passport V2 JSON record, import a passport, and compare it with local evidence. Source evidence stays on the user's device.

## Publication set

The controlled publication package is under `deliverables/2026-10-28/`:

- research paper in DOCX and PDF
- standard white paper in DOCX and PDF
- editable client presentation in PPTX

These materials describe a development-stage research and controlled-pilot program. They do not authorize a public token sale, exchange listing, investment solicitation, mainnet deployment, or production assurance claim.

## Security properties

- Fixed one-billion-token supply by default, minted once at deployment
- No post-deployment mint function
- Separate administrator and treasury addresses are enforced
- Delayed two-step default administrator transfer
- Separate pause role; no mint authority exists
- Emergency transfer pause
- Holder burn support and EIP-2612 permit
- Non-upgradeable contract surface

Defaults are test parameters and must not be treated as approved tokenomics.

## Quick verification

```text
nvm use
npm install
npm run compile
npm test
```

The verified local run on October 28, 2026 produced **15 passing tests** across the token, research core, and assurance core. This is developer verification, not an independent security audit.

Hardhat 3 requires Node 22.13 or newer. This repository records Node 24 in `.nvmrc` so an older system Node is not used accidentally.

Read `docs/LAUNCH_SEQUENCE.md` before any network deployment.

## Desktop verifier demonstration

The `desktop-verifier/` package provides a privacy-first macOS and Windows interface for selecting a local document and generating a scoped evidence-passport demonstration. Documents remain on the user's device. The transparent evaluation build permits two completed runs and then directs users to Murukutla Group LLC for licensing or subscription information.

Commercial distribution requires signed installers and a server-validated, privacy-reviewed entitlement service. The repository never treats a raw MAC address as a license key and does not upload the selected document.
