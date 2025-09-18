"""
Audit Trail Agent - Manages comprehensive audit logging and compliance tracking
"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from config.logging_config import get_logger
from config.settings import AUDIT_DIR

logger = get_logger('audit')

@dataclass
class ProcessingStep:
    step_name: str
    timestamp: str
    status: str
    duration_ms: Optional[float] = None
    details: Dict[str, Any] = None
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

@dataclass
class AuditRecord:
    session_id: str
    user_id: str
    file_processed: str
    processing_start: str
    processing_end: Optional[str] = None
    total_duration_ms: Optional[float] = None
    status: str = "in_progress"
    input_file_hash: str = ""
    output_files: List[str] = None
    processing_steps: List[ProcessingStep] = None
    validation_results: Dict[str, Any] = None
    template_used: str = ""
    errors: List[str] = None
    warnings: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.output_files is None:
            self.output_files = []
        if self.processing_steps is None:
            self.processing_steps = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.metadata is None:
            self.metadata = {}

class AuditTrailAgent:
    """Manages audit trail and compliance logging"""

    def __init__(self):
        self.logger = logger
        self.audit_folder = AUDIT_DIR
        self.audit_folder.mkdir(exist_ok=True)
        
        # Current session tracking
        self.current_sessions: Dict[str, AuditRecord] = {}
        
        # Performance tracking
        self.step_start_times: Dict[str, Dict[str, datetime]] = {}

    def start_session(self, user_id: str, file_path: str, file_hash: str = "") -> str:
        """Start a new audit session"""
        session_id = str(uuid.uuid4())
        
        audit_record = AuditRecord(
            session_id=session_id,
            user_id=user_id,
            file_processed=file_path,
            processing_start=datetime.now().isoformat(),
            input_file_hash=file_hash,
            metadata={
                'system_version': '1.0',
                'start_timestamp': datetime.now().timestamp()
            }
        )
        
        self.current_sessions[session_id] = audit_record
        self.step_start_times[session_id] = {}
        
        self.logger.info(f"Audit session started: {session_id} for user: {user_id}")
        return session_id

    def start_step(self, session_id: str, step_name: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """Start tracking a processing step"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        self.step_start_times[session_id][step_name] = datetime.now()
        
        step = ProcessingStep(
            step_name=step_name,
            timestamp=datetime.now().isoformat(),
            status="started",
            details=details or {}
        )
        
        self.current_sessions[session_id].processing_steps.append(step)
        self.logger.debug(f"Step started: {step_name} in session {session_id}")
        return True

    def end_step(self, session_id: str, step_name: str, status: str = "completed", 
                 details: Optional[Dict[str, Any]] = None, 
                 errors: Optional[List[str]] = None,
                 warnings: Optional[List[str]] = None) -> bool:
        """End tracking a processing step"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        # Calculate duration
        duration_ms = None
        if session_id in self.step_start_times and step_name in self.step_start_times[session_id]:
            start_time = self.step_start_times[session_id][step_name]
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            del self.step_start_times[session_id][step_name]
        
        # Find the step to update
        steps = self.current_sessions[session_id].processing_steps
        for step in reversed(steps):  # Look from the end for the most recent matching step
            if step.step_name == step_name and step.status == "started":
                step.status = status
                step.duration_ms = duration_ms
                if details:
                    step.details.update(details)
                if errors:
                    step.errors.extend(errors)
                if warnings:
                    step.warnings.extend(warnings)
                break
        else:
            # If no matching started step found, create a new completed step
            step = ProcessingStep(
                step_name=step_name,
                timestamp=datetime.now().isoformat(),
                status=status,
                duration_ms=duration_ms,
                details=details or {},
                errors=errors or [],
                warnings=warnings or []
            )
            steps.append(step)
        
        self.logger.debug(f"Step ended: {step_name} with status {status} in session {session_id}")
        return True

    def add_validation_results(self, session_id: str, validation_data: Dict[str, Any]) -> bool:
        """Add validation results to audit record"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        self.current_sessions[session_id].validation_results = validation_data
        self.logger.debug(f"Validation results added to session {session_id}")
        return True

    def add_output_file(self, session_id: str, file_path: str) -> bool:
        """Add output file to audit record"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        self.current_sessions[session_id].output_files.append(file_path)
        self.logger.debug(f"Output file added to session {session_id}: {file_path}")
        return True

    def set_template_used(self, session_id: str, template_name: str) -> bool:
        """Set the template used for this session"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        self.current_sessions[session_id].template_used = template_name
        return True

    def add_error(self, session_id: str, error_message: str) -> bool:
        """Add an error to the audit record"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        self.current_sessions[session_id].errors.append({
            'timestamp': datetime.now().isoformat(),
            'message': error_message
        })
        return True

    def add_warning(self, session_id: str, warning_message: str) -> bool:
        """Add a warning to the audit record"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        self.current_sessions[session_id].warnings.append({
            'timestamp': datetime.now().isoformat(),
            'message': warning_message
        })
        return True

    def end_session(self, session_id: str, final_status: str = "completed") -> bool:
        """End an audit session and save to file"""
        if session_id not in self.current_sessions:
            self.logger.error(f"Session not found: {session_id}")
            return False
        
        audit_record = self.current_sessions[session_id]
        
        # Finalize the record
        audit_record.processing_end = datetime.now().isoformat()
        audit_record.status = final_status
        
        # Calculate total duration
        start_timestamp = audit_record.metadata.get('start_timestamp')
        if start_timestamp:
            audit_record.total_duration_ms = (datetime.now().timestamp() - start_timestamp) * 1000
        
        # Save to file
        success = self._save_audit_record(audit_record)
        
        # Clean up
        if session_id in self.current_sessions:
            del self.current_sessions[session_id]
        if session_id in self.step_start_times:
            del self.step_start_times[session_id]
        
        self.logger.info(f"Audit session ended: {session_id} with status {final_status}")
        return success

    def _save_audit_record(self, audit_record: AuditRecord) -> bool:
        """Save audit record to file"""
        try:
            # Create filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audit_{audit_record.session_id}_{timestamp}.json"
            file_path = self.audit_folder / filename
            
            # Convert to dictionary for JSON serialization
            audit_data = asdict(audit_record)
            
            # Add system metadata
            audit_data['audit_metadata'] = {
                'audit_version': '1.0',
                'saved_at': datetime.now().isoformat(),
                'file_path': str(file_path)
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(audit_data, f, indent=2, default=str)
            
            self.logger.info(f"Audit record saved: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save audit record: {e}")
            return False

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of current or completed session"""
        if session_id in self.current_sessions:
            record = self.current_sessions[session_id]
        else:
            # Try to load from file
            record = self._load_audit_record(session_id)
            if not record:
                return None
        
        # Create summary
        summary = {
            'session_id': record.session_id,
            'status': record.status,
            'file_processed': record.file_processed,
            'processing_start': record.processing_start,
            'processing_end': record.processing_end,
            'total_steps': len(record.processing_steps),
            'errors_count': len(record.errors),
            'warnings_count': len(record.warnings),
            'output_files_count': len(record.output_files),
            'template_used': record.template_used
        }
        
        if record.total_duration_ms:
            summary['total_duration_seconds'] = record.total_duration_ms / 1000
        
        return summary

    def _load_audit_record(self, session_id: str) -> Optional[AuditRecord]:
        """Load audit record from file"""
        try:
            # Find the audit file for this session
            for file_path in self.audit_folder.glob(f"audit_{session_id}_*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Convert back to AuditRecord
                # Note: This is a simplified conversion - in a real system you'd want
                # proper deserialization handling
                return AuditRecord(**{k: v for k, v in data.items() 
                                    if k in AuditRecord.__annotations__})
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to load audit record for session {session_id}: {e}")
            return None

    def get_audit_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get audit statistics for the specified period"""
        stats = {
            'total_sessions': 0,
            'successful_sessions': 0,
            'failed_sessions': 0,
            'files_processed': 0,
            'average_processing_time': 0,
            'most_used_templates': {},
            'error_summary': {},
            'recent_sessions': []
        }
        
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            processing_times = []
            
            for file_path in self.audit_folder.glob("audit_*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Check if within time range
                    if data.get('metadata', {}).get('start_timestamp', 0) < cutoff_date:
                        continue
                    
                    stats['total_sessions'] += 1
                    
                    if data.get('status') == 'completed':
                        stats['successful_sessions'] += 1
                    else:
                        stats['failed_sessions'] += 1
                    
                    stats['files_processed'] += 1
                    
                    # Processing time
                    duration = data.get('total_duration_ms')
                    if duration:
                        processing_times.append(duration / 1000)
                    
                    # Template usage
                    template = data.get('template_used', 'unknown')
                    stats['most_used_templates'][template] = stats['most_used_templates'].get(template, 0) + 1
                    
                    # Recent sessions
                    if len(stats['recent_sessions']) < 10:
                        stats['recent_sessions'].append({
                            'session_id': data.get('session_id', ''),
                            'file': data.get('file_processed', ''),
                            'status': data.get('status', ''),
                            'timestamp': data.get('processing_start', '')
                        })
                
                except Exception as e:
                    self.logger.warning(f"Error processing audit file {file_path}: {e}")
                    continue
            
            # Calculate average processing time
            if processing_times:
                stats['average_processing_time'] = sum(processing_times) / len(processing_times)
            
        except Exception as e:
            self.logger.error(f"Failed to generate audit statistics: {e}")
        
        return stats

    def cleanup_old_audits(self, days_old: int = 90) -> Dict[str, Any]:
        """Clean up old audit files"""
        result = {
            'files_deleted': 0,
            'space_freed': 0,
            'errors': []
        }
        
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            for file_path in self.audit_folder.glob("audit_*.json"):
                try:
                    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_modified < cutoff_date:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        result['files_deleted'] += 1
                        result['space_freed'] += file_size
                except Exception as e:
                    result['errors'].append(f"Error deleting {file_path}: {e}")
            
            self.logger.info(f"Audit cleanup completed: {result['files_deleted']} files deleted")
            
        except Exception as e:
            error_msg = f"Audit cleanup failed: {e}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg)
        
        return result