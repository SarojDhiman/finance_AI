"""
Fixed Streamlit Web Interface for Financial Statement Automation System
Run with: streamlit run streamlit_app.py

Key fixes:
- Fixed threading issue with session state access
- Removed problematic timeout mechanism
- Simplified processing flow
- Better error handling for session state
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import zipfile
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import traceback
import logging
import tempfile
import shutil
import numpy as np
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from workflow import FinancialWorkflow
    from utils.data_generator import FinancialDataGenerator
    from config.settings import OUTPUT_DIR, SAMPLE_DATA_DIR, AUDIT_DIR, TEMPLATES_DIR
except ImportError as e:
    st.error(f"Failed to import required modules: {e}")
    st.info("Please ensure all required modules are installed and available.")
    st.stop()

# Configure Streamlit page
st.set_page_config(
    page_title="Financial Statement Automation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        padding: 2rem 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 2rem;
    }
    .success-banner {
        background: linear-gradient(90deg, #00c851 0%, #007e33 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-banner {
        background: linear-gradient(90deg, #ffbb33 0%, #ff8800 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state with proper defaults"""
    defaults = {
        'workflow': None,
        'data_generator': None,
        'processing_results': [],
        'custom_accounts': [],
        'file_upload_key': 0,
        'system_initialized': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

@st.cache_resource(show_spinner=True)
def initialize_system():
    """Initialize the financial automation system with caching"""
    try:
        # Create necessary directories
        directories = [OUTPUT_DIR, SAMPLE_DATA_DIR, AUDIT_DIR, TEMPLATES_DIR, Path("temp")]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        workflow = FinancialWorkflow()
        data_generator = FinancialDataGenerator()
        
        logger.info("System initialized successfully")
        return workflow, data_generator, None
        
    except Exception as e:
        error_msg = f"System initialization failed: {str(e)}"
        logger.error(error_msg)
        return None, None, error_msg

def create_secure_temp_file(uploaded_file):
    """Create a secure temporary file"""
    try:
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_filename = f"{timestamp}_{uploaded_file.name}"
        temp_path = temp_dir / safe_filename
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return temp_path
        
    except Exception as e:
        logger.error(f"Failed to create temp file: {e}")
        st.error(f"Failed to save uploaded file: {e}")
        return None

def safe_cleanup(file_path):
    """Safely cleanup temporary files"""
    try:
        if file_path and file_path.exists():
            file_path.unlink()
            logger.info(f"Cleaned up temp file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup {file_path}: {e}")

def create_download_zip(file_paths, zip_name="financial_statements.zip"):
    """Create a ZIP file from multiple file paths"""
    zip_buffer = BytesIO()
    
    try:
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    zip_file.write(file_path, os.path.basename(file_path))
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Failed to create ZIP: {e}")
        st.error(f"Failed to create download package: {e}")
        return b""

def display_processing_result(result):
    """Display processing result"""
    if result.success:
        st.markdown(f"""
        <div class="success-banner">
            <h3>✅ Processing Completed Successfully!</h3>
            <p>Session ID: {result.session_id[:8]}...</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Processing Time", f"{result.processing_time:.2f}s")
        
        with col2:
            st.metric("Output Files", len(result.output_files))
        
        with col3:
            if result.summary:
                st.metric("Records Processed", result.summary.get('records_processed', 0))
        
        # Financial summary
        if result.summary:
            st.subheader("Financial Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_debits = result.summary.get('total_debits', 0)
                st.metric("Total Debits", f"${total_debits:,.2f}")
            
            with col2:
                total_credits = result.summary.get('total_credits', 0)
                st.metric("Total Credits", f"${total_credits:,.2f}")
            
            with col3:
                balance_diff = abs(total_debits - total_credits)
                balanced = balance_diff <= 0.01
                st.metric("Balance Status", "✅ Balanced" if balanced else "❌ Not Balanced")
        
        # Download section
        if result.output_files:
            st.subheader("Download Generated Files")
            
            for i, file_path in enumerate(result.output_files):
                if os.path.exists(file_path):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"📁 {os.path.basename(file_path)}")
                        file_size = os.path.getsize(file_path)
                        st.caption(f"Size: {file_size:,} bytes")
                    
                    with col2:
                        try:
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                            
                            st.download_button(
                                label="Download",
                                data=file_data,
                                file_name=os.path.basename(file_path),
                                key=f"download_{i}_{result.session_id}"
                            )
                        except Exception as e:
                            st.error(f"Download failed: {e}")
            
            # ZIP download for multiple files
            if len(result.output_files) > 1:
                zip_data = create_download_zip(result.output_files)
                if zip_data:
                    st.download_button(
                        label="📦 Download All Files (ZIP)",
                        data=zip_data,
                        file_name=f"financial_statements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        key=f"download_zip_{result.session_id}"
                    )
        
        # Display warnings
        if result.warnings:
            st.subheader("⚠️ Warnings")
            for warning in result.warnings:
                st.warning(warning)
    
    else:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #ff4444 0%, #cc0000 100%); color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
            <h3>❌ Processing Failed</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for error in result.errors:
            st.error(error)

def main():
    """Main Streamlit application - FIXED VERSION"""
    
    # Initialize session state first
    initialize_session_state()
    
    # Header
    st.title("📊 Financial Statement Automation System")
    st.markdown("Upload financial data files and generate professional financial statements automatically")
    
    # Initialize system if needed
    if not st.session_state.system_initialized:
        with st.spinner("Initializing system..."):
            workflow, data_generator, error = initialize_system()
            
            if error:
                st.error(f"System initialization failed: {error}")
                st.stop()
            
            # Store in session state
            st.session_state.workflow = workflow
            st.session_state.data_generator = data_generator
            st.session_state.system_initialized = True
        
        st.success("System initialized successfully!")
        st.rerun()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 Upload & Process", 
        "📊 Sample Data", 
        "📋 Templates", 
        "⚙️ System Status"
    ])
    
    # Tab 1: Upload and Process Files - FIXED VERSION
    with tab1:
        st.header("Upload & Process Financial Data")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a financial data file",
            type=['xlsx', 'xls', 'csv', 'pdf'],
            key=f"file_uploader_{st.session_state.file_upload_key}"
        )
        
        if uploaded_file:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Filename:** {uploaded_file.name}")
            with col2:
                st.info(f"**Size:** {uploaded_file.size:,} bytes")
            with col3:
                st.info(f"**Type:** {uploaded_file.type}")
        
        # Processing options
        col1, col2 = st.columns(2)
        
        with col1:
            output_formats = st.multiselect(
                "Select output formats",
                ['md', 'html', 'xlsx', 'json'],
                default=['md', 'html']
            )
        
        with col2:
            template_override = st.selectbox(
                "Force specific template (optional)",
                options=[None] + st.session_state.workflow.list_templates(),
                help="Leave blank for auto-detection"
            )
        
        # Process button - FIXED VERSION
        if uploaded_file is not None and st.button("🚀 Process File", type="primary"):
            # Create secure temporary file
            temp_path = create_secure_temp_file(uploaded_file)
            
            if temp_path:
                try:
                    # Validate file
                    if temp_path.stat().st_size == 0:
                        st.error("Uploaded file is empty")
                        return
                    
                    # Show progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        status_text.text("🔄 Initializing processing...")
                        progress_bar.progress(20)
                        
                        status_text.text("📊 Processing financial data...")
                        progress_bar.progress(60)
                        
                        # FIXED: Direct processing without threading to avoid session state issues
                        result = st.session_state.workflow.process_file(
                            file_path=str(temp_path),
                            user_id=f"streamlit_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            output_formats=output_formats or ['md', 'html'],
                            template_override=template_override
                        )
                        
                        status_text.text("✅ Processing completed!")
                        progress_bar.progress(100)
                        
                        # Store result
                        st.session_state.processing_results.append(result)
                        
                        # Display result
                        st.markdown("---")
                        display_processing_result(result)
                        
                        # Reset file uploader
                        st.session_state.file_upload_key += 1
                        
                    except Exception as e:
                        st.error(f"Processing failed: {e}")
                        logger.error(f"Processing error: {e}")
                        logger.error(traceback.format_exc())
                    
                    finally:
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                
                except Exception as e:
                    st.error(f"File handling failed: {e}")
                
                finally:
                    # Always clean up temp file
                    safe_cleanup(temp_path)
        
        # Recent results
        if st.session_state.processing_results:
            st.markdown("---")
            st.subheader("Recent Processing Results")
            
            for i, result in enumerate(reversed(st.session_state.processing_results[-3:])):
                with st.expander(f"Session {result.session_id[:8]}... ({'✅ Success' if result.success else '❌ Failed'})"):
                    display_processing_result(result)
    
    # Tab 2: Sample Data
    with tab2:
        st.header("Sample Data Generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎲 Generate New Sample Data", type="primary"):
                with st.spinner("Creating sample datasets..."):
                    try:
                        datasets = st.session_state.data_generator.create_sample_datasets()
                        st.success(f"Created {len(datasets)} sample datasets!")
                        
                        for name, path in datasets.items():
                            st.write(f"✅ {name}")
                            
                    except Exception as e:
                        st.error(f"Failed to generate sample data: {e}")
        
        with col2:
            if st.button("📁 Show Sample Files"):
                try:
                    sample_files = st.session_state.data_generator.get_sample_files_list()
                    
                    if sample_files:
                        st.write(f"Found {len(sample_files)} sample files:")
                        
                        for file_info in sample_files:
                            col_a, col_b, col_c = st.columns([3, 1, 1])
                            
                            with col_a:
                                st.write(f"📄 {file_info['filename']}")
                            
                            with col_b:
                                st.write(f"{file_info['size']:,} bytes")
                            
                            with col_c:
                                if st.button("Process", key=f"process_{file_info['filename']}"):
                                    with st.spinner(f"Processing {file_info['filename']}..."):
                                        try:
                                            result = st.session_state.workflow.process_file(
                                                file_path=file_info['path'],
                                                user_id="streamlit_sample_user",
                                                output_formats=['md', 'html', 'xlsx']
                                            )
                                            
                                            st.session_state.processing_results.append(result)
                                            display_processing_result(result)
                                            
                                        except Exception as e:
                                            st.error(f"Processing failed: {e}")
                    else:
                        st.info("No sample files found. Generate some using the button above.")
                        
                except Exception as e:
                    st.error(f"Failed to scan sample files: {e}")
        
        # Custom dataset generator
        st.subheader("Create Custom Dataset")
        
        with st.expander("Custom Account Generator"):
            with st.form("add_account"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    account_name = st.text_input("Account Name")
                
                with col2:
                    account_type = st.selectbox("Type", ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense'])
                
                with col3:
                    amount = st.number_input("Amount", min_value=0.0, step=0.01)
                
                with col4:
                    is_credit = st.checkbox("Credit Balance")
                
                if st.form_submit_button("Add Account"):
                    if account_name and amount > 0:
                        st.session_state.custom_accounts.append({
                            'name': account_name,
                            'type': account_type,
                            'amount': amount,
                            'is_credit': is_credit
                        })
                        st.success(f"Added {account_name}")
                        st.rerun()
            
            # Display current accounts
            if st.session_state.custom_accounts:
                st.write("Custom Accounts:")
                df_custom = pd.DataFrame(st.session_state.custom_accounts)
                st.dataframe(df_custom)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Save as Excel"):
                        try:
                            custom_df = st.session_state.data_generator.generate_custom_dataset(
                                st.session_state.custom_accounts,
                                "custom_dataset.xlsx"
                            )
                            st.success("Custom dataset saved!")
                        except Exception as e:
                            st.error(f"Save failed: {e}")
                
                with col2:
                    if st.button("🚀 Process Custom Data"):
                        try:
                            custom_df = st.session_state.data_generator.generate_custom_dataset(
                                st.session_state.custom_accounts
                            )
                            
                            temp_path = Path("temp") / "custom_data.xlsx"
                            temp_path.parent.mkdir(exist_ok=True)
                            custom_df.to_excel(temp_path, index=False)
                            
                            result = st.session_state.workflow.process_file(
                                str(temp_path),
                                "custom_user",
                                ['md', 'html', 'xlsx']
                            )
                            
                            st.session_state.processing_results.append(result)
                            display_processing_result(result)
                            
                            safe_cleanup(temp_path)
                            
                        except Exception as e:
                            st.error(f"Processing failed: {e}")
                
                with col3:
                    if st.button("🗑️ Clear All"):
                        st.session_state.custom_accounts = []
                        st.rerun()
    
    # Tab 3: Templates
    with tab3:
        st.header("Financial Statement Templates")
        
        templates = st.session_state.workflow.list_templates()
        
        if templates:
            selected_template = st.selectbox("Select template to view", templates)
            
            if selected_template:
                template_info = st.session_state.workflow.validate_template(selected_template)
                
                if template_info.get('exists'):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Template:** {template_info['name']}")
                        st.write(f"**Size:** {template_info['size']} characters")
                        st.write(f"**Lines:** {template_info['lines']}")
                    
                    with col2:
                        st.write("**Variables used:**")
                        for var in template_info.get('variables', []):
                            st.write(f"• `{var}`")
                    
                    with st.expander("View Template Content"):
                        try:
                            with open(template_info['path'], 'r') as f:
                                content = f.read()
                            st.code(content, language='markdown')
                        except Exception as e:
                            st.error(f"Could not load template: {e}")
                else:
                    st.error("Template not found")
        else:
            st.warning("No templates available")
    
    # Tab 4: System Status
    with tab4:
        st.header("System Status & Health")
        
        if st.button("🔄 Refresh Status"):
            st.rerun()
        
        try:
            status = st.session_state.workflow.get_system_status()
            
            # System health
            health_color = "🟢" if status['system_healthy'] else "🔴"
            st.markdown(f"## {health_color} System Status: {'Healthy' if status['system_healthy'] else 'Unhealthy'}")
            
            # Agent status
            st.subheader("Agent Status")
            agent_cols = st.columns(len(status['agents_status']))
            
            for i, (agent, agent_status) in enumerate(status['agents_status'].items()):
                with agent_cols[i]:
                    status_icon = "✅" if agent_status == 'active' else "❌"
                    st.write(f"{status_icon} {agent.capitalize()}")
            
            # System errors
            if status.get('errors'):
                st.subheader("System Errors")
                for error in status['errors']:
                    st.error(error)
            
            # File system status
            st.subheader("File System")
            
            dirs_to_check = {
                'Output': OUTPUT_DIR,
                'Sample Data': SAMPLE_DATA_DIR,
                'Audit': AUDIT_DIR,
                'Templates': TEMPLATES_DIR
            }
            
            for name, directory in dirs_to_check.items():
                if directory.exists():
                    file_count = len(list(directory.glob('*')))
                    st.write(f"✅ {name}: {file_count} files")
                else:
                    st.write(f"❌ {name}: Directory not found")
            
            # Cleanup options
            st.subheader("Maintenance")
            
            if st.button("🧹 Cleanup Old Files"):
                try:
                    cleanup_result = st.session_state.workflow.cleanup_old_data(days_old=7)
                    st.success("Cleanup completed!")
                    st.write(f"Files deleted: {cleanup_result['total_files_deleted']}")
                    st.write(f"Space freed: {cleanup_result['total_space_freed']:,} bytes")
                except Exception as e:
                    st.error(f"Cleanup failed: {e}")
        
        except Exception as e:
            st.error(f"Could not retrieve system status: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Financial Statement Automation System** | Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
# """
# Streamlit Web Interface for Financial Statement Automation System
# Run with: streamlit run streamlit_app.py
# """
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# import zipfile
# from io import BytesIO
# import json
# import os
# from pathlib import Path
# import sys

# # Add project root to path
# project_root = Path(__file__).parent
# sys.path.insert(0, str(project_root))

# from workflow import FinancialWorkflow
# from utils.data_generator import FinancialDataGenerator
# from config.settings import OUTPUT_DIR, SAMPLE_DATA_DIR, AUDIT_DIR, TEMPLATES_DIR

# # Configure Streamlit page
# st.set_page_config(
#     page_title="Financial Statement Automation",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Initialize session state
# if 'workflow' not in st.session_state:
#     st.session_state.workflow = None
# if 'data_generator' not in st.session_state:
#     st.session_state.data_generator = None
# if 'processing_results' not in st.session_state:
#     st.session_state.processing_results = []

# @st.cache_resource
# def initialize_system():
#     """Initialize the financial automation system"""
#     try:
#         workflow = FinancialWorkflow()
#         data_generator = FinancialDataGenerator()
#         return workflow, data_generator, None
#     except Exception as e:
#         return None, None, str(e)

# def create_download_zip(file_paths, zip_name="financial_statements.zip"):
#     """Create a ZIP file from multiple file paths"""
#     zip_buffer = BytesIO()
    
#     with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
#         for file_path in file_paths:
#             if os.path.exists(file_path):
#                 zip_file.write(file_path, os.path.basename(file_path))
    
#     zip_buffer.seek(0)
#     return zip_buffer.getvalue()

# def display_processing_result(result):
#     """Display processing result in Streamlit"""
#     if result.success:
#         st.success(f"Processing completed successfully! (Session: {result.session_id[:8]}...)")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             st.metric("Processing Time", f"{result.processing_time:.2f}s")
#             st.metric("Output Files", len(result.output_files))
        
#         with col2:
#             if result.summary:
#                 st.metric("Records Processed", result.summary.get('records_processed', 0))
#                 st.metric("Template Used", result.summary.get('template_used', 'Unknown'))
        
#         # Display financial summary if available
#         if result.summary:
#             st.subheader("Financial Summary")
#             col1, col2, col3 = st.columns(3)
            
#             with col1:
#                 total_debits = result.summary.get('total_debits', 0)
#                 st.metric("Total Debits", f"${total_debits:,.2f}")
            
#             with col2:
#                 total_credits = result.summary.get('total_credits', 0)
#                 st.metric("Total Credits", f"${total_credits:,.2f}")
            
#             with col3:
#                 balance_diff = abs(total_debits - total_credits)
#                 balanced = balance_diff <= 0.01
#                 st.metric("Balance Status", "✅ Balanced" if balanced else "❌ Not Balanced")
        
#         # Download section
#         if result.output_files:
#             st.subheader("Generated Files")
            
#             # Create download buttons for individual files
#             for file_path in result.output_files:
#                 if os.path.exists(file_path):
#                     with open(file_path, 'rb') as f:
#                         file_data = f.read()
                    
#                     st.download_button(
#                         label=f"📁 Download {os.path.basename(file_path)}",
#                         data=file_data,
#                         file_name=os.path.basename(file_path),
#                         key=f"download_{os.path.basename(file_path)}_{result.session_id}"
#                     )
            
#             # Create ZIP download for all files
#             if len(result.output_files) > 1:
#                 zip_data = create_download_zip(result.output_files)
#                 st.download_button(
#                     label="📦 Download All Files (ZIP)",
#                     data=zip_data,
#                     file_name=f"financial_statements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
#                     mime="application/zip",
#                     key=f"download_zip_{result.session_id}"
#                 )
        
#         # Display warnings
#         if result.warnings:
#             st.warning("Warnings detected:")
#             for warning in result.warnings:
#                 st.write(f"⚠️ {warning}")
    
#     else:
#         st.error("Processing failed!")
#         for error in result.errors:
#             st.write(f"❌ {error}")

# def main():
#     """Main Streamlit application"""
    
#     # Header
#     st.title("📊 Financial Statement Automation System")
#     st.markdown("Upload financial data files and generate professional financial statements automatically")
    
#     # Initialize system
#     if st.session_state.workflow is None:
#         with st.spinner("Initializing system..."):
#             workflow, data_generator, error = initialize_system()
            
#             if error:
#                 st.error(f"System initialization failed: {error}")
#                 st.stop()
            
#             st.session_state.workflow = workflow
#             st.session_state.data_generator = data_generator
        
#         st.success("System initialized successfully!")
    
#     # Sidebar
#     st.sidebar.title("Navigation")
    
#     # Main tabs
#     tab1, tab2, tab3, tab4, tab5 = st.tabs([
#         "📤 Upload & Process", 
#         "📊 Sample Data", 
#         "📋 Templates", 
#         "📈 Analytics", 
#         "⚙️ System Status"
#     ])
    
#     # Tab 1: Upload and Process Files
#     with tab1:
#         st.header("Upload Financial Data")
        
#         # File uploader
#         uploaded_file = st.file_uploader(
#             "Choose a financial data file",
#             type=['xlsx', 'xls', 'csv', 'pdf'],
#             help="Supported formats: Excel (.xlsx, .xls), CSV (.csv), PDF (.pdf)"
#         )
        
#         # Processing options
#         col1, col2 = st.columns(2)
        
#         with col1:
#             output_formats = st.multiselect(
#                 "Select output formats",
#                 ['md', 'html', 'xlsx', 'json'],
#                 default=['md', 'html'],
#                 help="Choose which formats to generate"
#             )
        
#         with col2:
#             template_override = st.selectbox(
#                 "Force specific template (optional)",
#                 options=[None] + st.session_state.workflow.list_templates(),
#                 help="Leave blank for auto-detection"
#             )
        
#         # Process button
#         if uploaded_file is not None and st.button("🚀 Process File", type="primary"):
#             # Save uploaded file temporarily
#             temp_path = Path("temp") / uploaded_file.name
#             temp_path.parent.mkdir(exist_ok=True)
            
#             with open(temp_path, "wb") as f:
#                 f.write(uploaded_file.getbuffer())
            
#             try:
#                 with st.spinner("Processing file... This may take a few moments."):
#                     result = st.session_state.workflow.process_file(
#                         file_path=str(temp_path),
#                         user_id="streamlit_user",
#                         output_formats=output_formats,
#                         template_override=template_override
#                     )
                
#                 # Store result for later access
#                 st.session_state.processing_results.append(result)
                
#                 # Display result
#                 display_processing_result(result)
                
#             except Exception as e:
#                 st.error(f"Processing failed: {e}")
            
#             finally:
#                 # Clean up temp file
#                 if temp_path.exists():
#                     temp_path.unlink()
        
#         # Display recent results
#         if st.session_state.processing_results:
#             st.subheader("Recent Processing Results")
            
#             for i, result in enumerate(reversed(st.session_state.processing_results[-3:])):
#                 with st.expander(f"Session {result.session_id[:8]}... ({'✅ Success' if result.success else '❌ Failed'})"):
#                     display_processing_result(result)
    
#     # Tab 2: Sample Data
#     with tab2:
#         st.header("Sample Data Generation")
#         st.write("Generate sample financial datasets for testing and demonstration")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             if st.button("🎲 Generate New Sample Data", type="primary"):
#                 with st.spinner("Creating sample datasets..."):
#                     datasets = st.session_state.data_generator.create_sample_datasets()
                
#                 st.success(f"Created {len(datasets)} sample datasets!")
                
#                 for name, path in datasets.items():
#                     st.write(f"✅ {name}")
        
#         with col2:
#             if st.button("📁 Show Existing Sample Files"):
#                 sample_files = st.session_state.data_generator.get_sample_files_list()
                
#                 if sample_files:
#                     st.write(f"Found {len(sample_files)} sample files:")
                    
#                     for file_info in sample_files:
#                         col_a, col_b, col_c = st.columns([3, 1, 1])
                        
#                         with col_a:
#                             st.write(f"📄 {file_info['filename']}")
                        
#                         with col_b:
#                             st.write(f"{file_info['size']:,} bytes")
                        
#                         with col_c:
#                             # Quick process button for sample files
#                             if st.button("⚡ Process", key=f"process_{file_info['filename']}"):
#                                 with st.spinner(f"Processing {file_info['filename']}..."):
#                                     result = st.session_state.workflow.process_file(
#                                         file_path=file_info['path'],
#                                         user_id="streamlit_sample_user",
#                                         output_formats=['md', 'html', 'xlsx']
#                                     )
                                
#                                 st.session_state.processing_results.append(result)
#                                 display_processing_result(result)
#                 else:
#                     st.info("No sample files found. Generate some using the button above.")
        
#         # Custom dataset generator
#         st.subheader("Create Custom Dataset")
        
#         with st.expander("Custom Account Generator"):
#             st.write("Define custom accounts for testing")
            
#             # Initialize custom accounts in session state
#             if 'custom_accounts' not in st.session_state:
#                 st.session_state.custom_accounts = []
            
#             # Add account form
#             with st.form("add_account"):
#                 col1, col2, col3, col4 = st.columns(4)
                
#                 with col1:
#                     account_name = st.text_input("Account Name")
                
#                 with col2:
#                     account_type = st.selectbox("Type", ['Asset', 'Liability', 'Equity', 'Revenue', 'Expense'])
                
#                 with col3:
#                     amount = st.number_input("Amount", min_value=0.0, step=0.01)
                
#                 with col4:
#                     is_credit = st.checkbox("Credit Balance")
                
#                 if st.form_submit_button("Add Account"):
#                     if account_name and amount > 0:
#                         st.session_state.custom_accounts.append({
#                             'name': account_name,
#                             'type': account_type,
#                             'amount': amount,
#                             'is_credit': is_credit
#                         })
#                         st.success(f"Added {account_name}")
            
#             # Display current accounts
#             if st.session_state.custom_accounts:
#                 st.write("Custom Accounts:")
#                 df_custom = pd.DataFrame(st.session_state.custom_accounts)
#                 st.dataframe(df_custom)
                
#                 col1, col2, col3 = st.columns(3)
                
#                 with col1:
#                     if st.button("💾 Save as Excel"):
#                         custom_df = st.session_state.data_generator.generate_custom_dataset(
#                             st.session_state.custom_accounts,
#                             "custom_dataset.xlsx"
#                         )
#                         st.success("Custom dataset saved!")
                
#                 with col2:
#                     if st.button("🚀 Process Custom Data"):
#                         # Generate dataset and process it
#                         custom_df = st.session_state.data_generator.generate_custom_dataset(
#                             st.session_state.custom_accounts
#                         )
                        
#                         # Save temporarily and process
#                         temp_path = Path("temp") / "custom_data.xlsx"
#                         temp_path.parent.mkdir(exist_ok=True)
#                         custom_df.to_excel(temp_path, index=False)
                        
#                         result = st.session_state.workflow.process_file(
#                             str(temp_path),
#                             "custom_user",
#                             ['md', 'html', 'xlsx']
#                         )
                        
#                         st.session_state.processing_results.append(result)
#                         display_processing_result(result)
                        
#                         # Clean up
#                         temp_path.unlink()
                
#                 with col3:
#                     if st.button("🗑️ Clear All"):
#                         st.session_state.custom_accounts = []
#                         st.experimental_rerun()
    
#     # Tab 3: Templates
#     with tab3:
#         st.header("Financial Statement Templates")
        
#         templates = st.session_state.workflow.list_templates()
        
#         if templates:
#             selected_template = st.selectbox("Select template to view", templates)
            
#             if selected_template:
#                 template_info = st.session_state.workflow.validate_template(selected_template)
                
#                 if template_info.get('exists'):
#                     col1, col2 = st.columns(2)
                    
#                     with col1:
#                         st.write(f"**Template:** {template_info['name']}")
#                         st.write(f"**Size:** {template_info['size']} characters")
#                         st.write(f"**Lines:** {template_info['lines']}")
                    
#                     with col2:
#                         st.write("**Variables used:**")
#                         for var in template_info.get('variables', []):
#                             st.write(f"• `{var}`")
                    
#                     # Show template content
#                     with st.expander("View Template Content"):
#                         try:
#                             with open(template_info['path'], 'r') as f:
#                                 content = f.read()
#                             st.code(content, language='markdown')
#                         except Exception as e:
#                             st.error(f"Could not load template: {e}")
#                 else:
#                     st.error("Template not found")
#         else:
#             st.warning("No templates available")
    
#     # Tab 4: Analytics
#     with tab4:
#         st.header("System Analytics")
        
#         # Get system statistics
#         try:
#             system_status = st.session_state.workflow.get_system_status()
            
#             # Recent activity metrics
#             if system_status.get('recent_activity'):
#                 activity = system_status['recent_activity']
                
#                 col1, col2, col3 = st.columns(3)
                
#                 with col1:
#                     st.metric("Sessions Today", activity.get('sessions_today', 0))
                
#                 with col2:
#                     st.metric("Successful", activity.get('successful_sessions', 0))
                
#                 with col3:
#                     st.metric("Failed", activity.get('failed_sessions', 0))
            
#             # Output statistics visualization
#             if system_status.get('output_stats') and system_status['output_stats'].get('file_types'):
#                 st.subheader("Output File Types")
                
#                 file_types = system_status['output_stats']['file_types']
                
#                 # Create pie chart
#                 fig = px.pie(
#                     values=list(file_types.values()),
#                     names=list(file_types.keys()),
#                     title="Distribution of Output File Types"
#                 )
#                 st.plotly_chart(fig, use_container_width=True)
            
#             # Processing results analytics
#             if st.session_state.processing_results:
#                 st.subheader("Processing Performance")
                
#                 # Extract processing times
#                 processing_times = [r.processing_time for r in st.session_state.processing_results if r.success]
                
#                 if processing_times:
#                     # Create histogram of processing times
#                     fig = px.histogram(
#                         x=processing_times,
#                         nbins=10,
#                         title="Distribution of Processing Times",
#                         labels={'x': 'Processing Time (seconds)', 'y': 'Frequency'}
#                     )
#                     st.plotly_chart(fig, use_container_width=True)
                
#                 # Success rate
#                 success_rate = sum(1 for r in st.session_state.processing_results if r.success) / len(st.session_state.processing_results) * 100
#                 st.metric("Success Rate", f"{success_rate:.1f}%")
        
#         except Exception as e:
#             st.error(f"Analytics data unavailable: {e}")
    
#     # Tab 5: System Status
#     with tab5:
#         st.header("System Status & Health")
        
#         # Refresh button
#         if st.button("🔄 Refresh Status"):
#             st.experimental_rerun()
        
#         try:
#             status = st.session_state.workflow.get_system_status()
            
#             # System health indicator
#             health_color = "🟢" if status['system_healthy'] else "🔴"
#             st.markdown(f"## {health_color} System Status: {'Healthy' if status['system_healthy'] else 'Unhealthy'}")
            
#             # Agent status
#             st.subheader("Agent Status")
#             agent_cols = st.columns(len(status['agents_status']))
            
#             for i, (agent, agent_status) in enumerate(status['agents_status'].items()):
#                 with agent_cols[i]:
#                     status_icon = "✅" if agent_status == 'active' else "❌"
#                     st.write(f"{status_icon} {agent.capitalize()}")
            
#             # System errors
#             if status.get('errors'):
#                 st.subheader("⚠️ System Errors")
#                 for error in status['errors']:
#                     st.error(error)
            
#             # File system status
#             st.subheader("File System")
            
#             dirs_to_check = {
#                 'Output': OUTPUT_DIR,
#                 'Sample Data': SAMPLE_DATA_DIR,
#                 'Audit': AUDIT_DIR,
#                 'Templates': TEMPLATES_DIR
#             }
            
#             for name, directory in dirs_to_check.items():
#                 if directory.exists():
#                     file_count = len(list(directory.glob('*')))
#                     st.write(f"✅ {name}: {file_count} files")
#                 else:
#                     st.write(f"❌ {name}: Directory not found")
            
#             # Cleanup options
#             st.subheader("Maintenance")
            
#             col1, col2 = st.columns(2)
            
#             with col1:
#                 if st.button("🧹 Cleanup Old Files"):
#                     cleanup_result = st.session_state.workflow.cleanup_old_data(days_old=7)
                    
#                     st.success(f"Cleanup completed!")
#                     st.write(f"Files deleted: {cleanup_result['total_files_deleted']}")
#                     st.write(f"Space freed: {cleanup_result['total_space_freed']:,} bytes")
            
#             with col2:
#                 if st.button("📊 Export System Report"):
#                     # Generate system report
#                     report_data = {
#                         'timestamp': datetime.now().isoformat(),
#                         'system_status': status,
#                         'recent_sessions': len(st.session_state.processing_results),
#                         'supported_formats': st.session_state.workflow.get_supported_formats()
#                     }
                    
#                     report_json = json.dumps(report_data, indent=2, default=str)
                    
#                     st.download_button(
#                         label="📄 Download System Report (JSON)",
#                         data=report_json,
#                         file_name=f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
#                         mime="application/json"
#                     )
        
#         except Exception as e:
#             st.error(f"Could not retrieve system status: {e}")
    
#     # Footer
#     st.markdown("---")
#     st.markdown(
#         "**Financial Statement Automation System** | "
#         f"Built with Streamlit | "
#         f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#     )

# if __name__ == "__main__":
#     main()