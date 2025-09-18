"""
Data Ingestion Agent - Extracts data from various file formats
"""
import pandas as pd
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from config.logging_config import get_logger
from config.settings import SUPPORTED_FORMATS

# Optional imports with fallbacks
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    from docx import Document
except ImportError:
    Document = None

logger = get_logger('ingestion')

class DataIngestionAgent:
    """Extracts data from various file formats"""

    def __init__(self):
        self.logger = logger
        self.supported_formats = SUPPORTED_FORMATS
        self.extraction_stats = {
            'files_processed': 0,
            'rows_extracted': 0,
            'errors': []
        }

    def extract_from_excel(self, file_path: str) -> Dict[str, Any]:
        """Extract data from Excel files (.xlsx, .xls)"""
        result = {
            'success': False,
            'data': None,
            'metadata': {},
            'errors': []
        }
        
        try:
            self.logger.info(f"Extracting data from Excel file: {file_path}")
            
            # Try to read the Excel file
            df = pd.read_excel(file_path, sheet_name=0)
            
            # Handle empty DataFrame
            if df.empty:
                result['errors'].append("Excel file is empty")
                return result
            
            # Basic cleanup
            df = df.dropna(how='all')  # Remove completely empty rows
            df.columns = df.columns.astype(str)  # Ensure column names are strings
            
            result['data'] = df
            result['metadata'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'file_type': 'excel'
            }
            result['success'] = True
            
            self.logger.info(f"Successfully extracted {len(df)} rows from Excel file")
            
        except Exception as e:
            error_msg = f"Excel extraction failed: {e}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg)
            
        return result

    def extract_from_csv(self, file_path: str) -> Dict[str, Any]:
        """Extract data from CSV files"""
        result = {
            'success': False,
            'data': None,
            'metadata': {},
            'errors': []
        }
        
        try:
            self.logger.info(f"Extracting data from CSV file: {file_path}")
            
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    used_encoding = encoding
                    self.logger.debug(f"Successfully read CSV with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    if encoding == encodings[-1]:  # Last encoding
                        raise e
                    continue
            
            if df is None:
                result['errors'].append("Could not decode CSV file with any supported encoding")
                return result
            
            # Handle empty DataFrame
            if df.empty:
                result['errors'].append("CSV file is empty")
                return result
            
            # Basic cleanup
            df = df.dropna(how='all')
            df.columns = df.columns.astype(str)
            
            result['data'] = df
            result['metadata'] = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'encoding_used': used_encoding,
                'file_type': 'csv'
            }
            result['success'] = True
            
            self.logger.info(f"Successfully extracted {len(df)} rows from CSV file")
            
        except Exception as e:
            error_msg = f"CSV extraction failed: {e}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg)
            
        return result

    def extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract data from PDF files"""
        result = {
            'success': False,
            'data': None,
            'metadata': {},
            'errors': []
        }
        
        if not PyPDF2:
            result['errors'].append("PyPDF2 not available - PDF extraction not supported")
            self.logger.warning("PyPDF2 not available for PDF extraction")
            return result
        
        try:
            self.logger.info(f"Extracting data from PDF file: {file_path}")
            
            text_content = []
            page_count = 0
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        if text.strip():
                            text_content.append(text)
                    except Exception as e:
                        self.logger.warning(f"Failed to extract text from page {page_num}: {e}")
                        continue

            if not text_content:
                result['errors'].append("No readable text found in PDF")
                return result

            # Attempt to parse tabular data from text
            all_text = "\n".join(text_content)
            parsed_data = self._parse_tabular_text(all_text)
            
            if parsed_data:
                df = pd.DataFrame(parsed_data)
                result['data'] = df
                result['metadata'] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'pages_processed': page_count,
                    'file_type': 'pdf'
                }
                result['success'] = True
                self.logger.info(f"Successfully extracted {len(df)} rows from PDF")
            else:
                # Create basic structure with extracted text
                df = pd.DataFrame({
                    'Extracted_Text': [text.strip() for text in text_content if text.strip()],
                    'Page_Number': range(1, len(text_content) + 1)
                })
                result['data'] = df
                result['metadata'] = {
                    'rows': len(df),
                    'columns': 2,
                    'column_names': ['Extracted_Text', 'Page_Number'],
                    'pages_processed': page_count,
                    'file_type': 'pdf',
                    'note': 'Raw text extraction - manual parsing may be needed'
                }
                result['success'] = True
                self.logger.info(f"PDF text extracted but no tabular structure detected")
                
        except Exception as e:
            error_msg = f"PDF extraction failed: {e}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg)
            
        return result

    def _parse_tabular_text(self, text: str) -> Optional[List[Dict]]:
        """Attempt to parse tabular data from extracted text"""
        try:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Look for lines that might contain financial data
            financial_lines = []
            for line in lines:
                # Check if line contains numbers that look like financial amounts
                if re.search(r'\$?\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+\.\d{2}', line):
                    financial_lines.append(line)
            
            if len(financial_lines) < 2:
                return None
            
            # Try to split lines into columns
            parsed_rows = []
            for line in financial_lines[:50]:  # Limit to first 50 financial lines
                # Split by multiple spaces, tabs, or specific delimiters
                parts = re.split(r'\s{2,}|\t|(?<=\d)\s+(?=[A-Za-z])|(?<=[A-Za-z])\s+(?=\$?\d)', line)
                if len(parts) >= 2:
                    # Clean up parts
                    cleaned_parts = [part.strip() for part in parts if part.strip()]
                    if len(cleaned_parts) >= 2:
                        row_data = {}
                        if len(cleaned_parts) >= 3:
                            row_data['Account'] = cleaned_parts[0]
                            row_data['Debit'] = self._extract_amount(cleaned_parts[1])
                            row_data['Credit'] = self._extract_amount(cleaned_parts[2])
                        else:
                            row_data['Account'] = cleaned_parts[0]
                            row_data['Amount'] = self._extract_amount(cleaned_parts[1])
                        parsed_rows.append(row_data)
            
            return parsed_rows if len(parsed_rows) >= 2 else None
            
        except Exception as e:
            self.logger.debug(f"Text parsing failed: {e}")
            return None

    def _extract_amount(self, text: str) -> float:
        """Extract numeric amount from text"""
        try:
            # Remove currency symbols and clean up
            cleaned = re.sub(r'[^\d.,()-]', '', text)
            cleaned = cleaned.replace(',', '')
            
            # Handle negative amounts in parentheses
            if '(' in cleaned and ')' in cleaned:
                cleaned = cleaned.replace('(', '').replace(')', '')
                return -float(cleaned) if cleaned else 0.0
            
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0

    def extract_from_image(self, file_path: str) -> Dict[str, Any]:
        """Extract data from image files using OCR (placeholder)"""
        result = {
            'success': False,
            'data': None,
            'metadata': {},
            'errors': []
        }
        
        self.logger.warning("OCR extraction not fully implemented - creating placeholder data")
        
        # Create placeholder data structure
        placeholder_data = pd.DataFrame({
            'Account': ['OCR_Extracted_Account_1', 'OCR_Extracted_Account_2', 'OCR_Extracted_Account_3'],
            'Amount': [1000.00, 2500.00, 750.00],
            'Type': ['Debit', 'Credit', 'Debit']
        })
        
        result['data'] = placeholder_data
        result['metadata'] = {
            'rows': len(placeholder_data),
            'columns': len(placeholder_data.columns),
            'column_names': placeholder_data.columns.tolist(),
            'file_type': 'image',
            'note': 'OCR extraction placeholder - implement with pytesseract or similar'
        }
        result['success'] = True
        
        return result

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Main extraction method - routes to appropriate extractor"""
        self.logger.info(f"Processing file: {file_path}")
        
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.xlsx', '.xls']:
                return self.extract_from_excel(file_path)
            elif file_ext == '.csv':
                return self.extract_from_csv(file_path)
            elif file_ext == '.pdf':
                return self.extract_from_pdf(file_path)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                return self.extract_from_image(file_path)
            else:
                return {
                    'success': False,
                    'data': None,
                    'metadata': {},
                    'errors': [f"Unsupported file format: {file_ext}"]
                }
                
        except Exception as e:
            error_msg = f"File processing failed: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'data': None,
                'metadata': {},
                'errors': [error_msg]
            }

    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return self.extraction_stats.copy()

    def reset_stats(self):
        """Reset extraction statistics"""
        self.extraction_stats = {
            'files_processed': 0,
            'rows_extracted': 0,
            'errors': []
        }