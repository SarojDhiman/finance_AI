"""
Template Intelligence Agent - Handles template detection and data mapping
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from config.logging_config import get_logger
from config.settings import TEMPLATES_DIR, ACCOUNT_CATEGORIES
from .validation_agent import FinancialRecord

try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

logger = get_logger('template')

class TemplateIntelligenceAgent:
    """Handles template detection and placeholder mapping"""

    def __init__(self):
        self.logger = logger
        self.templates_folder = TEMPLATES_DIR
        self.templates_folder.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment if available
        if JINJA2_AVAILABLE:
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_folder)),
                autoescape=False
            )
        else:
            self.jinja_env = None
            self.logger.warning("Jinja2 not available - using simple string replacement")
        
        self.create_default_templates()

    def create_default_templates(self):
        """Create default financial statement templates"""
        templates = {
            'balance_sheet.md': self._get_balance_sheet_template(),
            'profit_loss.md': self._get_profit_loss_template(),
            'trial_balance.md': self._get_trial_balance_template(),
            'cash_flow.md': self._get_cash_flow_template()
        }
        
        for filename, content in templates.items():
            template_path = self.templates_folder / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"Created template: {filename}")
        
        self.logger.info(f"Template initialization complete - {len(templates)} templates available")

    def _get_balance_sheet_template(self) -> str:
        """Balance Sheet template"""
        return """# Balance Sheet
**{{ company_name | default('Company Name') }}**
**As of {{ date }}**

---

## ASSETS

### Current Assets
| Account | Amount |
|---------|--------|
| Cash and Cash Equivalents | ${{ "%.2f" | format(cash | default(0)) }} |
| Accounts Receivable | ${{ "%.2f" | format(accounts_receivable | default(0)) }} |
| Inventory | ${{ "%.2f" | format(inventory | default(0)) }} |
| Prepaid Expenses | ${{ "%.2f" | format(prepaid_expenses | default(0)) }} |
| **Total Current Assets** | **${{ "%.2f" | format(total_current_assets | default(0)) }}** |

### Non-Current Assets
| Account | Amount |
|---------|--------|
| Property, Plant & Equipment | ${{ "%.2f" | format(ppe | default(0)) }} |
| Investments | ${{ "%.2f" | format(investments | default(0)) }} |
| Intangible Assets | ${{ "%.2f" | format(intangible_assets | default(0)) }} |
| **Total Non-Current Assets** | **${{ "%.2f" | format(total_non_current_assets | default(0)) }}** |

### **TOTAL ASSETS: ${{ "%.2f" | format(total_assets | default(0)) }}**

---

## LIABILITIES AND EQUITY

### Current Liabilities
| Account | Amount |
|---------|--------|
| Accounts Payable | ${{ "%.2f" | format(accounts_payable | default(0)) }} |
| Accrued Expenses | ${{ "%.2f" | format(accrued_expenses | default(0)) }} |
| Short-term Debt | ${{ "%.2f" | format(short_term_debt | default(0)) }} |
| **Total Current Liabilities** | **${{ "%.2f" | format(total_current_liabilities | default(0)) }}** |

### Non-Current Liabilities
| Account | Amount |
|---------|--------|
| Long-term Debt | ${{ "%.2f" | format(long_term_debt | default(0)) }} |
| Deferred Tax Liabilities | ${{ "%.2f" | format(deferred_tax | default(0)) }} |
| **Total Non-Current Liabilities** | **${{ "%.2f" | format(total_non_current_liabilities | default(0)) }}** |

### Equity
| Account | Amount |
|---------|--------|
| Share Capital | ${{ "%.2f" | format(share_capital | default(0)) }} |
| Retained Earnings | ${{ "%.2f" | format(retained_earnings | default(0)) }} |
| **Total Equity** | **${{ "%.2f" | format(total_equity | default(0)) }}** |

### **TOTAL LIABILITIES AND EQUITY: ${{ "%.2f" | format(total_liab_equity | default(0)) }}**

---

**Balance Check:** {% if balance_check %}✅ Balanced{% else %}❌ Not Balanced (Difference: ${{ "%.2f" | format(balance_difference | default(0)) }}){% endif %}

**Report Generated:** {{ generation_date }}
"""

    def _get_profit_loss_template(self) -> str:
        """Profit & Loss Statement template"""
        return """# Profit & Loss Statement
**{{ company_name | default('Company Name') }}**
**For the period ending {{ date }}**

---

