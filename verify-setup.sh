#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==================================="
echo "Flutter + Rust Workspace Verification"
echo "==================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_command() {
    local cmd=$1
    local name=$2
    local required=$3
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $name: $(command -v $cmd)"
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} $name: NOT FOUND (REQUIRED)"
            return 1
        else
            echo -e "${YELLOW}⚠${NC} $name: NOT FOUND (OPTIONAL)"
            return 0
        fi
    fi
}

check_file() {
    local file=$1
    local name=$2
    
    if [ -f "$SCRIPT_DIR/$file" ]; then
        echo -e "${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "${RED}✗${NC} $name: NOT FOUND"
        return 1
    fi
}

check_dir() {
    local dir=$1
    local name=$2
    
    if [ -d "$SCRIPT_DIR/$dir" ]; then
        echo -e "${GREEN}✓${NC} $name"
        return 0
    else
        echo -e "${RED}✗${NC} $name: NOT FOUND"
        return 1
    fi
}

errors=0

echo "Checking Required Tools:"
echo "------------------------"
check_command "rustc" "Rust" "true" || ((errors++))
check_command "cargo" "Cargo" "true" || ((errors++))
check_command "flutter" "Flutter" "true" || ((errors++))
check_command "dart" "Dart" "true" || ((errors++))

echo ""
echo "Checking Optional Tools:"
echo "------------------------"
check_command "cargo-ndk" "cargo-ndk (for Android)" "false"
check_command "cmake" "CMake (for Windows)" "false"
check_command "git" "Git" "false"

echo ""
echo "Checking Workspace Structure:"
echo "------------------------------"
check_dir "app" "Flutter app directory" || ((errors++))
check_dir "core" "Rust core directory" || ((errors++))
check_dir "bridge" "Bridge directory" || ((errors++))

echo ""
echo "Checking Key Files:"
echo "-------------------"
check_file "app/pubspec.yaml" "App pubspec.yaml" || ((errors++))
check_file "app/lib/main.dart" "App main.dart" || ((errors++))
check_file "core/Cargo.toml" "Core Cargo.toml" || ((errors++))
check_file "core/src/lib.rs" "Core lib.rs" || ((errors++))
check_file "bridge/pubspec.yaml" "Bridge pubspec.yaml" || ((errors++))
check_file "bridge/lib/bridge.dart" "Bridge bridge.dart" || ((errors++))
check_file "README.md" "README.md" || ((errors++))
check_file ".gitignore" ".gitignore" || ((errors++))

echo ""
echo "Checking Rust Targets:"
echo "----------------------"
if command -v rustc &> /dev/null; then
    if rustup target list | grep -q "aarch64-linux-android (installed)"; then
        echo -e "${GREEN}✓${NC} aarch64-linux-android target"
    else
        echo -e "${YELLOW}⚠${NC} aarch64-linux-android target not installed"
        echo "  Run: rustup target add aarch64-linux-android"
    fi
    
    if rustup target list | grep -q "x86_64-pc-windows-msvc (installed)"; then
        echo -e "${GREEN}✓${NC} x86_64-pc-windows-msvc target"
    else
        echo -e "${YELLOW}⚠${NC} x86_64-pc-windows-msvc target not installed"
        echo "  Run: rustup target add x86_64-pc-windows-msvc"
    fi
else
    echo -e "${RED}✗${NC} Cannot check Rust targets (rustc not found)"
fi

echo ""
echo "==================================="
if [ $errors -eq 0 ]; then
    echo -e "${GREEN}All essential checks passed!${NC}"
    echo "You can now build and run the project."
    echo ""
    echo "Next steps:"
    echo "  1. Install any missing Rust targets: make setup"
    echo "  2. Build the project: ./build.sh [android|windows|all]"
    echo "  3. Run the app: cd app && flutter run"
    exit 0
else
    echo -e "${RED}Found $errors error(s)${NC}"
    echo "Please fix the issues above before proceeding."
    exit 1
fi
