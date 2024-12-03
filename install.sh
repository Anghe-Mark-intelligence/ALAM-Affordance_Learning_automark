#markmagic1
#https://github.com/Anghe-Mark-intelligence/ALAM-Affordance_Learning_automark/tree/main
#!/bin/bash

# This script will install the necessary dependencies for controlling a 6-axis robotic arm.
# It assumes you are using an Ubuntu-based system. If you are using another distribution, modify the commands accordingly.

# Check if the script is running with sudo privileges
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root or with sudo"
    exit 1
fi

# Update system packages
echo "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install necessary dependencies
echo "Installing dependencies..."

# Install general build tools and libraries
apt-get install -y build-essential cmake git

# Install ROS (Robot Operating System)
echo "Installing ROS..."
# ROS installation steps (this assumes ROS Noetic on Ubuntu 20.04, you can change the version if needed)
sh -c 'echo "deb [arch=amd64] http://packages.ros.org/ros2/ubuntu main" > /etc/apt/sources.list.d/ros2-latest.list'
sudo apt update
sudo apt install -y ros-noetic-desktop-full

# Install additional dependencies for controlling the robotic arm
echo "Installing additional libraries for robotic arm control..."
apt-get install -y libboost-all-dev libeigen3-dev libsdl2-dev libpcl-dev libopencv-dev

# Install Python dependencies (for any Python-based control or visualization)
echo "Installing Python dependencies..."
apt-get install -y python3-pip
pip3 install --upgrade pip
pip3 install numpy scipy matplotlib opencv-python

# Install dependencies for communication and control (like libserial)
echo "Installing serial communication libraries..."
apt-get install -y libserial-dev

# Install visualization libraries (e.g., for visualizing the robotic arm)
apt-get install -y libqt5widgets5 qtbase5-dev

# Setup directories for configuration and logging
echo "Setting up directories for configuration and logging..."
mkdir -p /home/$USER/robot_config
mkdir -p /home/$USER/robot_logs

# Copy the robot arm configuration file (Make sure you have the 'robot_arm_config.cfg' in the same directory as this script)
echo "Copying configuration file..."
cp robot_arm_config.cfg /home/$USER/robot_config/

# Create a symbolic link for easy access to the configuration
ln -s /home/$USER/robot_config/robot_arm_config.cfg /home/$USER/robot_config/latest_config.cfg

# Set up environment variables (add this to .bashrc for persistence)
echo "Setting up environment variables..."
echo "export ROBOT_CONFIG_DIR=/home/$USER/robot_config" >> /home/$USER/.bashrc
echo "export ROBOT_LOG_DIR=/home/$USER/robot_logs" >> /home/$USER/.bashrc
source /home/$USER/.bashrc

# Finish installation
echo "Installation complete!"

# Optionally, you could also start a service or open the ROS workspace here if needed.
# For example, you could start the ROS core:
# roscore &
