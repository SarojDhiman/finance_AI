# Profit & Loss Statement
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
