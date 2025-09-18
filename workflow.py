"""
Fixed Main Workflow System - Orchestrates the complete financial statement automation process
"""
import os
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import agents - with proper error handling
try:
    from agents.security_agent import SecurityAgent
    from agents.data_ingestion_agent import DataIngestionAgent
    from agents.validation_agent import ValidationAgent
    from agents.template_intelligence_agent import TemplateIntelligenceAgent
    from agents.output_generation_agent import OutputGenerationAgent
    from agents.audit_trail_agent import AuditTrailAgent
except ImportError as e:
    print(f"Warning: Could not import agents: {e}")
    print("Make sure all agent files are properly created")

# Import configuration - with fallbacks
try:
    from config.settings import validate_config
    from config.logging_config import setup_logging, get_logger
    
    # Set up logging
    setup_logging()
    logger = get_logger('workflow')
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('workflow')
    print(f"Warning: Using basic logging due to import error: {e}")
    
    # Dummy validate_config function
    def validate_config():
        return True

@dataclass
class ProcessingResult:
    success: bool
    session_id: str
    output_files: List[str]
    errors: List[str]
    warnings: List[str]
    processing_time: float
    summary: Dict[str, Any]

class FinancialWorkflow:
    """Main workflow orchestrator for financial statement automation"""

    def __init__(self):
        try:
            # Validate configuration
            validate_config()
            self.logger = logger
            self.logger.info("Financial Workflow System initializing...")
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            # Continue with basic setup
            self.logger = logger

        # Initialize agents with error handling
        try:
            self.security_agent = SecurityAgent()
            self.logger.info("Security agent initialized")
        except Exception as e:
            self.logger.error(f"Security agent failed to initialize: {e}")
            self.security_agent = None

        try:
            self.ingestion_agent = DataIngestionAgent()
            self.logger.info("Ingestion agent initialized")
        except Exception as e:
            self.logger.error(f"Ingestion agent failed to initialize: {e}")
            self.ingestion_agent = None

        try:
            self.validation_agent = ValidationAgent()
            self.logger.info("Validation agent initialized")
        except Exception as e:
            self.logger.error(f"Validation agent failed to initialize: {e}")
            self.validation_agent = None

        try:
            self.template_agent = TemplateIntelligenceAgent()
            self.logger.info("Template agent initialized")
        except Exception as e:
            self.logger.error(f"Template agent failed to initialize: {e}")
            self.template_agent = None

        try:
            self.output_agent = OutputGenerationAgent()
            self.logger.info("Output agent initialized")
        except Exception as e:
            self.logger.error(f"Output agent failed to initialize: {e}")
            self.output_agent = None

        try:
            self.audit_agent = AuditTrailAgent()
            self.logger.info("Audit agent initialized")
        except Exception as e:
            self.logger.error(f"Audit agent failed to initialize: {e}")
            self.audit_agent = None
        
        self.logger.info("Workflow system initialization completed")

    def process_file(self, 
                    file_path: str, 
                    user_id: str = "system", 
                    output_formats: List[str] = None,
                    template_override: Optional[str] = None) -> ProcessingResult:
        """
        Process a financial file through the complete automation workflow
        """
        start_time = time.time()
        
        if output_formats is None:
            output_formats = ['md', 'html']
        
        # Initialize result
        result = ProcessingResult(
            success=False,
            session_id="",
            output_files=[],
            errors=[],
            warnings=[],
            processing_time=0.0,
            summary={}
        )
        
        session_id = None
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                result.errors.append(f"File not found: {file_path}")
                return result

            # Step 1: Start audit session
            file_hash = self._calculate_file_hash(file_path)
            if self.audit_agent:
                session_id = self.audit_agent.start_session(user_id, file_path, file_hash)
                result.session_id = session_id
            else:
                session_id = f"session_{int(time.time())}"
                result.session_id = session_id
            
            self.logger.info(f"Starting workflow for file: {file_path} (Session: {session_id})")
            
            # Step 2: Security scanning
            if self.audit_agent:
                self.audit_agent.start_step(session_id, "security_scan", {"file_path": file_path})
            
            if self.security_agent:
                security_result = self.security_agent.scan_file(file_path)
                
                if not security_result['safe']:
                    errors = security_result.get('errors', [])
                    result.errors.extend(errors)
                    if self.audit_agent:
                        self.audit_agent.end_step(session_id, "security_scan", "failed", errors=errors)
                        self.audit_agent.end_session(session_id, "failed")
                    return result
                
                if security_result.get('warnings'):
                    result.warnings.extend(security_result['warnings'])
            else:
                self.logger.warning("Security agent not available - skipping security scan")
                security_result = {'safe': True}
            
            if self.audit_agent:
                self.audit_agent.end_step(session_id, "security_scan", "completed", 
                                         details=security_result)
            
            # Step 3: Data ingestion
            if self.audit_agent:
                self.audit_agent.start_step(session_id, "data_ingestion")
            
            if not self.ingestion_agent:
                result.errors.append("Data ingestion agent not available")
                return result
            
            extraction_result = self.ingestion_agent.process_file(file_path)
            
            if not extraction_result['success']:
                result.errors.extend(extraction_result.get('errors', []))
                if self.audit_agent:
                    self.audit_agent.end_step(session_id, "data_ingestion", "failed", 
                                             errors=extraction_result.get('errors', []))
                    self.audit_agent.end_session(session_id, "failed")
                return result
            
            if self.audit_agent:
                self.audit_agent.end_step(session_id, "data_ingestion", "completed",
                                         details=extraction_result.get('metadata', {}))
            
            # Step 4: Data validation and normalization
            if self.audit_agent:
                self.audit_agent.start_step(session_id, "validation")
            
            if not self.validation_agent:
                result.errors.append("Validation agent not available")
                return result
            
            validation_result = self.validation_agent.process_data(extraction_result)
            
            if not validation_result['success']:
                result.errors.extend(validation_result.get('errors', []))
                if self.audit_agent:
                    self.audit_agent.end_step(session_id, "validation", "failed",
                                             errors=validation_result.get('errors', []))
                    self.audit_agent.end_session(session_id, "failed")
                return result
            
            # Add validation warnings to result
            if validation_result.get('validation_result'):
                result.warnings.extend(validation_result['validation_result'].warnings)
                
                # Add validation results to audit
                if self.audit_agent:
                    validation_summary = {
                        'is_valid': validation_result['validation_result'].is_valid,
                        'total_records': validation_result['validation_result'].records_processed,
                        'total_debits': validation_result['validation_result'].total_debits,
                        'total_credits': validation_result['validation_result'].total_credits,
                        'balance_difference': validation_result['validation_result'].balance_difference
                    }
                    self.audit_agent.add_validation_results(session_id, validation_summary)
            
            if self.audit_agent:
                self.audit_agent.end_step(session_id, "validation", "completed")
            
            # Step 5: Template mapping and statement generation
            if self.audit_agent:
                self.audit_agent.start_step(session_id, "template_processing")
            
            if not self.template_agent:
                result.errors.append("Template agent not available")
                return result
            
            records = validation_result['normalized_records']
            
            # Use template override or auto-detect
            template_type = template_override or self.template_agent.detect_statement_type(records)
            if self.audit_agent:
                self.audit_agent.set_template_used(session_id, template_type)
            
            statement_result = self.template_agent.generate_statement(records, template_type)
            
            if not statement_result['success']:
                result.errors.extend(statement_result.get('errors', []))
                if self.audit_agent:
                    self.audit_agent.end_step(session_id, "template_processing", "failed",
                                             errors=statement_result.get('errors', []))
                    self.audit_agent.end_session(session_id, "failed")
                return result
            
            if self.audit_agent:
                self.audit_agent.end_step(session_id, "template_processing", "completed",
                                         details={'template_used': template_type})
            
            # Step 6: Output generation
            if self.audit_agent:
                self.audit_agent.start_step(session_id, "output_generation")
            
            if not self.output_agent:
                result.errors.append("Output agent not available")
                return result
            
            # Generate base filename
            base_filename = f"{Path(file_path).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output package
            output_result = self.output_agent.create_output_package(
                base_filename,
                output_formats,
                statement_result['content'],
                statement_result['template_data']
            )
            
            if not output_result['success']:
                result.errors.extend(output_result.get('errors', []))
                if self.audit_agent:
                    self.audit_agent.end_step(session_id, "output_generation", "failed",
                                             errors=output_result.get('errors', []))
                    self.audit_agent.end_session(session_id, "failed")
                return result
            
            # Add output files to audit and result
            result.output_files = output_result['files_created']
            if self.audit_agent:
                for file_path_out in result.output_files:
                    self.audit_agent.add_output_file(session_id, file_path_out)
            
            # Add package path if created
            if output_result.get('package_path'):
                result.output_files.append(output_result['package_path'])
                if self.audit_agent:
                    self.audit_agent.add_output_file(session_id, output_result['package_path'])
            
            if self.audit_agent:
                self.audit_agent.end_step(session_id, "output_generation", "completed",
                                         details={'formats_generated': output_formats,
                                                 'files_created': len(result.output_files)})
            
            # Finalize workflow
            result.success = True
            result.processing_time = time.time() - start_time
            
            # Create summary
            validation_res = validation_result.get('validation_result')
            result.summary = {
                'file_processed': file_path,
                'template_used': template_type,
                'records_processed': len(records) if records else 0,
                'output_formats': output_formats,
                'processing_time_seconds': result.processing_time,
                'validation_status': 'passed' if (validation_res and validation_res.is_valid) else 'warnings',
                'total_debits': validation_res.total_debits if validation_res else 0,
                'total_credits': validation_res.total_credits if validation_res else 0
            }
            
            # End audit session
            if self.audit_agent:
                self.audit_agent.end_session(session_id, "completed")
            
            self.logger.info(f"Workflow completed successfully for session {session_id}")
            
        except Exception as e:
            error_msg = f"Workflow failed: {e}"
            result.errors.append(error_msg)
            self.logger.error(error_msg)
            
            if session_id and self.audit_agent:
                self.audit_agent.add_error(session_id, error_msg)
                self.audit_agent.end_session(session_id, "error")
        
        return result

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate file hash for audit trail"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def batch_process(self, file_paths: List[str], user_id: str = "system") -> List[ProcessingResult]:
        """Process multiple files in batch"""
        results = []
        
        self.logger.info(f"Starting batch processing of {len(file_paths)} files")
        
        for i, file_path in enumerate(file_paths):
            self.logger.info(f"Processing file {i+1}/{len(file_paths)}: {file_path}")
            
            result = self.process_file(file_path, user_id)
            results.append(result)
            
            if not result.success:
                self.logger.warning(f"File processing failed: {file_path}")
            
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Batch processing completed: {successful}/{len(file_paths)} successful")
        
        return results

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and health"""
        status = {
            'system_healthy': True,
            'agents_status': {},
            'recent_activity': {},
            'errors': []
        }
        
        try:
            # Check agent health
            agents = {
                'security': self.security_agent,
                'ingestion': self.ingestion_agent,
                'validation': self.validation_agent,
                'template': self.template_agent,
                'output': self.output_agent,
                'audit': self.audit_agent
            }
            
            for name, agent in agents.items():
                status['agents_status'][name] = 'active' if agent else 'inactive'
                if not agent:
                    status['system_healthy'] = False
            
            # Get recent activity from audit
            if self.audit_agent:
                try:
                    audit_stats = self.audit_agent.get_audit_statistics(days=1)
                    status['recent_activity'] = {
                        'sessions_today': audit_stats.get('total_sessions', 0),
                        'successful_sessions': audit_stats.get('successful_sessions', 0),
                        'failed_sessions': audit_stats.get('failed_sessions', 0)
                    }
                except Exception as e:
                    status['errors'].append(f"Could not get audit stats: {e}")
            
            # Get output statistics
            if self.output_agent:
                try:
                    output_stats = self.output_agent.get_output_stats()
                    status['output_stats'] = output_stats
                except Exception as e:
                    status['errors'].append(f"Could not get output stats: {e}")
            
        except Exception as e:
            status['system_healthy'] = False
            status['errors'].append(f"Health check failed: {e}")
            self.logger.error(f"System health check failed: {e}")
        
        return status

    def cleanup_old_data(self, days_old: int = 7) -> Dict[str, Any]:
        """Clean up old files and audit records"""
        cleanup_results = {
            'output_cleanup': {},
            'audit_cleanup': {},
            'total_files_deleted': 0,
            'total_space_freed': 0,
            'errors': []
        }
        
        try:
            # Cleanup old output files
            if self.output_agent:
                output_cleanup = self.output_agent.cleanup_old_files(days_old)
                cleanup_results['output_cleanup'] = output_cleanup
                cleanup_results['total_files_deleted'] += output_cleanup.get('files_deleted', 0)
                cleanup_results['total_space_freed'] += output_cleanup.get('space_freed', 0)
            
            # Cleanup old audit files (keep longer - 90 days default)
            if self.audit_agent:
                audit_cleanup = self.audit_agent.cleanup_old_audits(max(days_old * 10, 90))
                cleanup_results['audit_cleanup'] = audit_cleanup
                cleanup_results['total_files_deleted'] += audit_cleanup.get('files_deleted', 0)
                cleanup_results['total_space_freed'] += audit_cleanup.get('space_freed', 0)
            
            self.logger.info(f"Cleanup completed: {cleanup_results['total_files_deleted']} files deleted")
            
        except Exception as e:
            error_msg = f"Cleanup failed: {e}"
            cleanup_results['errors'].append(error_msg)
            self.logger.error(error_msg)
        
        return cleanup_results

    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Validate a specific template"""
        if self.template_agent:
            return self.template_agent.get_template_info(template_name)
        return {'exists': False, 'error': 'Template agent not available'}

    def list_templates(self) -> List[str]:
        """List all available templates"""
        if self.template_agent:
            return self.template_agent.list_available_templates()
        return []

    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported input and output formats"""
        input_formats = self.ingestion_agent.supported_formats if self.ingestion_agent else []
        output_formats = self.output_agent.supported_formats if self.output_agent else []
        
        return {
            'input_formats': input_formats,
            'output_formats': output_formats
        }