## REVENUE
| Account | Amount |
|---------|--------|
| Sales Revenue | ${{ "%.2f" | format(sales_revenue | default(0)) }} |
| Service Revenue | ${{ "%.2f" | format(service_revenue | default(0)) }} |
| Other Income | ${{ "%.2f" | format(other_income | default(0)) }} |
| **Total Revenue** | **${{ "%.2f" | format(total_revenue | default(0)) }}** |

---

## EXPENSES

### Cost of Sales
| Account | Amount |
|---------|--------|
| Cost of Goods Sold | ${{ "%.2f" | format(cogs | default(0)) }} |
| **Gross Profit** | **${{ "%.2f" | format(gross_profit | default(0)) }}** |

### Operating Expenses
| Account | Amount |
|---------|--------|
| Salaries and Wages | ${{ "%.2f" | format(salaries | default(0)) }} |
| Rent Expense | ${{ "%.2f" | format(rent | default(0)) }} |
| Utilities | ${{ "%.2f" | format(utilities | default(0)) }} |
| Insurance | ${{ "%.2f" | format(insurance | default(0)) }} |
| Depreciation | ${{ "%.2f" | format(depreciation | default(0)) }} |
| Marketing & Advertising | ${{ "%.2f" | format(marketing | default(0)) }} |
| Professional Fees | ${{ "%.2f" | format(professional_fees | default(0)) }} |
| Office Expenses | ${{ "%.2f" | format(office_expenses | default(0)) }} |
| Other Expenses | ${{ "%.2f" | format(other_expenses | default(0)) }} |
| **Total Operating Expenses** | **${{ "%.2f" | format(total_operating_expenses | default(0)) }}** |

### **Operating Income: ${{ "%.2f" | format(operating_income | default(0)) }}**

### Other Income/Expenses
| Account | Amount |
|---------|--------|
| Interest Income | ${{ "%.2f" | format(interest_income | default(0)) }} |
| Interest Expense | ${{ "%.2f" | format(interest_expense | default(0)) }} |
| **Net Other Income** | **${{ "%.2f" | format(net_other_income | default(0)) }}** |

---

### **NET INCOME: ${{ "%.2f" | format(net_income | default(0)) }}**

---

**Key Ratios:**
- Gross Profit Margin: {{ "%.1f" | format(gross_margin | default(0)) }}%
- Operating Margin: {{ "%.1f" | format(operating_margin | default(0)) }}%
- Net Profit Margin: {{ "%.1f" | format(net_margin | default(0)) }}%

**Report Generated:** {{ generation_date }}
"""

    def _get_trial_balance_template(self) -> str:
        """Trial Balance template"""
        return """# Trial Balance
**{{ company_name | default('Company Name') }}**
**As of {{ date }}**

---

| Account Name | Account Type | Debit | Credit |
|--------------|--------------|-------|--------|
{% for account in accounts -%}
| {{ account.name }} | {{ account.type }} | ${{ "%.2f" | format(account.debit | default(0)) }} | ${{ "%.2f" | format(account.credit | default(0)) }} |
{% endfor -%}

---

| **TOTALS** | | **${{ "%.2f" | format(total_debits | default(0)) }}** | **${{ "%.2f" | format(total_credits | default(0)) }}** |

---

**Balance Verification:**
{% if balance_check -%}
✅ **Trial Balance is BALANCED**
{% else -%}
❌ **Trial Balance is NOT BALANCED**
- **Difference:** ${{ "%.2f" | format(balance_difference | default(0)) }}
{% endif %}

**Summary Statistics:**
- **Total Accounts:** {{ total_accounts | default(0) }}
- **Total Debits:** ${{ "%.2f" | format(total_debits | default(0)) }}
- **Total Credits:** ${{ "%.2f" | format(total_credits | default(0)) }}

**Account Breakdown by Type:**
{% for type, count in account_type_summary.items() -%}
- **{{ type }}:** {{ count }} accounts
{% endfor %}

**Report Generated:** {{ generation_date }}
"""

    def _get_cash_flow_template(self) -> str:
        """Cash Flow Statement template"""
        return """# Cash Flow Statement
**{{ company_name | default('Company Name') }}**
**For the period ending {{ date }}**

---

