# Architecture Overview

This document describes the high-level architecture of the Flutter + Rust hybrid workspace.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Flutter App                           │
│                      (/app directory)                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    UI Layer                           │  │
│  │  • Material Design components                         │  │
│  │  • State management                                   │  │
│  │  • Platform-specific rendering                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Bridge Layer                         │  │
│  │              (/bridge directory)                      │  │
│  │  • Dart FFI bindings                                  │  │
│  │  • Type conversions (Dart ↔ C)                        │  │
│  │  • Memory management                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
                           ↓ FFI
┌──────────────────────────────────────────────────────────────┐
│                     Rust Core Library                        │
│                    (/core directory)                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 Business Logic                        │  │
│  │  • Core algorithms                                    │  │
│  │  • Data processing                                    │  │
│  │  • Platform-agnostic code                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Compiled as: cdylib (shared library)                       │
│  • libcore.so (Android)                                     │
│  • core.dll (Windows)                                       │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Flutter App (`/app`)

**Purpose**: User interface and application logic

**Responsibilities**:
- Render UI using Flutter widgets
- Handle user interactions
- Manage application state
- Call Rust functions through bridge
- Platform-specific UI adaptations

**Key Files**:
- `lib/main.dart` - Application entry point
- `android/` - Android platform configuration
- `windows/` - Windows platform configuration
- `pubspec.yaml` - Flutter dependencies

### Bridge Package (`/bridge`)

**Purpose**: FFI abstraction layer between Dart and Rust

**Responsibilities**:
- Load native libraries dynamically
- Convert Dart types to C types and vice versa
- Manage memory lifecycle for FFI calls
- Provide Dart-friendly API for Rust functions
- Handle errors from native code

**Key Files**:
- `lib/bridge.dart` - FFI bindings and type conversions
- `android/CMakeLists.txt` - Android build configuration
- `windows/CMakeLists.txt` - Windows build configuration

**Design Patterns**:
- **Dynamic library loading**: Platform-specific library discovery
- **Type conversion**: Safe conversion between Dart and C types
- **Memory management**: Proper allocation and deallocation
- **Error handling**: Null checks and exception handling

### Rust Core (`/core`)

**Purpose**: High-performance business logic

**Responsibilities**:
- Implement core algorithms and data structures
- Expose C-compatible FFI interface
- Ensure thread safety and memory safety
- Provide cross-platform functionality

**Key Files**:
- `src/lib.rs` - Library entry point with FFI exports
- `Cargo.toml` - Rust dependencies and build configuration

**Design Patterns**:
- **FFI exports**: `#[no_mangle]` and `extern "C"` functions
- **Safe FFI**: Proper null checks and error handling
- **Memory ownership**: Clear ownership transfer at FFI boundary

## Data Flow

### Calling Rust from Dart

1. **Dart invocation**
   ```dart
   String result = greet('World');
   ```

2. **Bridge conversion**
   ```dart
   final namePtr = name.toNativeUtf8().cast<ffi.Char>();
   final resultPtr = _greet(namePtr);
   ```

3. **FFI boundary**
   - Dart string → C char pointer
   - Call native function
   - C char pointer → Dart string

4. **Rust processing**
   ```rust
   #[no_mangle]
   pub extern "C" fn greet(name: *const c_char) -> *mut c_char {
       // Process and return result
   }
   ```

5. **Memory cleanup**
   - Free Rust-allocated memory
   - Free Dart-allocated memory

## Build Process

### Android Build Flow

1. Flutter builds Dart code to native
2. CMake invokes Cargo for Rust compilation
3. Rust builds for Android targets (ARM64, ARMv7)
4. Shared libraries (.so) copied to APK
5. APK assembled with all assets

### Windows Build Flow

1. Flutter builds Dart code to native
2. CMake invokes Cargo for Rust compilation
3. Rust builds for Windows target (x86_64-MSVC)
4. DLL copied to executable directory
5. Executable packaged with dependencies

## Cross-Platform Strategy

### Rust Core
- Write platform-agnostic code
- Use conditional compilation for platform-specific features
- Compile to different targets (Android ARM, Windows x64)

### Flutter UI
- Use Material Design for consistency
- Handle platform differences with Platform checks
- Adapt UI for different screen sizes

### Bridge
- Platform-specific library loading
- Consistent API regardless of platform
- Handle platform-specific paths and configurations

## Security Considerations

### Memory Safety
- Rust provides memory safety guarantees
- FFI boundary requires careful null checking
- Proper cleanup prevents memory leaks

### Type Safety
- Strong typing in both Dart and Rust
- Type conversions validated at bridge layer
- Runtime checks for invalid data

### Thread Safety
- Rust ensures thread safety at compile time
- FFI calls should be thread-safe
- Consider using Arc/Mutex for shared state

## Performance Characteristics

### Advantages
- Rust provides near-native performance
- No garbage collection overhead in core logic
- Efficient FFI calls (minimal overhead)
- Parallel processing capabilities

### Trade-offs
- FFI calls have small overhead
- Type conversions require processing
- Memory must be managed manually at boundaries

## Testing Strategy

### Unit Tests
- Rust: `cargo test` in core/
- Dart: `flutter test` in app/
- Bridge: Test FFI conversions separately

### Integration Tests
- Test complete data flow from UI to Rust
- Verify memory management
- Test error handling paths

### Platform Tests
- Test on real Android devices
- Test on Windows machines
- Verify library loading works correctly

## Future Extensibility

### Adding New Platforms
1. Add Rust target for new platform
2. Configure bridge for platform-specific library loading
3. Add Flutter platform configuration
4. Update build scripts

### Adding New Features
1. Implement in Rust core
2. Export FFI function
3. Add bridge bindings
4. Update Flutter UI

### Performance Optimization
- Profile with platform-specific tools
- Optimize hot paths in Rust
- Minimize FFI boundary crossings
- Use batch operations where possible
