"""
Setup script for Financial Statement Automation System
Run this file first to setup the complete project
"""
import os
import sys
import subprocess
from pathlib import Path
import shutil

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    
    packages = [
        'pandas>=1.5.0',
        'numpy>=1.21.0', 
        'python-dotenv>=0.19.0',
        'langchain-core>=0.1.0',
        'langchain-openai>=0.0.5',
        'langgraph>=0.0.20',
        'agentops>=0.2.0',
        'openpyxl>=3.0.9',
        'PyPDF2>=3.0.0',
        'python-docx>=0.8.11',
        'Pillow>=9.0.0',
        'cryptography>=3.4.8',
        'pydantic>=1.10.0',
        'jinja2>=3.1.0',
        'streamlit>=1.25.0',
        'plotly>=5.15.0',
        'tabulate>=0.9.0'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to install {package}: {e}")

def create_project_structure():
    """Create the complete project directory structure"""
    print("Creating project structure...")
    
    directories = [
        'agents',
        'config', 
        'utils',
        'tests',
        'templates',
        'data/sample',
        'data/input', 
        'data/processed',
        'output',
        'audit',
        'logs',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create gitkeep files for empty directories
    gitkeep_dirs = ['data/input', 'output', 'audit', 'logs', 'temp']
    for directory in gitkeep_dirs:
        gitkeep_file = Path(directory) / '.gitkeep'
        gitkeep_file.touch()

def create_env_file():
    """Create .env file from template"""
    env_template = """\
# OpenAI API Key (optional - for LLM features)
OPENAI_API_KEY=your_openai_api_key_here

# AgentOps API Key (optional - for monitoring)
AGENTOPS_API_KEY=your_agentops_api_key_here

# System Configuration
LOG_LEVEL=INFO
MAX_FILE_SIZE=104857600

# Security Settings
ENCRYPTION_ENABLED=true
VIRUS_SCAN_ENABLED=true
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("✅ Created .env file")
        print("⚠️  Remember to add your actual API keys to the .env file!")
    else:
        print("✅ .env file already exists")

def verify_installation():
    """Verify the installation is working"""
    print("Verifying installation...")
    
    try:
        # Test core imports
        import pandas as pd
        import numpy as np
        print("✅ Core data libraries available")
        
        # Test optional imports  
        try:
            import streamlit as st
            print("✅ Streamlit available")
        except ImportError:
            print("⚠️ Streamlit not available")
        
        try:
            import agentops
            print("✅ AgentOps available")
        except ImportError:
            print("⚠️ AgentOps not available")
        
        try:
            from jinja2 import Template
            print("✅ Jinja2 available")
        except ImportError:
            print("⚠️ Jinja2 not available")
        
        # Test project structure
        required_files = [
            'workflow.py',
            'main.py', 
            'streamlit_app.py',
            'agents/__init__.py',
            'config/settings.py'
        ]
        
        all_files_exist = True
        for file_path in required_files:
            if Path(file_path).exists():
                print(f"✅ {file_path}")
            else:
                print(f"❌ {file_path} missing")
                all_files_exist = False
        
        if all_files_exist:
            print("✅ All core files present")
            return True
        else:
            print("❌ Some files are missing")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main setup process"""
    print("=" * 60)
    print("FINANCIAL STATEMENT AUTOMATION SYSTEM SETUP")
    print("=" * 60)
    
    # Step 1: Create project structure
    create_project_structure()
    
    # Step 2: Install dependencies
    install_dependencies()
    
    # Step 3: Create environment file
    create_env_file()
    
    # Step 4: Verify installation
    if verify_installation():
        print("\n" + "=" * 60)
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Edit .env file with your actual API keys")
        print("2. Run: python main.py")
        print("3. Or run: streamlit run streamlit_app.py")
        print("\nFor AgentOps monitoring:")
        print("1. Sign up at https://agentops.ai")
        print("2. Get your API key")
        print("3. Add it to the .env file")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("SETUP COMPLETED WITH WARNINGS")
        print("=" * 60)
        print("Some components may not work properly.")
        print("Please check the error messages above.")
        print("=" * 60)

if __name__ == "__main__":
    main()