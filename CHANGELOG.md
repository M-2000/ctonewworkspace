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
- Example greet function demonstrating FFI integration
- Unit tests for Rust and Flutter components

### Platform Support
- Android (ARM64, ARMv7)
- Windows (x86_64)

[0.1.0]: https://github.com/yourorg/yourrepo/releases/tag/v0.1.0
