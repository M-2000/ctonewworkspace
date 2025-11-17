cmake_minimum_required(VERSION 3.10)

project(bridge)

set(RUST_TARGET_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../core/target")

if(ANDROID_ABI STREQUAL "arm64-v8a")
    set(RUST_TARGET "aarch64-linux-android")
else()
    message(FATAL_ERROR "Unsupported Android ABI: ${ANDROID_ABI}. Only arm64-v8a is supported.")
endif()

set(RUST_LIB_PATH "${RUST_TARGET_DIR}/${RUST_TARGET}/release/libcore.so")

add_library(core SHARED IMPORTED)
set_target_properties(core PROPERTIES IMPORTED_LOCATION ${RUST_LIB_PATH})

add_custom_target(build_rust ALL
    COMMAND cargo build --release --target ${RUST_TARGET}
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../core
    COMMENT "Building Rust library for ${RUST_TARGET}"
)

add_dependencies(core build_rust)
