# Quick Start Guide

Get up and running with the Flutter + Rust hybrid workspace in minutes.

## Prerequisites Check

Before you begin, ensure you have installed:

- ✅ Rust (1.70.0+): `rustc --version`
- ✅ Flutter (3.10.0+): `flutter --version`
- ✅ Android SDK (for Android builds)
- ✅ Visual Studio Build Tools (for Windows builds)

## 1. Install Rust Targets

```bash
make setup
```

Or manually:

```bash
rustup target add aarch64-linux-android armv7-linux-androideabi
rustup target add x86_64-pc-windows-msvc
cargo install cargo-ndk
```

## 2. Build the Project

### For Android

```bash
./build.sh android
```

### For Windows

```bash
./build.sh windows
```

### For All Platforms

```bash
./build.sh all
```

## 3. Run the App

### On Android Device/Emulator

```bash
cd app
flutter run -d android
```

### On Windows

```bash
cd app
flutter run -d windows
```

## 4. Verify Installation

The app should display a simple UI with a button that calls Rust code and displays a greeting message.

## Troubleshooting

### Rust library not found

1. Make sure you built the Rust library first: `./build.sh android` or `./build.sh windows`
2. Check that the target directory exists: `ls -la core/target/`

### Android NDK issues

Set environment variables:

```bash
export ANDROID_HOME=$HOME/Android/Sdk
export NDK_HOME=$ANDROID_HOME/ndk/25.1.8937393
```

### Flutter dependencies

If you get dependency errors:

```bash
cd app && flutter clean && flutter pub get
cd ../bridge && dart pub get
```

## Next Steps

- Read [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Start building your app in `/app/lib/main.dart`
- Add Rust functionality in `/core/src/lib.rs`
- Update FFI bindings in `/bridge/lib/bridge.dart`

## Project Structure at a Glance

```
├── app/           # Flutter UI layer
├── core/          # Rust business logic
├── bridge/        # FFI bindings
├── build.sh       # Build automation
└── Makefile       # Development tasks
```

Happy coding! 🚀
