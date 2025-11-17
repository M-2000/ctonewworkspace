#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_usage() {
    echo "Usage: $0 [android|windows|all]"
    echo ""
    echo "Build the Flutter + Rust hybrid workspace"
    echo ""
    echo "Options:"
    echo "  android   Build for Android platform"
    echo "  windows   Build for Windows platform"
    echo "  all       Build for all platforms"
    exit 1
}

build_rust_android() {
    echo "Building Rust library for Android..."
    cd "$SCRIPT_DIR/core"
    
    if ! command -v cargo &> /dev/null; then
        echo "Error: Rust/Cargo not found. Please install from https://rustup.rs/"
        exit 1
    fi
    
    echo "Building for aarch64-linux-android..."
    cargo build --release --target aarch64-linux-android
    
    echo "Android Rust library (arm64-v8a) built successfully"
}

build_rust_windows() {
    echo "Building Rust library for Windows..."
    cd "$SCRIPT_DIR/core"
    
    if ! command -v cargo &> /dev/null; then
        echo "Error: Rust/Cargo not found. Please install from https://rustup.rs/"
        exit 1
    fi
    
    echo "Building for x86_64-pc-windows-msvc..."
    cargo build --release --target x86_64-pc-windows-msvc
    
    echo "Windows Rust library (MSVC) built successfully"
}

build_flutter() {
    echo "Installing Flutter dependencies..."
    cd "$SCRIPT_DIR/app"
    flutter pub get
    
    cd "$SCRIPT_DIR/bridge"
    dart pub get
    
    echo "Flutter dependencies installed successfully"
}

if [ $# -eq 0 ]; then
    print_usage
fi

case "$1" in
    android)
        build_rust_android
        build_flutter
        ;;
    windows)
        build_rust_windows
        build_flutter
        ;;
    all)
        build_rust_android
        build_rust_windows
        build_flutter
        ;;
    *)
        print_usage
        ;;
esac

echo ""
echo "Build completed successfully!"
echo ""
echo "To run the app:"
echo "  Android: cd app && flutter run -d android"
echo "  Windows: cd app && flutter run -d windows"
