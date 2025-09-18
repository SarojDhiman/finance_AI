"""
Logging configuration for Financial Statement Automation System
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from .settings import LOG_LEVEL, LOG_FORMAT, PROJECT_ROOT

def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    log_filename = f"financial_automation_{datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = logs_dir / log_filename
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(log_filepath),
            logging.StreamHandler()  # Console output
        ]
    )
    
    # Create specialized loggers
    loggers = {
        'security': logging.getLogger('financial_automation.security'),
        'ingestion': logging.getLogger('financial_automation.ingestion'), 
        'validation': logging.getLogger('financial_automation.validation'),
        'template': logging.getLogger('financial_automation.template'),
        'output': logging.getLogger('financial_automation.output'),
        'audit': logging.getLogger('financial_automation.audit'),
        'workflow': logging.getLogger('financial_automation.workflow'),
        'agentops': logging.getLogger('financial_automation.agentops')
    }
    
    # Set levels for different components
    if LOG_LEVEL == 'DEBUG':
        for logger in loggers.values():
            logger.setLevel(logging.DEBUG)
    
    return loggers

def get_logger(name: str):
    """Get a logger instance"""
    return logging.getLogger(f'financial_automation.{name}')