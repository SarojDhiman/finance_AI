"""
Configuration settings for Financial Statement Automation System
"""
import os
from pathlib import Path

# Try to load environment variables, but don't fail if dotenv isn't available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not available. Using system environment variables only.")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "output"
AUDIT_DIR = PROJECT_ROOT / "audit"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
INPUT_DATA_DIR = DATA_DIR / "input"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")

# File processing settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 104857600))  # 100MB
SUPPORTED_FORMATS = ['.xlsx', '.xls', '.csv', '.pdf', '.png', '.jpg', '.jpeg']

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# AgentOps configuration
AGENTOPS_CONFIG = {
    "auto_start_session": True,
    "instrument_llm_calls": True,
    "max_wait_time": 30,
    "api_endpoint": "https://api.agentops.ai"
}

# Validation settings
VALIDATION_TOLERANCE = 0.01  # For balance validation
MIN_ACCOUNT_NAME_LENGTH = 2
MAX_DECIMAL_PLACES = 2

# Template mappings
ACCOUNT_CATEGORIES = {
    'assets': ['cash', 'bank', 'receivable', 'inventory', 'equipment', 'building', 'assets'],
    'liabilities': ['payable', 'debt', 'loan', 'liability', 'accrued'],
    'equity': ['equity', 'capital', 'retained', 'earnings'],
    'revenue': ['revenue', 'income', 'sales', 'turnover'],
    'expenses': ['expense', 'cost', 'salary', 'rent', 'utilities']
}

# Security settings
ENCRYPTION_ENABLED = True
VIRUS_SCAN_ENABLED = True

# Ensure directories exist
for directory in [DATA_DIR, TEMPLATES_DIR, OUTPUT_DIR, AUDIT_DIR, SAMPLE_DATA_DIR, INPUT_DATA_DIR, PROCESSED_DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY not set in environment variables")
    
    if not AGENTOPS_API_KEY:
        errors.append("AGENTOPS_API_KEY not set (optional but recommended)")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True