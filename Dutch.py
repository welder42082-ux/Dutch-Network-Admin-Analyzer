#!/usr/bin/env python3
"""
Dutch - Network Information Gathering Tool
Author: System Administrator
Description: Comprehensive network and system information gathering tool
Version: 1.0.0
Usage: python dutch.py [options]

LEGAL NOTICE: This tool should only be used on systems you own or have 
explicit permission to analyze. Unauthorized system access is illegal.
"""

import os
import sys
import json
import csv
import time
import logging
import platform
import subprocess
import socket
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, List, Optional, Any
import argparse

try:
    import psutil
    import netifaces
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("Warning: Some dependencies not available. Install with: pip install psutil netifaces")

class NetworkInfoGatherer:
    """Main class for gathering network information"""
    
    def __init__(self, output_file: str = "output.txt", verbose: bool = False):
        self.output_file = output_file
        self.verbose = verbose
        self.info_data = {}
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        log_level = logging.DEBUG if self.verbose else logging.INFO
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(f'logs/dutch_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Gather basic system information"""
        self.logger.info("Gathering system information...")
        
        system_info = {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version
        }
        
        if DEPENDENCIES_AVAILABLE:
            try:
                system_info.update({
                    'cpu_count': psutil.cpu_count(),
                    'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat()
                })
            except Exception as e:
                self.logger.warning(f"Could not gather extended system info: {e}")
        
        return system_info
    
    def get_network_interfaces(self) -> Dict[str, List[Dict]]:
        """Get all network interfaces and their details"""
        self.logger.info("Gathering network interface information...")
        interfaces = {}
        
        if DEPENDENCIES_AVAILABLE:
            try:
                for interface in netifaces.interfaces():
                    interface_info = []
                    addrs = netifaces.ifaddresses(interface)
                    
                    # IPv4 addresses
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            interface_info.append({
                                'type': 'IPv4',
                                'address': addr.get('addr', ''),
                                'netmask': addr.get('netmask', ''),
                                'broadcast': addr.get('broadcast', '')
                            })
                    
                    # IPv6 addresses
                    if netifaces.AF_INET6 in addrs:
                        for addr in addrs[netifaces.AF_INET6]:
                            interface_info.append({
                                'type': 'IPv6',
                                'address': addr.get('addr', ''),
                                'netmask': addr.get('netmask', '')
                            })
                    
                    # MAC address
                    if netifaces.AF_LINK in addrs:
                        for addr in addrs[netifaces.AF_LINK]:
                            interface_info.append({
                                'type': 'MAC',
                                'address': addr.get('addr', '')
                            })
                    
                    interfaces[interface] = interface_info
                    
            except Exception as e:
                self.logger.error(f"Error gathering network interfaces: {e}")
        else:
            # Fallback method without netifaces
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['ipconfig', '/all'], 
                                          capture_output=True, text=True, timeout=30)
                    interfaces['ipconfig_output'] = [{'type': 'raw', 'data': result.stdout}]
                else:
                    result = subprocess.run(['ifconfig'], 
                                          capture_output=True, text=True, timeout=30)
                    interfaces['ifconfig_output'] = [{'type': 'raw', 'data': result.stdout}]
            except Exception as e:
                self.logger.error(f"Error with fallback interface gathering: {e}")
        
        return interfaces
    
    def get_public_ip(self) -> Optional[str]:
        """Get external/public IP address"""
        self.logger.info("Attempting to get public IP address...")
        
        services = [
            'https://api.ipify.org',
            'https://ipecho.net/plain',
            'https://icanhazip.com',
            'https://ident.me'
        ]
        
        for service in services:
            try:
                with urllib.request.urlopen(service, timeout=10) as response:
                    public_ip = response.read().decode('utf-8').strip()
                    self.logger.info(f"Public IP obtained from {service}: {public_ip}")
                    return public_ip
            except Exception as e:
                self.logger.debug(f"Failed to get public IP from {service}: {e}")
                continue
        
        self.logger.warning("Could not determine public IP address")
        return None
    
    def get_gateway_info(self) -> Dict[str, Any]:
        """Get default gateway information"""
        self.logger.info("Gathering gateway information...")
        gateway_info = {}
        
        if DEPENDENCIES_AVAILABLE:
            try:
                gateways = netifaces.gateways()
                default_gateway = gateways.get('default', {})
                
                if netifaces.AF_INET in default_gateway:
                    gateway_info['ipv4_gateway'] = default_gateway[netifaces.AF_INET][0]
                    gateway_info['ipv4_interface'] = default_gateway[netifaces.AF_INET][1]
                
                if netifaces.AF_INET6 in default_gateway:
                    gateway_info['ipv6_gateway'] = default_gateway[netifaces.AF_INET6][0]
                    gateway_info['ipv6_interface'] = default_gateway[netifaces.AF_INET6][1]
                    
            except Exception as e:
                self.logger.error(f"Error gathering gateway info: {e}")
        else:
            # Fallback method
            try:
                if platform.system() == "Windows":
                    result = subprocess.run(['route', 'print', '0.0.0.0'], 
                                          capture_output=True, text=True, timeout=30)
                    gateway_info['route_output'] = result.stdout
                else:
                    result = subprocess.run(['route', '-n'], 
                                          capture_output=True, text=True, timeout=30)
                    gateway_info['route_output'] = result.stdout
            except Exception as e:
                self.logger.error(f"Error with fallback gateway gathering: {e}")
        
        return gateway_info
    
    def get_network_adapter_details(self) -> Dict[str, Any]:
        """Get detailed network adapter information"""
        self.logger.info("Gathering network adapter details...")
        adapter_info = {}
        
        if DEPENDENCIES_AVAILABLE:
            try:
                # Network statistics
                net_stats = psutil.net_io_counters(pernic=True)
                for interface, stats in net_stats.items():
                    adapter_info[interface] = {
                        'bytes_sent': stats.bytes_sent,
                        'bytes_recv': stats.bytes_recv,
                        'packets_sent': stats.packets_sent,
                        'packets_recv': stats.packets_recv,
                        'errin': stats.errin,
                        'errout': stats.errout,
                        'dropin': stats.dropin,
                        'dropout': stats.dropout
                    }
            except Exception as e:
                self.logger.error(f"Error gathering adapter details: {e}")
        
        return adapter_info
    
    def get_network_connections(self) -> List[Dict]:
        """Get active network connections"""
        self.logger.info("Gathering network connections...")
        connections = []
        
        if DEPENDENCIES_AVAILABLE:
            try:
                conns = psutil.net_connections(kind='inet')
                for conn in conns:
                    conn_info = {
                        'family': 'IPv4' if conn.family == socket.AF_INET else 'IPv6',
                        'type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP',
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else '',
                        'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else '',
                        'status': conn.status,
                        'pid': conn.pid
                    }
                    connections.append(conn_info)
            except Exception as e:
                self.logger.error(f"Error gathering network connections: {e}")
        
        return connections
    
    def gather_all_info(self) -> Dict[str, Any]:
        """Gather all network and system information"""
        self.logger.info("Starting comprehensive information gathering...")
        
        self.info_data = {
            'system_info': self.get_system_info(),
            'network_interfaces': self.get_network_interfaces(),
            'public_ip': self.get_public_ip(),
            'gateway_info': self.get_gateway_info(),
            'adapter_details': self.get_network_adapter_details(),
            'network_connections': self.get_network_connections()
        }
        
        self.logger.info("Information gathering completed")
        return self.info_data
    
    def format_output(self, data: Dict[str, Any]) -> str:
        """Format the gathered information for readable output"""
        output = []
        output.append("=" * 80)
        output.append("DUTCH - NETWORK INFORMATION GATHERING REPORT")
        output.append("=" * 80)
        output.append(f"Generated: {data['system_info']['timestamp']}")
        output.append(f"Hostname: {data['system_info']['hostname']}")
        output.append("")
        
        # System Information
        output.append("SYSTEM INFORMATION")
        output.append("-" * 40)
        for key, value in data['system_info'].items():
            if key != 'timestamp':
                output.append(f"{key.replace('_', ' ').title()}: {value}")
        output.append("")
        
        # Public IP
        output.append("PUBLIC IP ADDRESS")
        output.append("-" * 40)
        output.append(f"Public IP: {data.get('public_ip', 'Not available')}")
        output.append("")
        
        # Network Interfaces
        output.append("NETWORK INTERFACES")
        output.append("-" * 40)
        for interface, details in data['network_interfaces'].items():
            output.append(f"Interface: {interface}")
            for detail in details:
                if detail['type'] == 'raw':
                    output.append(f"  Raw Data: {detail['data'][:200]}...")
                else:
                    output.append(f"  {detail['type']}: {detail.get('address', '')}")
                    if 'netmask' in detail and detail['netmask']:
                        output.append(f"    Netmask: {detail['netmask']}")
                    if 'broadcast' in detail and detail['broadcast']:
                        output.append(f"    Broadcast: {detail['broadcast']}")
            output.append("")
        
        # Gateway Information
        output.append("GATEWAY INFORMATION")
        output.append("-" * 40)
        gateway_info = data.get('gateway_info', {})
        if gateway_info:
            for key, value in gateway_info.items():
                output.append(f"{key.replace('_', ' ').title()}: {value}")
        else:
            output.append("No gateway information available")
        output.append("")
        
        # Adapter Details
        if data.get('adapter_details'):
            output.append("NETWORK ADAPTER STATISTICS")
            output.append("-" * 40)
            for adapter, stats in data['adapter_details'].items():
                output.append(f"Adapter: {adapter}")
                for stat_name, stat_value in stats.items():
                    output.append(f"  {stat_name.replace('_', ' ').title()}: {stat_value}")
                output.append("")
        
        # Network Connections
        if data.get('network_connections'):
            output.append("ACTIVE NETWORK CONNECTIONS")
            output.append("-" * 40)
            for conn in data['network_connections'][:20]:  # Limit to first 20 connections
                output.append(f"{conn['type']} {conn['local_address']} -> {conn['remote_address']} ({conn['status']})")
            if len(data['network_connections']) > 20:
                output.append(f"... and {len(data['network_connections']) - 20} more connections")
            output.append("")
        
        output.append("=" * 80)
        output.append("END OF REPORT")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def save_to_file(self, content: str, format_type: str = 'txt'):
        """Save the gathered information to file"""
        try:
            if format_type == 'txt':
                with open(self.output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            elif format_type == 'json':
                json_file = self.output_file.replace('.txt', '.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.info_data, f, indent=2, default=str)
            elif format_type == 'csv':
                csv_file = self.output_file.replace('.txt', '.csv')
                self.save_to_csv(csv_file)
            
            self.logger.info(f"Information saved to {self.output_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving to file: {e}")
    
    def save_to_csv(self, csv_file: str):
        """Save network interface information to CSV"""
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Interface', 'Type', 'Address', 'Netmask', 'Broadcast'])
                
                for interface, details in self.info_data['network_interfaces'].items():
                    for detail in details:
                        if detail['type'] != 'raw':
                            writer.writerow([
                                interface,
                                detail['type'],
                                detail.get('address', ''),
                                detail.get('netmask', ''),
                                detail.get('broadcast', '')
                            ])
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {e}")
    
    def run(self):
        """Main execution method"""
        try:
            print("Dutch - Network Information Gathering Tool")
            print("=" * 50)
            
            if not DEPENDENCIES_AVAILABLE:
                print("Warning: Running with limited functionality. Install dependencies for full features.")
                print("Run: pip install psutil netifaces")
                print()
            
            # Gather all information
            data = self.gather_all_info()
            
            # Format output
            formatted_output = self.format_output(data)
            
            # Display summary
            print(f"\nInformation gathering completed!")
            print(f"Hostname: {data['system_info']['hostname']}")
            print(f"Platform: {data['system_info']['platform']}")
            print(f"Public IP: {data.get('public_ip', 'Not available')}")
            print(f"Network Interfaces: {len(data['network_interfaces'])}")
            
            # Save to file
            self.save_to_file(formatted_output, 'txt')
            self.save_to_file('', 'json')  # Also save as JSON
            
            print(f"\nDetailed report saved to: {self.output_file}")
            print(f"JSON data saved to: {self.output_file.replace('.txt', '.json')}")
            
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            print("\nOperation cancelled by user.")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            print(f"Error: {e}")

def create_batch_file():
    """Create Windows batch file for easy execution"""
    batch_content = '''@echo off
echo Starting Dutch Network Information Gatherer...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if not available
echo Checking dependencies...
python -c "import psutil, netifaces" 2>nul
if errorlevel 1 (
    echo Installing required dependencies...
    pip install psutil netifaces
)

REM Run the Dutch tool
echo.
echo Running Dutch Network Information Gatherer...
python dutch.py %*

echo.
echo Process completed. Check output.txt for results.
pause
'''
    
    try:
        with open('run_dutch.bat', 'w') as f:
            f.write(batch_content)
        print("Windows batch file created: run_dutch.bat")
    except Exception as e:
        print(f"Error creating batch file: {e}")

def create_shell_script():
    """Create Unix/Linux shell script for easy execution"""
    shell_content = '''#!/bin/bash

echo "Starting Dutch Network Information Gatherer..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed"
    echo "Please install Python 3 from your package manager"
    exit 1
fi

# Install dependencies if not available
echo "Checking dependencies..."
python3 -c "import psutil, netifaces" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required dependencies..."
    pip3 install psutil netifaces
fi

# Run the Dutch tool
echo
echo "Running Dutch Network Information Gatherer..."
python3 dutch.py "$@"

echo
echo "Process completed. Check output.txt for results."
read -p "Press enter to continue..."
'''
    
    try:
        with open('run_dutch.sh', 'w') as f:
            f.write(shell_content)
        os.chmod('run_dutch.sh', 0o755)  # Make executable
        print("Unix/Linux shell script created: run_dutch.sh")
    except Exception as e:
        print(f"Error creating shell script: {e}")

def create_requirements_file():
    """Create requirements.txt file"""
    requirements_content = '''psutil>=5.8.0
netifaces>=0.11.0
'''
    
    try:
        with open('requirements.txt', 'w') as f:
            f.write(requirements_content)
        print("Requirements file created: requirements.txt")
    except Exception as e:
        print(f"Error creating requirements file: {e}")

def create_autorun_files():
    """Create autorun files for USB"""
    # Windows autorun.inf
    autorun_inf = '''[autorun]
open=run_dutch.bat
icon=dutch.ico
label=Dutch Network Tool
action=Run Dutch Network Information Gatherer
'''
    
    try:
        with open('autorun.inf', 'w') as f:
            f.write(autorun_inf)
        print("Windows autorun file created: autorun.inf")
    except Exception as e:
        print(f"Error creating autorun file: {e}")
    
    # Linux desktop file
    desktop_content = '''[Desktop Entry]
Version=1.0
Type=Application
Name=Dutch Network Tool
Comment=Network Information Gathering Tool
Exec=./run_dutch.sh
Icon=dutch
Terminal=true
Categories=Network;System;
'''
    
    try:
        with open('dutch.desktop', 'w') as f:
            f.write(desktop_content)
        print("Linux desktop file created: dutch.desktop")
    except Exception as e:
        print(f"Error creating desktop file: {e}")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Dutch - Network Information Gathering Tool',
        epilog='Example: python dutch.py -o network_report.txt -v --json'
    )
    
    parser.add_argument('-o', '--output', 
                       default='output.txt',
                       help='Output file name (default: output.txt)')
    parser.add_argument('-v', '--verbose', 
                       action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--json', 
                       action='store_true',
                       help='Also save output in JSON format')
    parser.add_argument('--csv', 
                       action='store_true',
                       help='Also save network interfaces in CSV format')
    parser.add_argument('--create-scripts', 
                       action='store_true',
                       help='Create helper scripts and exit')
    
    args = parser.parse_args()
    
    if args.create_scripts:
        print("Creating helper scripts and files...")
        create_batch_file()
        create_shell_script()
        create_requirements_file()
        create_autorun_files()
        print("Helper files created successfully!")
        return
    
    # Create and run the network info gatherer
    gatherer = NetworkInfoGatherer(output_file=args.output, verbose=args.verbose)
    gatherer.run()
    
    # Save additional formats if requested
    if args.json:
        gatherer.save_to_file('', 'json')
    
    if args.csv:
        gatherer.save_to_file('', 'csv')

if __name__ == "__main__":
    main()