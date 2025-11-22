"""
Eromang - Multi-functional Media Management Software
Setup script for building C++ extensions and Python package
"""

import os
import sys
from pathlib import Path

from setuptools import Extension, find_packages, setup

# Read version from pyproject.toml
try:
    import tomli
except ImportError:
    import tomllib as tomli

with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)
    version = pyproject["project"]["version"]

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# C++ extension modules configuration
cpp_extensions = []

# Check if pybind11 is available
try:
    from pybind11.setup_helpers import Pybind11Extension, build_ext

    # Image Decoder Extension
    image_decoder_ext = Pybind11Extension(
        "eromang_decoders.image_decoder",
        sources=[
            "src/core/decoders/cpp/image_decoder.cpp",
            "src/core/decoders/cpp/bindings.cpp",
        ],
        include_dirs=["src/core/decoders/cpp"],
        extra_compile_args=["/O2"] if sys.platform == "win32" else ["-O3", "-std=c++17"],
        language="c++",
    )

    # Video Decoder Extension (placeholder for future implementation)
    # video_decoder_ext = Pybind11Extension(
    #     "eromang_decoders.video_decoder",
    #     sources=["src/core/decoders/cpp/video_decoder.cpp"],
    #     include_dirs=["src/core/decoders/cpp"],
    #     extra_compile_args=["/O2"] if sys.platform == "win32" else ["-O3", "-std=c++17"],
    #     language="c++",
    # )

    # Archive Decoder Extension (placeholder for future implementation)
    # archive_decoder_ext = Pybind11Extension(
    #     "eromang_decoders.archive_decoder",
    #     sources=["src/core/decoders/cpp/archive_decoder.cpp"],
    #     include_dirs=["src/core/decoders/cpp"],
    #     extra_compile_args=["/O2"] if sys.platform == "win32" else ["-O3", "-std=c++17"],
    #     language="c++",
    # )

    cpp_extensions = [
        image_decoder_ext,
        # video_decoder_ext,  # Uncomment when implemented
        # archive_decoder_ext,  # Uncomment when implemented
    ]

    cmdclass = {"build_ext": build_ext}

except ImportError:
    print("Warning: pybind11 not found. C++ extensions will not be built.")
    print("Install with: pip install pybind11")
    cmdclass = {}

# Setup configuration
setup(
    name="eromang",
    version=version,
    author="Eromang Team",
    description="A multi-functional media management software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/eromang",
    packages=find_packages(where="."),
    package_dir={"": "."},
    ext_modules=cpp_extensions,
    cmdclass=cmdclass,
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.0",
        "SQLAlchemy>=2.0.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "Pillow>=10.2.0",
        "PyMuPDF>=1.23.0",
        "chardet>=5.2.0",
        "watchdog>=4.0.0",
        "pyyaml>=6.0.1",
        "loguru>=0.7.2",
        "pydantic>=2.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.3.0",
            "black>=24.1.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pybind11>=2.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eromang=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Topic :: Multimedia",
    ],
    include_package_data=True,
    zip_safe=False,
)