## CASH FLOWS FROM OPERATING ACTIVITIES
| Item | Amount |
|------|--------|
| Net Income | ${{ "%.2f" | format(net_income | default(0)) }} |
| Adjustments: | |
| &nbsp;&nbsp;Depreciation | ${{ "%.2f" | format(depreciation | default(0)) }} |
| &nbsp;&nbsp;Changes in Working Capital: | |
| &nbsp;&nbsp;&nbsp;&nbsp;Accounts Receivable | ${{ "%.2f" | format(ar_change | default(0)) }} |
| &nbsp;&nbsp;&nbsp;&nbsp;Inventory | ${{ "%.2f" | format(inventory_change | default(0)) }} |
| &nbsp;&nbsp;&nbsp;&nbsp;Accounts Payable | ${{ "%.2f" | format(ap_change | default(0)) }} |
| **Net Cash from Operating Activities** | **${{ "%.2f" | format(operating_cash_flow | default(0)) }}** |

---

## CASH FLOWS FROM INVESTING ACTIVITIES
| Item | Amount |
|------|--------|
| Purchase of Equipment | ${{ "%.2f" | format(equipment_purchase | default(0)) }} |
| Sale of Investments | ${{ "%.2f" | format(investment_sale | default(0)) }} |
| **Net Cash from Investing Activities** | **${{ "%.2f" | format(investing_cash_flow | default(0)) }}** |

---

## CASH FLOWS FROM FINANCING ACTIVITIES
| Item | Amount |
|------|--------|
| Proceeds from Debt | ${{ "%.2f" | format(debt_proceeds | default(0)) }} |
| Repayment of Debt | ${{ "%.2f" | format(debt_repayment | default(0)) }} |
| Dividends Paid | ${{ "%.2f" | format(dividends | default(0)) }} |
| **Net Cash from Financing Activities** | **${{ "%.2f" | format(financing_cash_flow | default(0)) }}** |

---

## NET CHANGE IN CASH
| Item | Amount |
|------|--------|
| Net Change in Cash | ${{ "%.2f" | format(net_cash_change | default(0)) }} |
| Cash at Beginning of Period | ${{ "%.2f" | format(beginning_cash | default(0)) }} |
| **Cash at End of Period** | **${{ "%.2f" | format(ending_cash | default(0)) }}** |

