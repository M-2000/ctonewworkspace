.PHONY: help setup build-rust-android build-rust-windows test-rust clean

help:
	@echo "Available targets:"
	@echo "  setup              - Install Rust targets for Android and Windows"
	@echo "  build-rust-android - Build Rust library for Android targets"
	@echo "  build-rust-windows - Build Rust library for Windows target"
	@echo "  test-rust          - Run Rust tests"
	@echo "  clean              - Clean build artifacts"

setup:
	@echo "Installing Rust targets..."
	rustup target add aarch64-linux-android
	rustup target add armv7-linux-androideabi
	rustup target add x86_64-linux-android
	rustup target add i686-linux-android
	rustup target add x86_64-pc-windows-msvc
	@echo "Installing cargo-ndk..."
	cargo install cargo-ndk

build-rust-android:
	@echo "Building Rust library for Android..."
	cd core && cargo build --release --target aarch64-linux-android
	cd core && cargo build --release --target armv7-linux-androideabi

build-rust-windows:
	@echo "Building Rust library for Windows..."
	cd core && cargo build --release --target x86_64-pc-windows-msvc

test-rust:
	@echo "Running Rust tests..."
	cd core && cargo test

clean:
	@echo "Cleaning build artifacts..."
	cd core && cargo clean
	cd app && flutter clean
	rm -rf app/build
	rm -rf bridge/.dart_tool
