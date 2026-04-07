# Changelog

All notable changes to this repository are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **OmniVoiceApi** monorepo layout: `apps/api`, `infra/docker`, `examples/console-ui`, `examples/maui`, `libraries/OmniVoice.Client`.
- Environment variables `OMNIVOICE_MODEL`, `OMNIVOICE_VOICES_DIR`, `OMNIVOICE_DEVICE` for API configuration (with CLI overrides).
- Docker image and Compose file for GPU-oriented deployment.
- .NET client (`OmniVoice.Client`) and MAUI sample using `Plugin.Maui.Audio` for playback.

## [0.1.2] — existing Python package

Prior releases refer to the `omnivoice` PyPI package versioning in `pyproject.toml`.
