# Cash Flow Statement
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
