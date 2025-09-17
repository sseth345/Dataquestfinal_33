#!/bin/bash

# Insider Threat Detection System Installation Script

set -e

echo "========================================"
echo "Insider Threat Detection System Installer"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "This script should not be run as root for security reasons."
        print_warning "Please run as a regular user with sudo privileges."
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_step "Checking System Requirements"
    
    # Check Python version
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_status "Python version: $PYTHON_VERSION"
        
        # Check if Python 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_status "Python version is compatible"
        else
            print_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 >/dev/null 2>&1; then
        print_error "pip3 is not installed"
        exit 1
    fi
    
    # Check git
    if ! command -v git >/dev/null 2>&1; then
        print_error "git is not installed"
        exit 1
    fi
    
    # Check available disk space (at least 2GB)
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_SPACE" -lt 2000000 ]; then
        print_warning "Less than 2GB of disk space available"
    fi
    
    print_status "System requirements check completed"
}

# Install system dependencies
install_system_deps() {
    print_step "Installing System Dependencies"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get >/dev/null 2>&1; then
            # Debian/Ubuntu
            print_status "Installing packages for Debian/Ubuntu..."
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev \
                python3-pip \
                python3-venv \
                build-essential \
                sqlite3 \
                libsqlite3-dev \
                curl \
                git \
                wget
        elif command -v yum >/dev/null 2>&1; then
            # CentOS/RHEL
            print_status "Installing packages for CentOS/RHEL..."
            sudo yum update -y
            sudo yum install -y \
                python3-devel \
                python3-pip \
                gcc \
                gcc-c++ \
                sqlite \
                sqlite-devel \
                curl \
                git \
                wget
        else
            print_warning "Unsupported Linux distribution. Please install dependencies manually."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        print_status "Installing packages for macOS..."
        if command -v brew >/dev/null 2>&1; then
            brew install python3 sqlite3 git
        else
            print_warning "Homebrew not found. Please install dependencies manually."
        fi
    else
        print_warning "Unsupported operating system. Please install dependencies manually."
    fi
}

# Setup virtual environment
setup_venv() {
    print_step "Setting Up Python Virtual Environment"
    
    if [ -d "venv" ]; then
        print_status "Virtual environment already exists"
        print_status "Activating existing virtual environment..."
        source venv/bin/activate
    else
        print_status "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        print_status "Virtual environment created and activated"
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python Dependencies"
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing from requirements.txt..."
        pip install -r requirements.txt
        print_status "Python dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Setup configuration
setup_config() {
    print_step "Setting Up Configuration"
    
    if [ ! -d "config" ]; then
        mkdir -p config
    fi
    
    if [ ! -f "config/config.yaml" ]; then
        if [ -f "config/config.example.yaml" ]; then
            print_status "Creating configuration file from example..."
            cp config/config.example.yaml config/config.yaml
            print_status "Configuration file created: config/config.yaml"
            print_warning "Please edit config/config.yaml to customize your installation"
        else
            print_error "config/config.example.yaml not found"
            exit 1
        fi
    else
        print_status "Configuration file already exists"
    fi
}

# Create directories
create_directories() {
    print_step "Creating Required Directories"
    
    DIRECTORIES=("data" "logs" "models" "reports" "backups")
    
    for dir in "${DIRECTORIES[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_status "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
    
    # Set permissions
    chmod 755 data logs models reports backups
    print_status "Directory permissions set"
}

# Create systemd service (Linux only)
create_service() {
    print_step "Creating System Service"
    
    if [[ "$OSTYPE" == "linux-gnu"* ]] && command -v systemctl >/dev/null 2>&1; then
        print_status "Creating systemd service..."
        
        INSTALL_DIR=$(pwd)
        SERVICE_FILE="/etc/systemd/system/insider-threat-detection.service"
        
        sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Insider Threat Detection System
After=network.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python src/main.py --mode full
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        print_status "Systemd service created: insider-threat-detection.service"
        print_status "To start the service: sudo systemctl start insider-threat-detection"
        print_status "To enable on boot: sudo systemctl enable insider-threat-detection"
    else
        print_warning "Systemd not available. Service file not created."
    fi
}

# Test installation
test_installation() {
    print_step "Testing Installation"
    
    print_status "Running basic functionality test..."
    
    # Test Python imports
    python -c "
import sys
sys.path.insert(0, 'src')
try:
    from data_collectors.base_collector import BaseCollector
    from ml_models.isolation_forest_model import IsolationForestModel
    from real_time.anomaly_engine import AnomalyEngine
    from alerts.alert_manager import AlertManager
    print('All modules imported successfully')
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_status "Module import test passed"
    else
        print_error "Module import test failed"
        exit 1
    fi
    
    print_status "Installation test completed successfully"
}

# Main installation function
main() {
    echo "Starting installation..."
    
    check_root
    check_requirements
    install_system_deps
    setup_venv
    install_python_deps
    setup_config
    create_directories
    create_service
    test_installation
    
    print_step "Installation Complete!"
    
    echo -e "\n${GREEN}===== Next Steps =====${NC}"
    echo "1. Edit config/config.yaml to customize your installation"
    echo "2. Run the system:"
    echo "   - Full system: python src/main.py --mode full"
    echo "   - Data collection only: python src/main.py --mode collect"
    echo "   - Dashboard only: python src/main.py --mode dashboard"
    echo "   - Train models: python src/main.py --mode train"
    echo ""
    echo "3. Access the web dashboard at: http://localhost:5000"
    echo ""
    echo "4. For production deployment, consider:"
    echo "   - Setting up email alerts in config.yaml"
    echo "   - Running as a system service"
    echo "   - Setting up log rotation"
    echo "   - Configuring firewall rules"
    echo ""
    echo -e "${GREEN}Installation completed successfully!${NC}"
}

# Handle command line arguments
case "${1:-install}" in
    "install")
        main
        ;;
    "test")
        print_step "Running Tests Only"
        setup_venv
        test_installation
        ;;
    "update")
        print_step "Updating Installation"
        setup_venv
        install_python_deps
        print_status "Update completed"
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [install|test|update|help]"
        echo ""
        echo "Commands:"
        echo "  install  - Full installation (default)"
        echo "  test     - Test existing installation"
        echo "  update   - Update Python dependencies"
        echo "  help     - Show this help message"
        ;;
    *)
        print_error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac