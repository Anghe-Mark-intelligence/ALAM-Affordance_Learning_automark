#!/bin/bash

# Update package list
sudo apt update

# Install dependencies for GTK and OpenCV
echo "Installing GTK and OpenCV dependencies..."

# Install GTK 3
sudo apt install -y \
    libgtk-3-dev \
    pkg-config \
    libglib2.0-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libcairo2-dev

# Install OpenCV dependencies
sudo apt install -y \
    libopencv-dev \
    libopencv-core-dev \
    libopencv-highgui-dev \
    libopencv-imgproc-dev \
    libopencv-video-dev \
    libopencv-features2d-dev \
    libopencv-calib3d-dev

# Install other dependencies for development (if not already installed)
sudo apt install -y \
    build-essential \
    cmake \
    g++ \
    gcc \
    make \
    libopencv-dev \
    libopencv-core-dev \
    libopencv-imgproc-dev \
    libopencv-video-dev

# Install video capture library (opencv will be able to use it)
sudo apt install -y \
    v4l-utils

# Verify if GTK and OpenCV are correctly installed
echo "Verifying GTK installation..."
pkg-config --modversion gtk+-3.0

echo "Verifying OpenCV installation..."
pkg-config --modversion opencv4

echo "Installation completed successfully!"
