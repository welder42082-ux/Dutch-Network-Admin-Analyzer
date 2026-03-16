#!/bin/bash


# Dutch Network Information Tool -
Linux/macOS Launcher
clear



echo "==================================
=============="
echo "      Dutch Network Information
Gathering Tool"
echo "==================================
=============="
echo



# Get the directory where the script is located

SCRIPT_DIR ="$(dirname "$
{BASH_SOURCE[0]}" && pwd)"
cd "$SCRIPT_DIR"



echo "Current directory: $(pwd)"
echo



# Check if Python 3 is installed
if ! command -v python3 &> /dev/null;
then
    echo "Python 3 is not installed"
    echo "Please install Python 3.7+
using your package manager:"
    echo "   Ubuntu/Debian: sudo apt update &&sudo apt install python3
python3-pip"
    echo "   CentOS/RHEL: sudo yum
install python3 python3-pip"
    echo "   macOS: brew install python3"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi



echo "Python 3 found: $(python3 --version)"
echo



# Check if pip is aqvailable
if ! command -v pip3 &> /dev/null; then
    echo "pip3 not found. Installing pip ..."
    sudo apt update && sudo apt install python3-pip -y
fi



echo "Installing required Python packages ..."
pip3 install --user -r requirements.txt



if [ $? -ne 0 ]; then
    echo "Failed to install some
packages. Trying alternative installation ..."
    pip3 install --user psutil netifaces requests
fi



echo
echo "Starting Dutch Network Information Tool..."
echo



# Make sure the logs directory exists
mkdir -p logs



# Run the main script
python3 dutch.py



echo
echo "Script execution completed."
echo "Check the logs folder for output files."
echo
read -p "Press Enter to exit ..."