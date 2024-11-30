# Network Analyzer Tool

A simple network analyzer tool built with Flask and tcpdump. This tool allows you to capture network packets and analyze them using a web interface.

## Features
- Start and stop packet capture using tcpdump.
- View output directly in the web interface.
- Export captured data as a .pcap file.
- Command library with common tcpdump commands.

## Requirements
- Python 3.x
- Flask

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/network-analyzer.git
   cd network-analyzer

2. Install the required packages:
   pip install -r requirements.txt
3.Run the application:
  python app.py
4. Access the tool in your web browser at http://localhost:5000.

Usage
Select a tcpdump command from the dropdown or enter a custom command, then click "Run Command" to start capturing packets.

Your project directory should look like this:

network_analyzer/
├── app.py
├── requirements.txt
└── README.md
