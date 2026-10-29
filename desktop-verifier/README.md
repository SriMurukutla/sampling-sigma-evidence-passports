# Sampling Sigma Desktop Verifier

A macOS and Windows demonstration application for creating a local, scope-bound document evidence passport.

## What the demo does

- The user chooses a document using the native file picker.
- The document is processed locally and is not uploaded.
- The application records the filename, byte size, SHA-256 commitment, scope, limitations, and generation time.
- Two completed evaluation runs are permitted per registered device before licensing is requested.
- The licensing button opens an email addressed to `murukutlassl@gmail.com`.

## Privacy and licensing boundary

The application derives a one-way SHA-256 device identifier from the operating system's stable machine identifier. It does not store or display a raw MAC address. The local state is stored in the operating system's application-data directory with owner-only permissions where supported.

The included enforcement is suitable for a transparent demonstration, not commercial anti-tamper protection. Strong reinstall-resistant licensing requires a Murukutla Group licensing service that records the hashed device identifier and signed entitlement. That service should publish a privacy notice, provide device-reset/support procedures, rate-limit requests, and never collect uploaded document content.

## Run locally

```bash
npm install
npm test
npm start
```

## Build installers

```bash
npm run build:mac
npm run build:win
```

macOS installers must be signed and notarized before public distribution. Windows installers should be code-signed to reduce SmartScreen warnings.
