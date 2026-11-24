# Nonprofit: Website Donations as Donations

Odoo's website Donation block (`website_payment`) takes the money but never
creates a donation in the OCA Donations app: no donor history, no tax
receipt. No OCA module bridges the two (checked OCA/donation 12.0 to 19.0,
2026-11-24). This one does, when an online donation's payment is done:

1. **The donor.** The payment is booked on a contact matched by email (or
   created from the name, email and country typed in the form) instead of
   the website's anonymous visitor (`_create_payment`).
2. **The donation.** A `donation.donation` is created and validated with the
   payment's method (marked as a donation method if it wasn't), so it shows in
   donor history and gets its numbered tax receipt the usual way
   (`nonprofit_donation_receipts`).
3. **Fees the donor covered** (`website_donation_cover_fees`): two lines, the
   gift ("Online donation") and the fees ("Processing fees covered by donor").
   Both are receipted by default: her decision on 2026-11-24, confirmed by
   her CPA the same day (better for donor transparency). Untick "Is Eligible for a Tax Receipt" on the fees product to leave
   them off.
4. **Booked once.** The website payment debits the bank side and credits the
   donor's receivable; the donation's entry debits that receivable (not the
   payment method's account) and credits donation income, and the two
   receivable lines are reconciled.

If creating the donation fails, the payment still goes through and a chatter
note on it says so.

## Testing

6 tests (`account_payment`'s test base): the donation is created and
validated, the receipt is issued, the payment is on the donor and matched,
a returning donor is matched by email, covered fees are their own line on
the receipt, and ordinary payments are left alone.