**Report Generated:** {{ generation_date }}
"""

    def detect_statement_type(self, records: List[FinancialRecord]) -> str:
        """Detect the most appropriate financial statement template"""
        if not records:
            return 'trial_balance.md'
        
        # Analyze account types and categories
        account_types = {}
        categories = {}
        
        for record in records:
            if record.account_type:
                account_types[record.account_type] = account_types.get(record.account_type, 0) + 1
            if record.category:
                categories[record.category] = categories.get(record.category, 0) + 1
        
        # Decision logic for template selection
        balance_sheet_indicators = sum(account_types.get(t, 0) for t in ['Asset', 'Liability', 'Equity'])
        income_statement_indicators = sum(account_types.get(t, 0) for t in ['Revenue', 'Expense'])
        
        self.logger.debug(f"Template detection - BS indicators: {balance_sheet_indicators}, IS indicators: {income_statement_indicators}")
        
        # If mostly assets, liabilities, and equity -> Balance Sheet
        if balance_sheet_indicators > income_statement_indicators and balance_sheet_indicators >= len(records) * 0.6:
            return 'balance_sheet.md'
        
        # If mostly revenue and expenses -> Income Statement
        elif income_statement_indicators > balance_sheet_indicators and income_statement_indicators >= len(records) * 0.5:
            return 'profit_loss.md'
        
        # Default to trial balance for mixed or unclear data
        else:
            return 'trial_balance.md'

    def map_data_to_template(self, records: List[FinancialRecord], template_type: str) -> Dict[str, Any]:
        """Map financial records to template variables"""
        self.logger.info(f"Mapping data to template: {template_type}")
        
        # Base template data
        template_data = {
            'company_name': 'Your Company Name',
            'date': datetime.now().strftime('%B %d, %Y'),
            'generation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_accounts': len(records),
            'accounts': [],
            'total_debits': 0.0,
            'total_credits': 0.0,
            'balance_difference': 0.0,
            'balance_check': False
        }
        
        # Process records for common calculations
        account_summary = {}
        account_type_summary = {}
        
        for record in records:
            template_data['total_debits'] += record.debit
            template_data['total_credits'] += record.credit
            
            # Account type summary
            if record.account_type:
                account_type_summary[record.account_type] = account_type_summary.get(record.account_type, 0) + 1
            
            # For trial balance and other uses
            template_data['accounts'].append({
                'name': record.account_name,
                'type': record.account_type,
                'debit': record.debit,
                'credit': record.credit,
                'balance': record.balance
            })
            
            # Accumulate by account category for specific statements
            category = record.category.lower() if record.category else 'other'
            account_name_lower = record.account_name.lower()
            
            # Map specific accounts
            if 'cash' in account_name_lower or 'bank' in account_name_lower:
                template_data['cash'] = template_data.get('cash', 0) + (record.debit or record.balance)
            elif 'receivable' in account_name_lower:
                template_data['accounts_receivable'] = template_data.get('accounts_receivable', 0) + (record.debit or record.balance)
            elif 'inventory' in account_name_lower:
                template_data['inventory'] = template_data.get('inventory', 0) + (record.debit or record.balance)
            elif 'payable' in account_name_lower:
                template_data['accounts_payable'] = template_data.get('accounts_payable', 0) + (record.credit or abs(record.balance))
            elif 'revenue' in account_name_lower or 'sales' in account_name_lower:
                if 'service' in account_name_lower:
                    template_data['service_revenue'] = template_data.get('service_revenue', 0) + (record.credit or abs(record.balance))
                else:
                    template_data['sales_revenue'] = template_data.get('sales_revenue', 0) + (record.credit or abs(record.balance))
            elif 'expense' in account_name_lower or 'cost' in account_name_lower:
                if 'salary' in account_name_lower or 'wage' in account_name_lower:
                    template_data['salaries'] = template_data.get('salaries', 0) + (record.debit or record.balance)
                elif 'rent' in account_name_lower:
                    template_data['rent'] = template_data.get('rent', 0) + (record.debit or record.balance)
                elif 'utility' in account_name_lower or 'utilities' in account_name_lower:
                    template_data['utilities'] = template_data.get('utilities', 0) + (record.debit or record.balance)
                elif 'cogs' in account_name_lower or 'cost of goods' in account_name_lower:
                    template_data['cogs'] = template_data.get('cogs', 0) + (record.debit or record.balance)
                else:
                    template_data['other_expenses'] = template_data.get('other_expenses', 0) + (record.debit or record.balance)
        
        # Calculate balance check
        template_data['balance_difference'] = abs(template_data['total_debits'] - template_data['total_credits'])
        template_data['balance_check'] = template_data['balance_difference'] <= 0.01
        template_data['account_type_summary'] = account_type_summary
        
        # Template-specific calculations
        if template_type == 'balance_sheet.md':
            self._calculate_balance_sheet_totals(template_data)
        elif template_type == 'profit_loss.md':
            self._calculate_income_statement_totals(template_data)
        
        self.logger.info(f"Template data mapping completed for {template_type}")
        return template_data

    def _calculate_balance_sheet_totals(self, data: Dict[str, Any]):
        """Calculate Balance Sheet specific totals"""
        # Current Assets
        data['total_current_assets'] = sum([
            data.get('cash', 0),
            data.get('accounts_receivable', 0),
            data.get('inventory', 0),
            data.get('prepaid_expenses', 0)
        ])
        
        # Non-Current Assets
        data['total_non_current_assets'] = sum([
            data.get('ppe', 0),
            data.get('investments', 0),
            data.get('intangible_assets', 0)
        ])
        
        data['total_assets'] = data['total_current_assets'] + data['total_non_current_assets']
        
        # Current Liabilities
        data['total_current_liabilities'] = sum([
            data.get('accounts_payable', 0),
            data.get('accrued_expenses', 0),
            data.get('short_term_debt', 0)
        ])
        
        # Non-Current Liabilities
        data['total_non_current_liabilities'] = sum([
            data.get('long_term_debt', 0),
            data.get('deferred_tax', 0)
        ])
        
        # Equity
        data['total_equity'] = sum([
            data.get('share_capital', 0),
            data.get('retained_earnings', 0)
        ])
        
        data['total_liab_equity'] = data['total_current_liabilities'] + data['total_non_current_liabilities'] + data['total_equity']

    def _calculate_income_statement_totals(self, data: Dict[str, Any]):
        """Calculate Income Statement specific totals"""
        # Revenue calculations
        data['total_revenue'] = sum([
            data.get('sales_revenue', 0),
            data.get('service_revenue', 0),
            data.get('other_income', 0)
        ])
        
        # Gross Profit
        data['gross_profit'] = data['total_revenue'] - data.get('cogs', 0)
        
        # Operating Expenses
        data['total_operating_expenses'] = sum([
            data.get('salaries', 0),
            data.get('rent', 0),
            data.get('utilities', 0),
            data.get('insurance', 0),
            data.get('depreciation', 0),
            data.get('marketing', 0),
            data.get('professional_fees', 0),
            data.get('office_expenses', 0),
            data.get('other_expenses', 0)
        ])
        
        # Operating Income
        data['operating_income'] = data['gross_profit'] - data['total_operating_expenses']
        
        # Net Other Income
        data['net_other_income'] = data.get('interest_income', 0) - data.get('interest_expense', 0)
        
        # Net Income
        data['net_income'] = data['operating_income'] + data['net_other_income']
        
        # Calculate margins (avoid division by zero)
        if data['total_revenue'] > 0:
            data['gross_margin'] = (data['gross_profit'] / data['total_revenue']) * 100
            data['operating_margin'] = (data['operating_income'] / data['total_revenue']) * 100
            data['net_margin'] = (data['net_income'] / data['total_revenue']) * 100
        else:
            data['gross_margin'] = 0
            data['operating_margin'] = 0
            data['net_margin'] = 0

    def generate_statement(self, records: List[FinancialRecord], template_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate financial statement from records"""
        result = {
            'success': False,
            'content': '',
            'template_used': '',
            'template_data': {},
            'errors': []
        }
        
        try:
            if not records:
                result['errors'].append("No records provided for statement generation")
                return result
            
            # Auto-detect template if not specified
            if not template_type:
                template_type = self.detect_statement_type(records)
            
            # Map data to template
            template_data = self.map_data_to_template(records, template_type)
            
            # Generate content
            template_path = self.templates_folder / template_type
            if not template_path.exists():
                result['errors'].append(f"Template not found: {template_type}")
                return result
            
            # Load and render template
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            if self.jinja_env:
                # Use Jinja2 rendering
                template = self.jinja_env.from_string(template_content)
                rendered_content = template.render(**template_data)
            else:
                # Simple string replacement fallback
                rendered_content = self._simple_template_render(template_content, template_data)
            
            result['success'] = True
            result['content'] = rendered_content
            result['template_used'] = template_type
            result['template_data'] = template_data
            
            self.logger.info(f"Financial statement generated successfully using {template_type}")
            
        except Exception as e:
            error_msg = f"Statement generation failed: {e}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg)
        
        return result

    def _simple_template_render(self, template_content: str, data: Dict[str, Any]) -> str:
        """Simple template rendering without Jinja2"""
        import re
        
        content = template_content
        
        # Handle simple variable substitutions {{ variable }}
        def replace_simple_var(match):
            var_name = match.group(1).strip()
            return str(data.get(var_name, '0.00'))
        
        content = re.sub(r'\{\{\s*([^|{}]+)\s*\}\}', replace_simple_var, content)
        
        # Handle formatted numbers {{ "%.2f" | format(variable) }}
        def replace_format_var(match):
            var_name = match.group(1).strip()
            value = data.get(var_name, 0)
            try:
                return f"{float(value):.2f}"
            except:
                return "0.00"
        
        content = re.sub(r'\{\{\s*"%.2f"\s*\|\s*format\(([^)]+)\)\s*\}\}', replace_format_var, content)
        
        # Handle default values {{ variable | default(0) }}
        def replace_default_var(match):
            var_name = match.group(1).strip()
            default_val = match.group(2).strip()
            value = data.get(var_name, default_val)
            return str(value)
        
        content = re.sub(r'\{\{\s*([^|{}]+)\s*\|\s*default\(([^)]+)\)\s*\}\}', replace_default_var, content)
        
        return content

    def list_available_templates(self) -> List[str]:
        """List all available templates"""
        templates = []
        if self.templates_folder.exists():
            for template_file in self.templates_folder.glob('*.md'):
                templates.append(template_file.name)
        return templates

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a specific template"""
        template_path = self.templates_folder / template_name
        if not template_path.exists():
            return {'exists': False, 'error': 'Template not found'}
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract variables used in template
            import re
            variables = set(re.findall(r'\{\{\s*([^|{}]+?)(?:\s*\|[^}]*)?\s*\}\}', content))
            
            return {
                'exists': True,
                'name': template_name,
                'path': str(template_path),
                'variables': list(variables),
                'size': len(content),
                'lines': len(content.split('\n'))
            }
        except Exception as e:
            return {'exists': False, 'error': str(e)}