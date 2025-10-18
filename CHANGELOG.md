# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-18

### Added
- Initial Flutter app scaffold with Windows and Android platform support
- Rust core library crate configured as cdylib with cross-platform build settings
- Dart FFI bridge package for Flutter-Rust integration
- Comprehensive workspace configuration files (.gitignore, README, LICENSE, formatting configs)
- Build automation scripts (build.sh, Makefile)
- Documentation (README, QUICKSTART, CONTRIBUTING)
- GitHub Actions CI workflow for automated testing
- **core_version API**: Rust FFI function returning JSON-formatted version metadata (M0-2)
  - Exposes crate name and version via C ABI
  - Complete Dart FFI bindings for core_version function
  - Flutter UI demonstrating version display
  - Unit tests for Rust core_version function
- Unit tests for Rust and Flutter components

### Platform Support
- Android (arm64-v8a via NDK)
- Windows (x86_64-MSVC)

[0.1.0]: https://github.com/yourorg/yourrepo/releases/tag/v0.1.0
