"""
Financial Data Generator - Creates sample datasets for testing and demonstration
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.settings import SAMPLE_DATA_DIR
from config.logging_config import get_logger

logger = get_logger('data_generator')

class FinancialDataGenerator:
    """Generates sample financial datasets for testing"""

    def __init__(self):
        self.logger = logger
        self.sample_folder = SAMPLE_DATA_DIR
        self.sample_folder.mkdir(exist_ok=True)
        
        # Seed for reproducible results
        np.random.seed(42)

    def generate_trial_balance(self, num_accounts: int = 50, company_name: str = "Sample Company") -> pd.DataFrame:
        """Generate a trial balance dataset"""
        
        # Define account categories with realistic account names
        account_templates = {
            'Assets': [
                'Cash - Operating Account', 'Cash - Savings Account', 'Petty Cash',
                'Accounts Receivable - Trade', 'Accounts Receivable - Other',
                'Inventory - Raw Materials', 'Inventory - Work in Process', 'Inventory - Finished Goods',
                'Prepaid Insurance', 'Prepaid Rent', 'Office Supplies',
                'Equipment - Office', 'Equipment - Manufacturing', 'Vehicles',
                'Building', 'Land', 'Accumulated Depreciation - Equipment',
                'Patents', 'Goodwill', 'Investments - Short Term', 'Investments - Long Term'
            ],
            'Liabilities': [
                'Accounts Payable - Trade', 'Accounts Payable - Other',
                'Accrued Salaries Payable', 'Accrued Interest Payable', 'Accrued Taxes Payable',
                'Notes Payable - Short Term', 'Credit Line Payable',
                'Mortgage Payable', 'Bonds Payable', 'Long Term Debt',
                'Deferred Revenue', 'Warranty Liability', 'Employee Benefits Payable'
            ],
            'Equity': [
                'Common Stock', 'Preferred Stock', 'Paid-in Capital in Excess of Par',
                'Retained Earnings', 'Treasury Stock', 'Accumulated Other Comprehensive Income'
            ],
            'Revenue': [
                'Sales Revenue - Product A', 'Sales Revenue - Product B', 'Sales Revenue - Services',
                'Interest Income', 'Dividend Income', 'Rental Income',
                'Gain on Sale of Assets', 'Other Income'
            ],
            'Expenses': [
                'Cost of Goods Sold', 'Salaries and Wages', 'Employee Benefits',
                'Rent Expense', 'Utilities Expense', 'Insurance Expense',
                'Office Supplies Expense', 'Advertising Expense', 'Travel Expense',
                'Professional Fees', 'Depreciation Expense', 'Interest Expense',
                'Bad Debt Expense', 'Repairs and Maintenance', 'Telephone Expense',
                'Training and Development', 'Bank Charges', 'Tax Expense'
            ]
        }
        
        data = []
        total_debits = 0.0
        total_credits = 0.0
        accounts_created = 0
        
        # Create accounts from each category
        for category, account_names in account_templates.items():
            category_accounts = min(len(account_names), max(1, num_accounts // 5))
            
            for i in range(category_accounts):
                if accounts_created >= num_accounts:
                    break
                
                account_name = account_names[i % len(account_names)]
                if i >= len(account_names):
                    account_name += f" - Division {i // len(account_names) + 1}"
                
                # Generate realistic amounts based on account type
                if category == 'Assets':
                    if 'cash' in account_name.lower():
                        amount = np.random.uniform(5000, 150000)
                    elif 'receivable' in account_name.lower():
                        amount = np.random.uniform(10000, 200000)
                    elif 'inventory' in account_name.lower():
                        amount = np.random.uniform(15000, 300000)
                    elif 'equipment' in account_name.lower() or 'building' in account_name.lower():
                        amount = np.random.uniform(50000, 500000)
                    else:
                        amount = np.random.uniform(1000, 100000)
                    
                    debit = round(amount, 2)
                    credit = 0.0
                    total_debits += debit
                
                elif category == 'Liabilities':
                    if 'payable' in account_name.lower():
                        amount = np.random.uniform(5000, 100000)
                    elif 'debt' in account_name.lower() or 'mortgage' in account_name.lower():
                        amount = np.random.uniform(20000, 400000)
                    else:
                        amount = np.random.uniform(2000, 50000)
                    
                    debit = 0.0
                    credit = round(amount, 2)
                    total_credits += credit
                
                elif category == 'Equity':
                    if 'stock' in account_name.lower():
                        amount = np.random.uniform(50000, 200000)
                    else:
                        amount = np.random.uniform(10000, 150000)
                    
                    debit = 0.0
                    credit = round(amount, 2)
                    total_credits += credit
                
                elif category == 'Revenue':
                    if 'sales' in account_name.lower():
                        amount = np.random.uniform(100000, 1000000)
                    else:
                        amount = np.random.uniform(1000, 50000)
                    
                    debit = 0.0
                    credit = round(amount, 2)
                    total_credits += credit
                
                else:  # Expenses
                    if 'salary' in account_name.lower() or 'wage' in account_name.lower():
                        amount = np.random.uniform(80000, 500000)
                    elif 'cost of goods' in account_name.lower():
                        amount = np.random.uniform(200000, 800000)
                    else:
                        amount = np.random.uniform(2000, 100000)
                    
                    debit = round(amount, 2)
                    credit = 0.0
                    total_debits += debit
                
                data.append({
                    'Account_Name': account_name,
                    'Account_Type': category,
                    'Debit': debit,
                    'Credit': credit,
                    'Balance': debit - credit,
                    'Description': f'{category} account for {company_name}'
                })
                
                accounts_created += 1
        
        # Create balancing entry if needed
        balance_diff = total_debits - total_credits
        if abs(balance_diff) > 0.01:  # More than 1 cent difference
            if balance_diff > 0:
                # Need more credits
                data.append({
                    'Account_Name': 'Retained Earnings - Balancing',
                    'Account_Type': 'Equity',
                    'Debit': 0.0,
                    'Credit': round(balance_diff, 2),
                    'Balance': -round(balance_diff, 2),
                    'Description': 'System balancing entry'
                })
            else:
                # Need more debits
                data.append({
                    'Account_Name': 'Miscellaneous Assets',
                    'Account_Type': 'Assets',
                    'Debit': round(abs(balance_diff), 2),
                    'Credit': 0.0,
                    'Balance': round(abs(balance_diff), 2),
                    'Description': 'System balancing entry'
                })
        
        df = pd.DataFrame(data)
        self.logger.info(f"Generated trial balance with {len(df)} accounts for {company_name}")
        return df

    def generate_balance_sheet_data(self, company_name: str = "Sample Company") -> pd.DataFrame:
        """Generate balance sheet focused data"""
        
        balance_sheet_accounts = {
            # Current Assets
            'Cash and Cash Equivalents': ('Asset', 85000),
            'Accounts Receivable': ('Asset', 125000),
            'Inventory': ('Asset', 180000),
            'Prepaid Expenses': ('Asset', 15000),
            
            # Non-Current Assets
            'Property Plant Equipment': ('Asset', 650000),
            'Accumulated Depreciation': ('Asset', -180000),  # Contra asset
            'Intangible Assets': ('Asset', 45000),
            'Investments': ('Asset', 75000),
            
            # Current Liabilities
            'Accounts Payable': ('Liability', 95000),
            'Accrued Expenses': ('Liability', 25000),
            'Short Term Debt': ('Liability', 50000),
            'Current Portion of Long Term Debt': ('Liability', 30000),
            
            # Non-Current Liabilities
            'Long Term Debt': ('Liability', 400000),
            'Deferred Tax Liability': ('Liability', 35000),
            
            # Equity
            'Common Stock': ('Equity', 200000),
            'Retained Earnings': ('Equity', 240000)
        }
        
        data = []
        for account_name, (account_type, amount) in balance_sheet_accounts.items():
            if account_type == 'Asset':
                if amount >= 0:
                    debit = amount
                    credit = 0
                else:  # Contra asset
                    debit = 0
                    credit = abs(amount)
                balance = amount
            else:  # Liability or Equity
                debit = 0
                credit = amount
                balance = -amount
            
            data.append({
                'Account': account_name,
                'Account_Type': account_type,
                'Debit': debit,
                'Credit': credit,
                'Balance': balance,
                'Company': company_name
            })
        
        df = pd.DataFrame(data)
        self.logger.info(f"Generated balance sheet data for {company_name}")
        return df

    def generate_income_statement_data(self, company_name: str = "Sample Company") -> pd.DataFrame:
        """Generate P&L statement data"""
        
        income_accounts = {
            # Revenue
            'Sales Revenue': ('Revenue', 1500000),
            'Service Revenue': ('Revenue', 250000),
            'Interest Income': ('Revenue', 8000),
            'Other Income': ('Revenue', 12000),
            
            # Cost of Sales
            'Cost of Goods Sold': ('Expense', 900000),
            
            # Operating Expenses
            'Salaries and Wages': ('Expense', 350000),
            'Employee Benefits': ('Expense', 85000),
            'Rent Expense': ('Expense', 60000),
            'Utilities': ('Expense', 18000),
            'Insurance': ('Expense', 25000),
            'Office Supplies': ('Expense', 8000),
            'Marketing and Advertising': ('Expense', 45000),
            'Professional Fees': ('Expense', 22000),
            'Depreciation': ('Expense', 35000),
            'Travel and Entertainment': ('Expense', 15000),
            
            # Other Expenses
            'Interest Expense': ('Expense', 28000),
            'Tax Expense': ('Expense', 45000)
        }
        
        data = []
        for account_name, (account_type, amount) in income_accounts.items():
            if account_type == 'Revenue':
                debit = 0
                credit = amount
            else:  # Expense
                debit = amount
                credit = 0
            
            data.append({
                'Account_Name': account_name,
                'Account_Type': account_type,
                'Amount': amount,
                'Debit': debit,
                'Credit': credit,
                'Company': company_name
            })
        
        df = pd.DataFrame(data)
        self.logger.info(f"Generated income statement data for {company_name}")
        return df

    def generate_cash_flow_data(self, company_name: str = "Sample Company") -> pd.DataFrame:
        """Generate cash flow statement data"""
        
        cash_flow_items = {
            # Operating Activities
            'Net Income': ('Operating', 155000),
            'Depreciation and Amortization': ('Operating', 35000),
            'Increase in Accounts Receivable': ('Operating', -25000),
            'Increase in Inventory': ('Operating', -35000),
            'Increase in Accounts Payable': ('Operating', 18000),
            'Decrease in Prepaid Expenses': ('Operating', 3000),
            
            # Investing Activities
            'Purchase of Equipment': ('Investing', -125000),
            'Sale of Investments': ('Investing', 45000),
            'Purchase of Intangible Assets': ('Investing', -20000),
            
            # Financing Activities
            'Proceeds from Long Term Debt': ('Financing', 100000),
            'Repayment of Debt': ('Financing', -50000),
            'Dividends Paid': ('Financing', -30000),
            'Issuance of Common Stock': ('Financing', 75000)
        }
        
        data = []
        for item_name, (category, amount) in cash_flow_items.items():
            data.append({
                'Cash_Flow_Item': item_name,
                'Category': category,
                'Amount': amount,
                'Company': company_name
            })
        
        df = pd.DataFrame(data)
        self.logger.info(f"Generated cash flow data for {company_name}")
        return df

    def create_sample_datasets(self) -> Dict[str, str]:
        """Create all sample datasets and save to files"""
        datasets_created = {}
        
        try:
            companies = ["TechStart Inc", "Manufacturing Corp", "Service Solutions LLC"]
            
            for i, company in enumerate(companies):
                # Trial Balance (different sizes)
                tb_sizes = [25, 50, 100]
                tb_df = self.generate_trial_balance(tb_sizes[i], company)
                tb_filename = f"trial_balance_{company.replace(' ', '_').lower()}_{tb_sizes[i]}_accounts.xlsx"
                tb_path = self.sample_folder / tb_filename
                tb_df.to_excel(tb_path, index=False)
                datasets_created[f"Trial Balance - {company}"] = str(tb_path)
                
                # Balance Sheet
                bs_df = self.generate_balance_sheet_data(company)
                bs_filename = f"balance_sheet_{company.replace(' ', '_').lower()}.xlsx"
                bs_path = self.sample_folder / bs_filename
                bs_df.to_excel(bs_path, index=False)
                datasets_created[f"Balance Sheet - {company}"] = str(bs_path)
                
                # Income Statement
                is_df = self.generate_income_statement_data(company)
                is_filename = f"income_statement_{company.replace(' ', '_').lower()}.xlsx"
                is_path = self.sample_folder / is_filename
                is_df.to_excel(is_path, index=False)
                datasets_created[f"Income Statement - {company}"] = str(is_path)
                
                # Cash Flow
                cf_df = self.generate_cash_flow_data(company)
                cf_filename = f"cash_flow_{company.replace(' ', '_').lower()}.xlsx"
                cf_path = self.sample_folder / cf_filename
                cf_df.to_excel(cf_path, index=False)
                datasets_created[f"Cash Flow - {company}"] = str(cf_path)
            
            # Create some CSV versions
            tb_df = self.generate_trial_balance(75, "Mixed Data Corp")
            csv_path = self.sample_folder / "trial_balance_mixed_data.csv"
            tb_df.to_csv(csv_path, index=False)
            datasets_created["Trial Balance - CSV Format"] = str(csv_path)
            
            self.logger.info(f"Created {len(datasets_created)} sample datasets")
            
        except Exception as e:
            self.logger.error(f"Error creating sample datasets: {e}")
            
        return datasets_created

    def generate_custom_dataset(self, 
                              accounts: List[Dict[str, Any]], 
                              filename: str = None) -> pd.DataFrame:
        """Generate custom dataset from provided account specifications"""
        
        data = []
        for account_spec in accounts:
            account_name = account_spec.get('name', 'Unknown Account')
            account_type = account_spec.get('type', 'Other')
            amount = account_spec.get('amount', 0)
            is_credit = account_spec.get('is_credit', False)
            
            if is_credit:
                debit = 0
                credit = abs(amount)
                balance = -abs(amount)
            else:
                debit = abs(amount)
                credit = 0
                balance = abs(amount)
            
            data.append({
                'Account_Name': account_name,
                'Account_Type': account_type,
                'Debit': debit,
                'Credit': credit,
                'Balance': balance,
                'Description': account_spec.get('description', '')
            })
        
        df = pd.DataFrame(data)
        
        if filename:
            file_path = self.sample_folder / filename
            if filename.endswith('.csv'):
                df.to_csv(file_path, index=False)
            else:
                df.to_excel(file_path, index=False)
            self.logger.info(f"Custom dataset saved: {file_path}")
        
        return df

    def get_sample_files_list(self) -> List[Dict[str, Any]]:
        """Get list of available sample files"""
        sample_files = []
        
        if self.sample_folder.exists():
            for file_path in self.sample_folder.iterdir():
                if file_path.is_file() and file_path.suffix in ['.xlsx', '.csv']:
                    try:
                        file_info = {
                            'filename': file_path.name,
                            'path': str(file_path),
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            'type': file_path.suffix
                        }
                        sample_files.append(file_info)
                    except Exception as e:
                        self.logger.warning(f"Error reading file info for {file_path}: {e}")
        
        return sample_files