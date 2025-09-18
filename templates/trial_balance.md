# Trial Balance
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
