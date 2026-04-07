# Security policy

## Supported versions

Security fixes are applied to the active development branch of this repository. Docker and API usage should track the latest documented setup in [README](README.md) and [infra/docker/README.md](infra/docker/README.md).

## Reporting a vulnerability

Please **do not** open a public issue for security-sensitive reports.

- Email or contact the maintainers of your fork or organization privately with:
  - Description of the issue and impact
  - Steps to reproduce
  - Affected components (e.g. OmniVoiceApi HTTP server, Docker image, .NET client)

We will acknowledge receipt and work on a fix and disclosure timeline when applicable.

## Hardening notes

- The OmniVoiceApi server loads a large model and writes uploaded audio only under the configured `OMNIVOICE_VOICES_DIR`. Run with least privilege and restrict network exposure in production.
- The MAUI sample enables **cleartext HTTP** on Android for local development; do not ship that configuration to production without TLS and proper network policies.
