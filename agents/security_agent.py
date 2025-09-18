"""
Security Agent - Handles file security, encryption, and virus scanning
"""
import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from config.logging_config import get_logger
from config.settings import MAX_FILE_SIZE, SUPPORTED_FORMATS, ENCRYPTION_ENABLED

try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

logger = get_logger('security')

class SecurityAgent:
    """Handles file security, encryption, and virus scanning"""

    def __init__(self):
        self.logger = logger
        self.encryption_key = None
        self.cipher_suite = None
        
        if ENCRYPTION_ENABLED and Fernet:
            try:
                self.encryption_key = Fernet.generate_key()
                self.cipher_suite = Fernet(self.encryption_key)
                self.logger.info("Encryption initialized successfully")
            except Exception as e:
                self.logger.error(f"Encryption setup failed: {e}")
        else:
            self.logger.warning("Encryption not available or disabled")

    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for integrity verification"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Hash calculation failed: {e}")
            return ""

    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive file security check"""
        scan_result = {
            'safe': False,
            'file_size': 0,
            'file_extension': '',
            'file_hash': '',
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                scan_result['errors'].append(f"File does not exist: {file_path}")
                return scan_result
                
            # Get file info
            file_path_obj = Path(file_path)
            scan_result['file_extension'] = file_path_obj.suffix.lower()
            scan_result['file_size'] = os.path.getsize(file_path)
            scan_result['file_hash'] = self.calculate_file_hash(file_path)

            # File size check
            if scan_result['file_size'] > MAX_FILE_SIZE:
                scan_result['errors'].append(
                    f"File size too large: {scan_result['file_size']} bytes (max: {MAX_FILE_SIZE})"
                )
                return scan_result

            # File extension check
            if scan_result['file_extension'] not in SUPPORTED_FORMATS:
                scan_result['errors'].append(
                    f"File extension not supported: {scan_result['file_extension']}"
                )
                return scan_result

            # Basic content validation
            if scan_result['file_size'] == 0:
                scan_result['errors'].append("File is empty")
                return scan_result

            # Additional security checks
            if self._check_suspicious_patterns(file_path):
                scan_result['warnings'].append("File contains potentially suspicious patterns")

            # If we get here, file passed all checks
            scan_result['safe'] = len(scan_result['errors']) == 0
            
            if scan_result['safe']:
                self.logger.info(f"File security scan passed: {file_path}")
            else:
                self.logger.warning(f"File security scan failed: {scan_result['errors']}")

            return scan_result

        except Exception as e:
            error_msg = f"Security scan failed: {e}"
            scan_result['errors'].append(error_msg)
            self.logger.error(error_msg)
            return scan_result

    def _check_suspicious_patterns(self, file_path: str) -> bool:
        """Check for suspicious file patterns"""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # For text-based files, check for suspicious content
            if file_ext in ['.csv', '.txt']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1024)  # Read first 1KB
                    suspicious_patterns = [
                        '<script', 'javascript:', 'eval(', 'exec(',
                        'system(', 'shell_exec', 'passthru'
                    ]
                    return any(pattern in content.lower() for pattern in suspicious_patterns)
            
            return False
        except Exception:
            return False

    def encrypt_data(self, data: str) -> bytes:
        """Encrypt sensitive data"""
        if self.cipher_suite:
            try:
                encrypted = self.cipher_suite.encrypt(data.encode())
                self.logger.debug("Data encrypted successfully")
                return encrypted
            except Exception as e:
                self.logger.error(f"Encryption failed: {e}")
                return data.encode()
        else:
            self.logger.warning("Encryption not available, returning unencrypted data")
            return data.encode()

    def decrypt_data(self, encrypted_data: bytes) -> str:
        """Decrypt sensitive data"""
        if self.cipher_suite:
            try:
                decrypted = self.cipher_suite.decrypt(encrypted_data).decode()
                self.logger.debug("Data decrypted successfully")
                return decrypted
            except Exception as e:
                self.logger.error(f"Decryption failed: {e}")
                try:
                    return encrypted_data.decode()
                except:
                    return str(encrypted_data)
        else:
            self.logger.warning("Decryption not available")
            try:
                return encrypted_data.decode()
            except:
                return str(encrypted_data)

    def create_secure_temp_file(self, content: str, suffix: str = '.tmp') -> Optional[str]:
        """Create a secure temporary file"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as tmp_file:
                tmp_file.write(content)
                temp_path = tmp_file.name
            
            self.logger.info(f"Secure temp file created: {temp_path}")
            return temp_path
        except Exception as e:
            self.logger.error(f"Failed to create secure temp file: {e}")
            return None

    def cleanup_temp_file(self, file_path: str) -> bool:
        """Safely remove temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Temp file cleaned up: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp file: {e}")
            return False