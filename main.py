"""
Financial Statement Automation System - Main Application
Run this file to start the system and create sample data
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from workflow import FinancialWorkflow
from utils.data_generator import FinancialDataGenerator
from config.logging_config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger('main')

class FinancialAutomationApp:
    """Main application class for the Financial Statement Automation System"""
    
    def __init__(self):
        self.workflow = None
        self.data_generator = None
        self.logger = logger
        
    def initialize(self):
        """Initialize the system components"""
        try:
            self.logger.info("Initializing Financial Statement Automation System...")
            
            # Initialize workflow
            self.workflow = FinancialWorkflow()
            self.logger.info("Workflow system initialized")
            
            # Initialize data generator
            self.data_generator = FinancialDataGenerator()
            self.logger.info("Data generator initialized")
            
            self.logger.info("System initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            return False
    
    def create_sample_data(self):
        """Create sample datasets for demonstration"""
        self.logger.info("Creating sample datasets...")
        
        try:
            datasets = self.data_generator.create_sample_datasets()
            
            print("\n" + "="*80)
            print("SAMPLE DATASETS CREATED")
            print("="*80)
            
            for name, path in datasets.items():
                print(f"✓ {name}")
                print(f"  File: {path}")
                
                # Get file size
                try:
                    file_size = Path(path).stat().st_size
                    print(f"  Size: {file_size:,} bytes")
                except:
                    pass
                print()
            
            print(f"Total datasets created: {len(datasets)}")
            print("="*80)
            
            return datasets
            
        except Exception as e:
            self.logger.error(f"Sample data creation failed: {e}")
            return {}
    
    def demonstrate_processing(self, sample_files: dict = None):
        """Demonstrate the processing workflow"""
        if not sample_files:
            sample_files = self.data_generator.get_sample_files_list()
            if not sample_files:
                self.logger.warning("No sample files available for demonstration")
                return
        
        print("\n" + "="*80)
        print("WORKFLOW DEMONSTRATION")
        print("="*80)
        
        # Process a few sample files
        files_to_process = list(sample_files.keys())[:2] if isinstance(sample_files, dict) else sample_files[:2]
        
        for i, file_info in enumerate(files_to_process):
            if isinstance(sample_files, dict):
                file_path = sample_files[file_info]
                file_name = file_info
            else:
                file_path = file_info['path']
                file_name = file_info['filename']
            
            print(f"\n{'-'*60}")
            print(f"Processing File {i+1}: {file_name}")
            print(f"Path: {file_path}")
            print(f"{'-'*60}")
            
            try:
                # Process the file
                result = self.workflow.process_file(
                    file_path=file_path,
                    user_id="demo_user",
                    output_formats=['md', 'html', 'xlsx', 'json']
                )
                
                # Display results
                self._display_processing_result(result)
                
            except Exception as e:
                print(f"❌ Processing failed: {e}")
                self.logger.error(f"Demonstration processing failed for {file_path}: {e}")
    
    def _display_processing_result(self, result):
        """Display processing result in a formatted way"""
        print(f"\n📊 PROCESSING RESULT")
        print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        print(f"Session ID: {result.session_id}")
        print(f"Processing Time: {result.processing_time:.2f} seconds")
        
        if result.summary:
            print(f"\n📋 Summary:")
            for key, value in result.summary.items():
                if isinstance(value, float):
                    if 'time' in key.lower():
                        print(f"  {key}: {value:.2f}")
                    elif 'debit' in key.lower() or 'credit' in key.lower():
                        print(f"  {key}: ${value:,.2f}")
                    else:
                        print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {value}")
        
        if result.output_files:
            print(f"\n📁 Output Files ({len(result.output_files)}):")
            for file_path in result.output_files:
                try:
                    file_size = Path(file_path).stat().st_size
                    print(f"  ✓ {Path(file_path).name} ({file_size:,} bytes)")
                except:
                    print(f"  ✓ {Path(file_path).name}")
        
        if result.warnings:
            print(f"\n⚠️ Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  • {warning}")
        
        if result.errors:
            print(f"\n❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  • {error}")
    
    def run_system_health_check(self):
        """Run system health check and display status"""
        print("\n" + "="*80)
        print("SYSTEM HEALTH CHECK")
        print("="*80)
        
        try:
            status = self.workflow.get_system_status()
            
            print(f"System Health: {'✅ HEALTHY' if status['system_healthy'] else '❌ UNHEALTHY'}")
            
            print(f"\nAgent Status:")
            for agent, status_val in status['agents_status'].items():
                print(f"  {agent.capitalize()}: {'✅ Active' if status_val == 'active' else '❌ Inactive'}")
            
            if status.get('recent_activity'):
                activity = status['recent_activity']
                print(f"\nRecent Activity (24h):")
                print(f"  Total Sessions: {activity.get('sessions_today', 0)}")
                print(f"  Successful: {activity.get('successful_sessions', 0)}")
                print(f"  Failed: {activity.get('failed_sessions', 0)}")
            
            if status.get('output_stats'):
                stats = status['output_stats']
                print(f"\nOutput Statistics:")
                print(f"  Total Files: {stats.get('total_files', 0)}")
                print(f"  Total Size: {stats.get('total_size', 0):,} bytes")
                if stats.get('file_types'):
                    print(f"  File Types: {dict(stats['file_types'])}")
            
            if status.get('errors'):
                print(f"\n❌ System Errors:")
                for error in status['errors']:
                    print(f"  • {error}")
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            self.logger.error(f"System health check failed: {e}")
        
        print("="*80)
    
    def run_interactive_demo(self):
        """Run interactive demonstration"""
        print("\n" + "="*80)
        print("INTERACTIVE FINANCIAL STATEMENT AUTOMATION DEMO")
        print("="*80)
        print("This demo will show you the complete workflow from file input to statement generation.")
        print()
        
        # Get sample files
        sample_files = self.data_generator.get_sample_files_list()
        
        if not sample_files:
            print("Creating sample files first...")
            datasets = self.create_sample_data()
            sample_files = self.data_generator.get_sample_files_list()
        
        if not sample_files:
            print("❌ No sample files available. Please check the data generation process.")
            return
        
        print(f"Available sample files ({len(sample_files)}):")
        for i, file_info in enumerate(sample_files):
            print(f"  {i+1}. {file_info['filename']} ({file_info['size']:,} bytes)")
        
        print("\nProcessing first few files automatically...")
        self.demonstrate_processing(sample_files)
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("Check the 'output' folder for generated financial statements.")
        print("Check the 'audit' folder for processing logs and audit trails.")
        print("Run 'streamlit run streamlit_app.py' to start the web interface.")
        print("="*80)

def main():
    """Main entry point"""
    print("Financial Statement Automation System")
    print("=" * 50)
    
    # Create and initialize application
    app = FinancialAutomationApp()
    
    if not app.initialize():
        print("❌ System initialization failed. Please check the logs.")
        return 1
    
    try:
        # Run system health check
        app.run_system_health_check()
        
        # Create sample data
        print("\nCreating sample datasets...")
        datasets = app.create_sample_data()
        
        # Run demonstration
        if datasets:
            app.run_interactive_demo()
        else:
            print("⚠️ No sample data created. Skipping demonstration.")
        
        print(f"\nSystem ready! Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        return 0
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.error(f"Main demo failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()