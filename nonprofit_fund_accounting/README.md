# Non-Profit Fund Accounting

Turns the *Fund* analytic plan from `nonprofit_base` into enforced fund
accounting: a Fund is required on income and expense, donor restrictions
are released with a balanced entry, and net assets roll forward by fund.

Requires **Analytic Accounting** to be enabled (Settings → Accounting).

## What it adds

### Require a Fund on income & expense

Per company (Settings → Accounting → *Fund Accounting (Non-Profit)* →
**Require a Fund on income & expense**). When on, an `account.move`
cannot be posted while any line whose account is an income or expense
type is not assigned **100%** to *Fund* analytic accounts (split across
several funds is fine as long as the Fund-plan share totals 100%). The
balancing receivable / payable / cash / tax lines are never asked for a
Fund.

Bypass for opening balances, migrations or corrections with
`skip_fund_check` in the context:

```python
move.with_context(skip_fund_check=True).action_post()
```

### Release from restriction

**Accounting → Non-Profit → Restriction Releases**. A release picks the
restricted Fund it comes *from*, the Fund it goes *to* (default
*Unrestricted*), an amount, a date, and optionally a Program and
Function. Posting it creates a balanced journal entry:

| | Account | Analytic |
| --- | --- | --- |
| Dr | Net Assets Released - Restricted side | from-Fund (+ Program / Function) |
| Cr | Net Assets Released - Unrestricted side | to-Fund (+ Program / Function) |

Both accounts are income-type clearing accounts that net to zero
org-wide; the entry only reclassifies between fund columns. The release
is kept as a `nonprofit.restriction.release` record with a `REL/YYYY/…`
reference and chatter; **Cancel** reverses the entry.

The two clearing accounts are read from the company settings and
auto-detected from the `nonprofit_base` chart (accounts tagged
*NFP: Net Assets Released - …*) on install and via the **Detect from
chart** button.

### Net-asset roll-forward

**Accounting → Non-Profit → Net-Asset Roll-Forward**. For a date range,
per Fund: beginning balance, revenue, expense, restrictions released in /
out, ending balance. Beginning balance is the same figure accumulated for
everything dated before the start date (a from-inception roll-forward).
The two release clearing accounts are excluded from *revenue* so a
release is not double-counted.

## Settings

Settings → Accounting → **Fund Accounting (Non-Profit)**: the require-a-Fund
toggle, a default Program and Function (pre-filled on releases), and the
two Net Assets Released accounts.

## Requirements

Odoo 19 Community, `nonprofit_base`. No extra Python packages.

## Tests

`./testing` harness, `--test-tags=/nonprofit_fund_accounting` (16):
constraint blocks / passes / splits / toggles / skip-context; release
posts a balanced entry with the right analytic distribution, sequence,
program flow-through, same-fund and missing-account guards, cancel
reverses, account auto-detect; roll-forward numbers tie and exclude the
clearing accounts from revenue.
