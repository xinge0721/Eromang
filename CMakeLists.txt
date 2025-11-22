cmake_minimum_required(VERSION 3.15)
project(EromangDecoders VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set build type if not specified
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
if(MSVC)
    add_compile_options(/W4 /O2)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    add_compile_options(-Wall -Wextra -O3)
endif()

# Find Python
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Find pybind11
find_package(pybind11 CONFIG REQUIRED)

# Find OpenCV (optional, for image processing)
find_package(OpenCV QUIET)
if(OpenCV_FOUND)
    message(STATUS "OpenCV found: ${OpenCV_VERSION}")
    add_definitions(-DHAVE_OPENCV)
else()
    message(STATUS "OpenCV not found. Image decoder will use basic implementation.")
endif()

# Find FFmpeg (optional, for video processing)
# Note: FFmpeg detection is platform-specific
if(WIN32)
    # On Windows, you may need to set FFMPEG_ROOT manually
    set(FFMPEG_ROOT "" CACHE PATH "Path to FFmpeg installation")
    if(EXISTS "${FFMPEG_ROOT}/include/libavcodec/avcodec.h")
        set(FFMPEG_FOUND TRUE)
        set(FFMPEG_INCLUDE_DIRS "${FFMPEG_ROOT}/include")
        set(FFMPEG_LIBRARIES
            "${FFMPEG_ROOT}/lib/avcodec.lib"
            "${FFMPEG_ROOT}/lib/avformat.lib"
            "${FFMPEG_ROOT}/lib/avutil.lib"
            "${FFMPEG_ROOT}/lib/swscale.lib"
        )
        message(STATUS "FFmpeg found at: ${FFMPEG_ROOT}")
        add_definitions(-DHAVE_FFMPEG)
    else()
        message(STATUS "FFmpeg not found. Video decoder will not be built.")
    endif()
endif()

# Include directories
include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders/cpp
    ${Python_INCLUDE_DIRS}
)

# Source files
set(IMAGE_DECODER_SOURCES
    src/core/decoders/cpp/image_decoder.cpp
    src/core/decoders/cpp/bindings.cpp
)

set(VIDEO_DECODER_SOURCES
    src/core/decoders/cpp/video_decoder.cpp
)

set(ARCHIVE_DECODER_SOURCES
    src/core/decoders/cpp/archive_decoder.cpp
)

# Image Decoder Module
pybind11_add_module(image_decoder ${IMAGE_DECODER_SOURCES})
target_include_directories(image_decoder PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders/cpp)

if(OpenCV_FOUND)
    target_link_libraries(image_decoder PRIVATE ${OpenCV_LIBS})
    target_include_directories(image_decoder PRIVATE ${OpenCV_INCLUDE_DIRS})
endif()

# Set output directory
set_target_properties(image_decoder PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders
)

# Video Decoder Module (optional, only if FFmpeg is found)
if(FFMPEG_FOUND)
    pybind11_add_module(video_decoder ${VIDEO_DECODER_SOURCES})
    target_include_directories(video_decoder PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders/cpp
        ${FFMPEG_INCLUDE_DIRS}
    )
    target_link_libraries(video_decoder PRIVATE ${FFMPEG_LIBRARIES})

    set_target_properties(video_decoder PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders
    )
endif()

# Archive Decoder Module (placeholder for future implementation)
# pybind11_add_module(archive_decoder ${ARCHIVE_DECODER_SOURCES})
# target_include_directories(archive_decoder PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders/cpp)
# set_target_properties(archive_decoder PROPERTIES
#     LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders
#     RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/core/decoders
# )

# Installation
install(TARGETS image_decoder
    LIBRARY DESTINATION src/core/decoders
    RUNTIME DESTINATION src/core/decoders
)

if(FFMPEG_FOUND)
    install(TARGETS video_decoder
        LIBRARY DESTINATION src/core/decoders
        RUNTIME DESTINATION src/core/decoders
    )
endif()

# Print configuration summary
message(STATUS "")
message(STATUS "=== Eromang C++ Decoders Configuration ===")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Python version: ${Python_VERSION}")
message(STATUS "Python include: ${Python_INCLUDE_DIRS}")
message(STATUS "pybind11 version: ${pybind11_VERSION}")
message(STATUS "OpenCV: ${OpenCV_FOUND}")
if(WIN32)
    message(STATUS "FFmpeg: ${FFMPEG_FOUND}")
endif()
message(STATUS "==========================================")
message(STATUS "")
