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

## Tools: WebDAV Incremental Uploader (增量上传器)

A standalone Python tool is provided to incrementally upload files to a WebDAV server and safely archive or delete local files on success.

- Location: tools/oplist-uploader/oplist_uploader_webdav.py
- Example config: tools/oplist-uploader/oplist_uploader_webdav.yaml

Key features
- Recursive upload preserving directory structure under dest_root (e.g. /123/动画)
- Only new files are uploaded; if the same relative path appears again with changed content, it is re-uploaded and overwrites the remote file
- Fingerprint methods: size_mtime (fast) or sha256 (strict)
- State JSON records last uploaded fingerprint and history
- On success: archive to source_dir/.oplist_archive (default) or delete permanently
- Retention cleanup for archive (retention_days)
- Cleans up previously uploaded files that remain at original location
- Optional removal of empty directories after move/delete
- Reliable WebDAV operations: MKCOL per level (405/409 treated as exists), PUT with retries and exponential backoff
- Auth: basic or bearer, configurable verify_ssl, concurrency, timeout, retries

Quick start
1) Copy and edit the example YAML:
   - source_dir: the local directory to scan
   - dest_root: remote root path under the WebDAV base URL (keep leading slash)
   - webdav_base_url + auth fields (basic username/password or bearer token)
   - delete_mode: archive (default) or delete
   - archive_dir: default to <source_dir>/.oplist_archive
   - retention_days: set 0 to disable archive retention cleanup
   - include_globs/exclude_globs: control which files are uploaded
   - fingerprint: size_mtime or sha256
2) Run:
   python3 tools/oplist-uploader/oplist_uploader_webdav.py --config tools/oplist-uploader/oplist_uploader_webdav.yaml

Safety notes (安全提示)
- Default delete_mode is archive. Uploaded files are moved to source_dir/.oplist_archive, preserving relative paths.
- To switch to permanent delete, set delete_mode: delete. Use with caution.
- Archive retention cleanup: set retention_days (e.g., 30). Files older than N days in the archive will be deleted. Set 0 to disable.
- Residual files: files already recorded as uploaded but still present in source_dir will be archived/deleted automatically on the next run.
- Empty directories: enable clean_empty_dirs to remove directories that become empty after moves/deletions.

Scheduling examples
- Cron (hourly):
  0 * * * * /usr/bin/python3 /path/to/repo/tools/oplist-uploader/oplist_uploader_webdav.py --config /etc/oplist_uploader_webdav.yaml >> /var/log/oplist_uploader.log 2>&1

- systemd unit: /etc/systemd/system/oplist-uploader.service
  [Unit]
  Description=WebDAV Oplist Uploader
  After=network-online.target
  Wants=network-online.target

  [Service]
  Type=oneshot
  ExecStart=/usr/bin/python3 /path/to/repo/tools/oplist-uploader/oplist_uploader_webdav.py --config /etc/oplist_uploader_webdav.yaml
  Nice=10

- systemd timer: /etc/systemd/system/oplist-uploader.timer
  [Unit]
  Description=Run op list uploader hourly

  [Timer]
  OnCalendar=hourly
  Persistent=true

  [Install]
  WantedBy=timers.target

Enable timer:
  sudo systemctl daemon-reload
  sudo systemctl enable --now oplist-uploader.timer

## License

See LICENSE file for details.
