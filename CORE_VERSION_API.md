# Core Version API Documentation (M0-2)

## Overview

The `core_version` API exposes version metadata from the Rust core library via FFI. This API is accessible from Dart/Flutter applications running on Windows (MSVC) and Android (arm64-v8a) platforms.

## Architecture

### Rust Core (cdylib)

The Rust library exposes a C-compatible function that returns JSON-formatted metadata:

```rust
#[no_mangle]
pub extern "C" fn core_version() -> *mut c_char {
    // Returns JSON: {"crate_name":"core","crate_version":"0.1.0"}
}
```

**Build Targets:**
- Windows: `x86_64-pc-windows-msvc` → `core.dll`
- Android: `aarch64-linux-android` → `libcore.so` (arm64-v8a)

### Dart FFI Bridge

The bridge package (`/bridge`) provides type-safe Dart bindings:

```dart
String coreVersion() => CoreLib.coreVersion();
```

### Flutter Application

The Flutter app (`/app`) demonstrates the API usage:

```dart
import 'package:bridge/bridge.dart';

final version = coreVersion(); // Returns JSON string
final data = jsonDecode(version);
print(data['crate_name']);    // "core"
print(data['crate_version']); // "0.1.0"
```

## Building

### Prerequisites

- Rust toolchain with targets installed:
  - `rustup target add x86_64-pc-windows-msvc`
  - `rustup target add aarch64-linux-android`
- Android NDK (for Android builds)
- Flutter SDK

### Build Commands

```bash
# Build for Windows
./build.sh windows

# Build for Android
./build.sh android

# Build for both platforms
./build.sh all
```

## Testing

### Rust Unit Tests

```bash
cd core
cargo test
```

Expected output: Test `core_version_returns_metadata` should pass.

### Running the Flutter App

```bash
cd app

# On Windows
flutter run -d windows

# On Android
flutter run -d android
```

The app will display the core version metadata in a card widget.

## API Response Format

The `core_version()` function returns a JSON string with the following schema:

```json
{
  "crate_name": "core",
  "crate_version": "0.1.0"
}
```

## Platform Support

| Platform | Target Triple | Library Output | Status |
|----------|---------------|----------------|--------|
| Windows | x86_64-pc-windows-msvc | core.dll | ✅ Supported |
| Android (arm64) | aarch64-linux-android | libcore.so | ✅ Supported |

## Memory Management

The Rust function allocates memory for the returned string. The Dart bridge automatically frees this memory using the `free_string` FFI function:

```rust
#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    // Deallocates the string
}
```

The Dart bridge handles this automatically - no manual memory management required from the Flutter side.

## Future Extensions

Future versions may include additional metadata fields:

- `build_timestamp`: When the library was compiled
- `git_commit`: Git commit hash
- `target_triple`: The Rust target triple used for compilation
- `build_profile`: "debug" or "release"

## Troubleshooting

### Library Not Found

If you see "Failed to load dynamic library" errors:

1. **Windows**: Ensure `core.dll` is in the same directory as the Flutter executable
2. **Android**: Check that `libcore.so` is included in the APK under `lib/arm64-v8a/`

### Version Mismatch

If the version displayed doesn't match expectations:

1. Rebuild the Rust library: `./build.sh <platform>`
2. Clean Flutter build: `cd app && flutter clean`
3. Rebuild the Flutter app: `flutter build <platform>`

## Implementation Checklist

- [x] Rust `core_version()` function implemented
- [x] Cargo configured for cdylib output
- [x] Windows (MSVC) build target configured
- [x] Android (arm64-v8a) build target configured
- [x] Dart FFI bindings implemented
- [x] Flutter UI demonstration
- [x] Rust unit tests
- [x] Build scripts updated
- [x] Documentation updated

---

**Milestone:** M0-2  
**Status:** Complete  
**Last Updated:** 2025-10-18
