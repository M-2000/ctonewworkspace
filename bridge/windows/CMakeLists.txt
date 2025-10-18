cmake_minimum_required(VERSION 3.14)

project(bridge)

set(RUST_TARGET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../core/target")
set(RUST_TARGET "x86_64-pc-windows-msvc")
set(RUST_LIB_PATH "${RUST_TARGET_DIR}/${RUST_TARGET}/release/core.dll")

add_library(core SHARED IMPORTED)
set_target_properties(core PROPERTIES
    IMPORTED_LOCATION ${RUST_LIB_PATH}
    IMPORTED_IMPLIB "${RUST_TARGET_DIR}/${RUST_TARGET}/release/core.dll.lib"
)

add_custom_target(build_rust ALL
    COMMAND cargo build --release --target ${RUST_TARGET}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../core
    COMMENT "Building Rust library for ${RUST_TARGET}"
)

add_dependencies(core build_rust)
