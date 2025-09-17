# Insider Threat Detection Using User Behavior Analytics (UBA)

## Overview
An AI-powered system that continuously monitors user activities to detect abnormal patterns indicating malicious intent or policy violations. The system provides real-time alerts and comprehensive reporting for Security Operations Centers (SOC).

## Problem Statement
Insider threats are difficult to detect as they originate from trusted employees or contractors with legitimate access to systems. This system addresses this challenge by implementing advanced behavioral analytics.

## Features
- **Real-time Data Collection**: Monitors file access, login times, application usage, and system commands
- **AI-Powered Anomaly Detection**: Uses Isolation Forest and Autoencoders to identify behavioral deviations
- **Real-time Alerts**: Immediate notifications for detected anomalies
- **Interactive Dashboard**: Web-based visualization for SOC teams
- **Comprehensive Reporting**: CSV export functionality for detailed analysis
- **Scalable Architecture**: Designed for enterprise deployment

## Architecture
```
├── Data Collection Layer
│   ├── Endpoint Logs
│   ├── Network Logs
│   ├── File Access Monitoring
│   └── System Commands Tracking
├── ML Processing Layer
│   ├── Isolation Forest
│   ├── Autoencoders
│   └── Real-time Anomaly Detection
├── Alert & Reporting Layer
│   ├── Real-time Alerts
│   ├── Dashboard Integration
│   └── CSV Report Generation
└── Visualization Layer
    ├── Web Dashboard
    ├── Real-time Monitoring
    └── Historical Analysis
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd insider-threat-detection-uba
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the system:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your settings
```

4. Initialize the database:
```bash
python src/setup_database.py
```

## Usage

### Start the System
```bash
# Start data collection
python src/main.py --mode collect

# Start real-time monitoring
python src/main.py --mode monitor

# Start dashboard
python src/dashboard/app.py
```

### Access Dashboard
Open your browser and navigate to `http://localhost:5000`

## Configuration
Edit `config/config.yaml` to customize:
- Data sources
- ML model parameters
- Alert thresholds
- Dashboard settings

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License - see LICENSE file for details

## Support
For issues and questions, please create an issue in the repository.