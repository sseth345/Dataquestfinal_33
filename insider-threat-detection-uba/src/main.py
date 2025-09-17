"""
Main application entry point for the Insider Threat Detection System.
"""

import argparse
import logging
import logging.handlers
import os
import sys
import yaml
import signal
import time
from typing import Dict, Any

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from real_time.data_processor import RealTimeDataProcessor
from alerts.alert_manager import AlertManager
from dashboard.app import create_dashboard_app


def setup_logging(config: Dict[str, Any]):
    """
    Setup logging configuration.
    
    Args:
        config: Configuration dictionary
    """
    log_config = config.get('logging', {})
    
    # Create logs directory if it doesn't exist
    log_file = log_config.get('file', 'logs/insider_threat_detection.log')
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=log_config.get('max_bytes', 10485760),  # 10MB
        backupCount=log_config.get('backup_count', 5)
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Reduce noise from some libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        print("Please copy config/config.example.yaml to config/config.yaml and customize it.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file: {e}")
        sys.exit(1)


def create_directories(config: Dict[str, Any]):
    """
    Create necessary directories.
    
    Args:
        config: Configuration dictionary
    """
    directories = [
        'data',
        'logs',
        'models',
        'reports',
        os.path.dirname(config.get('database', {}).get('path', 'data/threat_detection.db'))
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory)


def run_data_collection(config: Dict[str, Any]):
    """
    Run data collection mode.
    
    Args:
        config: Configuration dictionary
    """
    logger = logging.getLogger('DataCollection')
    logger.info("Starting data collection mode")
    
    # Initialize alert manager
    alert_manager = AlertManager(config.get('alerts', {}))
    
    # Initialize real-time data processor
    processor = RealTimeDataProcessor(config.get('real_time', {}))
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, stopping data collection...")
        processor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start the processor
        processor.start()
        
        logger.info("Data collection started. Press Ctrl+C to stop.")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Shutting down data collection...")
        processor.stop()
    except Exception as e:
        logger.error(f"Error in data collection: {str(e)}")
        processor.stop()
        sys.exit(1)


def run_dashboard(config: Dict[str, Any]):
    """
    Run dashboard mode.
    
    Args:
        config: Configuration dictionary
    """
    logger = logging.getLogger('Dashboard')
    logger.info("Starting dashboard mode")
    
    # Initialize components
    alert_manager = AlertManager(config.get('alerts', {}))
    processor = RealTimeDataProcessor(config.get('real_time', {}))
    
    # Create dashboard app
    dashboard = create_dashboard_app(config.get('dashboard', {}))
    dashboard.initialize_components(processor, alert_manager)
    
    # Start data processor in background
    processor.start()
    
    try:
        # Run dashboard
        dashboard_config = config.get('dashboard', {})
        dashboard.run(
            host=dashboard_config.get('host', '0.0.0.0'),
            port=dashboard_config.get('port', 5000),
            debug=dashboard_config.get('debug', False)
        )
    finally:
        processor.stop()


def run_full_system(config: Dict[str, Any]):
    """
    Run the full system (data collection + dashboard).
    
    Args:
        config: Configuration dictionary
    """
    logger = logging.getLogger('FullSystem')
    logger.info("Starting full insider threat detection system")
    
    # Initialize components
    alert_manager = AlertManager(config.get('alerts', {}))
    processor = RealTimeDataProcessor(config.get('real_time', {}))
    
    # Create dashboard app
    dashboard = create_dashboard_app(config.get('dashboard', {}))
    dashboard.initialize_components(processor, alert_manager)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal, stopping system...")
        processor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start data processor
        processor.start()
        
        # Run dashboard
        dashboard_config = config.get('dashboard', {})
        dashboard.run(
            host=dashboard_config.get('host', '0.0.0.0'),
            port=dashboard_config.get('port', 5000),
            debug=dashboard_config.get('debug', False)
        )
    
    except KeyboardInterrupt:
        logger.info("Shutting down system...")
        processor.stop()
    except Exception as e:
        logger.error(f"Error running system: {str(e)}")
        processor.stop()
        sys.exit(1)


def train_models(config: Dict[str, Any]):
    """
    Train machine learning models.
    
    Args:
        config: Configuration dictionary
    """
    logger = logging.getLogger('ModelTraining')
    logger.info("Starting model training")
    
    from ml_models.isolation_forest_model import IsolationForestModel
    from ml_models.autoencoder_model import AutoencoderModel
    
    try:
        # Initialize models
        if_model = IsolationForestModel(config.get('ml_models', {}).get('isolation_forest', {}))
        ae_model = AutoencoderModel(config.get('ml_models', {}).get('autoencoder', {}))
        
        # Load training data
        logger.info("Loading training data...")
        df = if_model.load_data_from_db()
        
        if df.empty:
            logger.warning("No training data available. Please run data collection first.")
            return
        
        logger.info(f"Loaded {len(df)} training samples")
        
        # Preprocess data
        X, y = if_model.preprocess_data(df)
        
        if X.size == 0:
            logger.warning("No valid features extracted from data")
            return
        
        logger.info(f"Preprocessed data: {X.shape[0]} samples, {X.shape[1]} features")
        
        # Train Isolation Forest
        logger.info("Training Isolation Forest model...")
        if_metrics = if_model.train(X)
        logger.info(f"Isolation Forest training completed: {if_metrics}")
        
        # Save Isolation Forest model
        if_path = if_model.save_model("trained")
        logger.info(f"Isolation Forest model saved: {if_path}")
        
        # Train Autoencoder
        logger.info("Training Autoencoder model...")
        ae_metrics = ae_model.train(X)
        logger.info(f"Autoencoder training completed: {ae_metrics}")
        
        # Save Autoencoder model
        ae_path = ae_model.save_model("trained")
        logger.info(f"Autoencoder model saved: {ae_path}")
        
        logger.info("Model training completed successfully")
    
    except Exception as e:
        logger.error(f"Error training models: {str(e)}")
        sys.exit(1)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='Insider Threat Detection System')
    parser.add_argument('--config', '-c', default='config/config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--mode', '-m', choices=['collect', 'dashboard', 'full', 'train'],
                       default='full', help='Operating mode')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    setup_logging(config)
    
    # Create necessary directories
    create_directories(config)
    
    logger = logging.getLogger('Main')
    logger.info(f"Starting Insider Threat Detection System in {args.mode} mode")
    
    try:
        if args.mode == 'collect':
            run_data_collection(config)
        elif args.mode == 'dashboard':
            run_dashboard(config)
        elif args.mode == 'full':
            run_full_system(config)
        elif args.mode == 'train':
            train_models(config)
        else:
            logger.error(f"Unknown mode: {args.mode}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()