"""
Fixed Validation Agent - Validates financial data integrity and normalizes data
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from config.logging_config import get_logger
from config.settings import VALIDATION_TOLERANCE, ACCOUNT_CATEGORIES

logger = get_logger('validation')

@dataclass
class FinancialRecord:
    account_name: str
    debit: float = 0.0
    credit: float = 0.0
    balance: float = 0.0
    account_type: str = ""
    category: str = ""
    description: str = ""
    original_amount: Optional[float] = None

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    total_debits: float
    total_credits: float
    balance_difference: float
    records_processed: int
    empty_accounts: int
    zero_amounts: int

class ValidationAgent:
    """Validates financial data integrity and normalizes data"""

    def __init__(self):
        self.logger = logger
        self.account_mappings = ACCOUNT_CATEGORIES
        self.validation_rules = {
            'min_account_name_length': 2,
            'max_amount': 999999999.99,
            'tolerance': VALIDATION_TOLERANCE
        }

    def normalize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names to standard format"""
        self.logger.debug("Normalizing column names")
        
        column_mapping = {}
        
        for col in df.columns:
            col_lower = str(col).lower().strip()
            col_clean = re.sub(r'[^\w\s]', '', col_lower)
            
            # Map to standard names - avoid duplicate mappings
            if 'account' in col_clean and 'account_name' not in column_mapping.values():
                column_mapping[col] = 'account_name'
            elif 'name' in col_clean and 'account_name' not in column_mapping.values() and 'account' not in col_clean:
                column_mapping[col] = 'account_name'
            elif 'debit' in col_clean:
                column_mapping[col] = 'debit'
            elif 'credit' in col_clean:
                column_mapping[col] = 'credit'
            elif 'balance' in col_clean:
                column_mapping[col] = 'balance'
            elif any(keyword in col_clean for keyword in ['amount', 'value', 'total']) and 'amount' not in column_mapping.values():
                column_mapping[col] = 'amount'
            elif 'type' in col_clean:
                column_mapping[col] = 'type'
            elif 'description' in col_clean:
                column_mapping[col] = 'description'
        
        # Apply mapping
        normalized_df = df.rename(columns=column_mapping)
        
        self.logger.info(f"Column mapping applied: {column_mapping}")
        return normalized_df

    def clean_amount_value(self, value: Any) -> float:
        """Clean and convert amount values to float"""
        if pd.isna(value) or value == '' or value is None:
            return 0.0
        
        try:
            # Convert to string first
            str_value = str(value).strip()
            
            # Handle empty strings
            if not str_value or str_value.lower() in ['nan', 'null', 'none']:
                return 0.0
            
            # Remove currency symbols and formatting
            cleaned = re.sub(r'[^\d.,()-]', '', str_value)
            
            # Handle negative amounts in parentheses
            is_negative = False
            if '(' in str_value and ')' in str_value:
                is_negative = True
                cleaned = cleaned.replace('(', '').replace(')', '')
            
            # Handle comma separators
            if ',' in cleaned and '.' in cleaned:
                # Assume comma is thousands separator if it appears before decimal
                parts = cleaned.split('.')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    cleaned = parts[0].replace(',', '') + '.' + parts[1]
            elif ',' in cleaned:
                # Check if comma might be decimal separator
                comma_parts = cleaned.split(',')
                if len(comma_parts) == 2 and len(comma_parts[1]) <= 2:
                    # Likely decimal separator
                    cleaned = comma_parts[0] + '.' + comma_parts[1]
                else:
                    # Likely thousands separator
                    cleaned = cleaned.replace(',', '')
            
            # Convert to float
            amount = float(cleaned) if cleaned else 0.0
            
            # Apply negative sign if detected
            if is_negative:
                amount = -amount
                
            return amount
            
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Could not convert amount '{value}': {e}")
            return 0.0

    def categorize_account(self, account_name: str) -> tuple:
        """Categorize account based on name patterns"""
        if not account_name:
            return ("Unknown", "Other")
        
        account_lower = account_name.lower().strip()
        
        for category, keywords in self.account_mappings.items():
            if any(keyword in account_lower for keyword in keywords):
                # Determine account type based on category
                if category == 'assets':
                    return ('Asset', category)
                elif category == 'liabilities':
                    return ('Liability', category)
                elif category == 'equity':
                    return ('Equity', category)
                elif category == 'revenue':
                    return ('Revenue', category)
                elif category == 'expenses':
                    return ('Expense', category)
        
        return ("Unknown", "other")

    def normalize_data(self, df: pd.DataFrame) -> List[FinancialRecord]:
        """Convert DataFrame to normalized FinancialRecord objects"""
        self.logger.info("Normalizing financial data")
        
        # Normalize column names
        df_normalized = self.normalize_column_names(df)
        
        records = []
        
        for index, row in df_normalized.iterrows():
            record = FinancialRecord(account_name="")
            
            # Extract account name - handle multiple possible column names
            account_name = ""
            for col in ['account_name', 'account', 'name']:
                if col in df_normalized.columns:
                    value = row.get(col)
                    if pd.notna(value) and str(value).strip():
                        account_name = str(value).strip()
                        break
            
            record.account_name = account_name
            
            # Extract description
            if 'description' in df_normalized.columns:
                desc_value = row.get('description')
                if pd.notna(desc_value):
                    record.description = str(desc_value).strip()
            
            # Extract amounts - prioritize debit/credit columns
            if 'debit' in df_normalized.columns:
                record.debit = self.clean_amount_value(row.get('debit'))
            
            if 'credit' in df_normalized.columns:
                record.credit = self.clean_amount_value(row.get('credit'))
            
            if 'balance' in df_normalized.columns:
                record.balance = self.clean_amount_value(row.get('balance'))
            
            # Handle single amount column
            if record.debit == 0 and record.credit == 0 and 'amount' in df_normalized.columns:
                amount = self.clean_amount_value(row.get('amount'))
                record.original_amount = amount
                
                # Determine if debit or credit based on type column or amount sign
                if 'type' in df_normalized.columns:
                    type_value = row.get('type')
                    if pd.notna(type_value):
                        type_str = str(type_value).lower()
                        if 'credit' in type_str or 'cr' in type_str:
                            record.credit = abs(amount)
                        else:
                            record.debit = abs(amount)
                    else:
                        # Default logic based on amount sign
                        if amount >= 0:
                            record.debit = amount
                        else:
                            record.credit = abs(amount)
                else:
                    # Use amount sign or default to debit for positive
                    if amount >= 0:
                        record.debit = amount
                    else:
                        record.credit = abs(amount)
            
            # If only balance is provided, convert based on sign
            if record.debit == 0 and record.credit == 0 and record.balance != 0:
                if record.balance >= 0:
                    record.debit = record.balance
                else:
                    record.credit = abs(record.balance)
            
            # Categorize account
            record.account_type, record.category = self.categorize_account(record.account_name)
            
            records.append(record)
        
        self.logger.info(f"Normalized {len(records)} financial records")
        return records

    def validate_records(self, records: List[FinancialRecord]) -> ValidationResult:
        """Validate normalized financial records"""
        self.logger.info("Validating financial records")
        
        errors = []
        warnings = []
        total_debits = 0.0
        total_credits = 0.0
        empty_accounts = 0
        zero_amounts = 0
        
        for record in records:
            # Accumulate totals
            total_debits += record.debit
            total_credits += record.credit
            
            # Check for empty account names
            if not record.account_name or len(record.account_name) < self.validation_rules['min_account_name_length']:
                empty_accounts += 1
            
            # Check for zero amounts
            if record.debit == 0 and record.credit == 0 and record.balance == 0:
                zero_amounts += 1
            
            # Check for excessive amounts
            max_amount = self.validation_rules['max_amount']
            if record.debit > max_amount or record.credit > max_amount:
                warnings.append(f"Large amount detected in account '{record.account_name}': ${max(record.debit, record.credit):,.2f}")
        
        # Calculate balance difference
        balance_difference = abs(total_debits - total_credits)
        
        # Validation checks
        if balance_difference > self.validation_rules['tolerance']:
            errors.append(f"Trial balance does not balance: Debits (${total_debits:,.2f}) ≠ Credits (${total_credits:,.2f}), Difference: ${balance_difference:,.2f}")
        
        if empty_accounts > 0:
            warnings.append(f"{empty_accounts} records have missing or invalid account names")
        
        if zero_amounts > 0:
            warnings.append(f"{zero_amounts} records have zero amounts")
        
        # Check for duplicate account names
        account_names = [r.account_name for r in records if r.account_name]
        if len(account_names) != len(set(account_names)):
            duplicates = len(account_names) - len(set(account_names))
            warnings.append(f"{duplicates} duplicate account names detected")
        
        is_valid = len(errors) == 0
        
        validation_result = ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            total_debits=total_debits,
            total_credits=total_credits,
            balance_difference=balance_difference,
            records_processed=len(records),
            empty_accounts=empty_accounts,
            zero_amounts=zero_amounts
        )
        
        self.logger.info(f"Validation complete: {'PASSED' if is_valid else 'FAILED'} - {len(errors)} errors, {len(warnings)} warnings")
        return validation_result

    def process_data(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Main validation method"""
        result = {
            'success': False,
            'normalized_records': [],
            'validation_result': None,
            'errors': []
        }
        
        try:
            if not extraction_result.get('success') or extraction_result.get('data') is None:
                result['errors'].append("No valid data to validate")
                return result
            
            df = extraction_result['data']
            
            if df.empty:
                result['errors'].append("Dataset is empty")
                return result
            
            self.logger.debug(f"Input DataFrame shape: {df.shape}")
            self.logger.debug(f"Input DataFrame columns: {df.columns.tolist()}")
            
            # Normalize data
            normalized_records = self.normalize_data(df)
            
            if not normalized_records:
                result['errors'].append("No records could be normalized")
                return result
            
            # Validate records
            validation_result = self.validate_records(normalized_records)
            
            result['success'] = True
            result['normalized_records'] = normalized_records
            result['validation_result'] = validation_result
            
            self.logger.info("Data validation process completed successfully")
            
        except Exception as e:
            error_msg = f"Validation process failed: {e}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg, exc_info=True)
        
        return result

    def get_summary_statistics(self, records: List[FinancialRecord]) -> Dict[str, Any]:
        """Generate summary statistics for financial records"""
        if not records:
            return {}
        
        stats = {
            'total_records': len(records),
            'account_types': {},
            'categories': {},
            'total_debits': 0.0,
            'total_credits': 0.0,
            'largest_debit': 0.0,
            'largest_credit': 0.0,
            'accounts_with_description': 0
        }
        
        for record in records:
            stats['total_debits'] += record.debit
            stats['total_credits'] += record.credit
            
            if record.debit > stats['largest_debit']:
                stats['largest_debit'] = record.debit
            
            if record.credit > stats['largest_credit']:
                stats['largest_credit'] = record.credit
            
            # Count by type and category
            if record.account_type:
                stats['account_types'][record.account_type] = stats['account_types'].get(record.account_type, 0) + 1
            
            if record.category:
                stats['categories'][record.category] = stats['categories'].get(record.category, 0) + 1
            
            if record.description:
                stats['accounts_with_description'] += 1
        
        return stats