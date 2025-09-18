# Balance Sheet
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
