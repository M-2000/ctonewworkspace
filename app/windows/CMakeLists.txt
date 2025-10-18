cmake_minimum_required(VERSION 3.14)
project(app LANGUAGES CXX)

set(BINARY_NAME "app")

cmake_policy(SET CMP0063 NEW)

set(CMAKE_INSTALL_RPATH "$ORIGIN/lib")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_C_VISIBILITY_PRESET hidden)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)

get_filename_component(FLUTTER_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../../../flutter" ABSOLUTE)

set(FLUTTER_EPHEMERAL_DIR "${CMAKE_CURRENT_BINARY_DIR}/flutter")

add_subdirectory(${FLUTTER_EPHEMERAL_DIR} flutter)

add_subdirectory("runner")

add_custom_target(flutter_assemble DEPENDS
  "${FLUTTER_EPHEMERAL_DIR}/flutter_windows.dll"
)
