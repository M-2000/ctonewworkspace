# Flutter + Rust Hybrid Workspace

A cross-platform mobile and desktop application combining Flutter for UI and Rust for core business logic.

## Architecture

This workspace consists of three main components:

- **`/app`** - Flutter application with Windows and Android platform support
- **`/core`** - Rust library compiled as a cdylib for FFI integration
- **`/bridge`** - Dart package providing FFI bindings between Flutter and Rust

## Build Prerequisites

### Required Tools

#### 1. Rust
- **Version**: 1.70.0 or higher
- **Installation**: https://rustup.rs/
- **Verify**: `rustc --version`

#### 2. Flutter
- **Version**: 3.10.0 or higher
- **Installation**: https://docs.flutter.dev/get-started/install
- **Verify**: `flutter --version`

#### 3. Dart
- **Version**: 3.0.0 or higher (included with Flutter)
- **Verify**: `dart --version`

### Platform-Specific Prerequisites

#### Android Development

1. **Android Studio** with Android SDK
   - Minimum SDK: API 21 (Android 5.0)
   - Target SDK: API 34
   - NDK version: 25.1.8937393

2. **Android NDK** for Rust compilation
   - Install via Android Studio SDK Manager

3. **Rust Android Targets**
   ```bash
   rustup target add aarch64-linux-android
   rustup target add armv7-linux-androideabi
   rustup target add x86_64-linux-android
   rustup target add i686-linux-android
   ```

4. **cargo-ndk** for cross-compilation
   ```bash
   cargo install cargo-ndk
   ```

5. **Environment Variables**
   ```bash
   export ANDROID_HOME=$HOME/Android/Sdk
   export NDK_HOME=$ANDROID_HOME/ndk/25.1.8937393
   ```

#### Windows Development

1. **Visual Studio 2022** or Visual Studio Build Tools
   - Workload: "Desktop development with C++"
   - Components: Windows 10/11 SDK, MSVC v143

2. **CMake** (3.14 or higher)
   - Install via Visual Studio or standalone

3. **Rust Windows Target**
   ```bash
   rustup target add x86_64-pc-windows-msvc
   ```

## Building

### Build Rust Core Library

#### For Android
```bash
cd core
cargo build --release --target aarch64-linux-android
cargo build --release --target armv7-linux-androideabi
```

#### For Windows
```bash
cd core
cargo build --release --target x86_64-pc-windows-msvc
```

### Build Flutter App

#### Install Dependencies
```bash
cd app
flutter pub get

cd ../bridge
dart pub get
```

#### Run on Android
```bash
cd app
flutter run -d android
```

#### Run on Windows
```bash
cd app
flutter run -d windows
```

## Project Structure

```
.
├── app/                    # Flutter application
│   ├── lib/
│   │   └── main.dart      # Application entry point
│   ├── android/           # Android platform configuration
│   ├── windows/           # Windows platform configuration
│   └── pubspec.yaml       # Flutter dependencies
│
├── core/                  # Rust core library
│   ├── src/
│   │   └── lib.rs        # Rust FFI interface
│   └── Cargo.toml        # Rust dependencies
│
├── bridge/               # Dart FFI bridge
│   ├── lib/
│   │   └── bridge.dart   # FFI bindings
│   ├── android/          # Android build configuration
│   ├── windows/          # Windows build configuration
│   └── pubspec.yaml      # Dart dependencies
│
└── README.md             # This file
```

## Development Workflow

1. Make changes to Rust code in `/core`
2. Rebuild the Rust library for target platform
3. Run Flutter app with `flutter run`
4. The app automatically loads the native library

## Testing

### Test Rust Code
```bash
cd core
cargo test
```

### Test Flutter App
```bash
cd app
flutter test
```

## Common Issues

### Library Not Found
Ensure the Rust library is built for the correct target platform before running the Flutter app.

### Android NDK Errors
Verify `ANDROID_HOME` and `NDK_HOME` environment variables are set correctly.

### Windows Build Errors
Ensure Visual Studio C++ build tools are installed and CMake is in PATH.

## License

See LICENSE file for details.
