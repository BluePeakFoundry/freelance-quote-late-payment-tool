import unittest
from datetime import date

from quote_core import QuoteError, calculate_quote, money


class QuoteCoreTests(unittest.TestCase):
    def test_standard_invoice_breakdown(self):
        r = calculate_quote(
            client="ACME",
            project="Landing audit",
            net_fee=1200,
            hours=18,
            vat_rate=21,
            withholding_rate=15,
            issue_date=date(2026, 8, 24),
            due_days=30,
        )
        self.assertEqual(r.invoice.vat_eur, money("252.00"))
        self.assertEqual(r.invoice.withholding_eur, money("180.00"))
        self.assertEqual(r.invoice.total_due_eur, money("1272.00"))
        self.assertEqual(r.late_payment.due_date, "2026-09-23")
        self.assertEqual(r.money_verified_eur, 0)

    def test_rounding_half_up_to_cents(self):
        r = calculate_quote(client="C", project="P", net_fee="100.005", hours=2, vat_rate="21", withholding_rate=0)
        self.assertEqual(r.invoice.net_fee_eur, money("100.01"))
        self.assertEqual(r.invoice.vat_eur, money("21.00"))

    def test_margin_below_target(self):
        r = calculate_quote(client="C", project="P", net_fee=200, hours=10, min_hourly_rate=30, buffer_rate=0)
        self.assertEqual(r.invoice.margin_status, "below_target")
        self.assertEqual(r.invoice.margin_gap_eur, money("100.00"))

    def test_margin_ok_with_buffer_and_fee(self):
        r = calculate_quote(client="C", project="P", net_fee=1000, hours=10, min_hourly_rate=70, buffer_rate=10, platform_fee_rate=5)
        self.assertEqual(r.invoice.platform_fee_eur, money("50.00"))
        self.assertEqual(r.invoice.buffer_eur, money("100.00"))
        self.assertEqual(r.invoice.margin_status, "ok")

    def test_late_payment_interest(self):
        r = calculate_quote(
            client="C",
            project="P",
            net_fee=1000,
            hours=10,
            vat_rate=21,
            withholding_rate=0,
            issue_date=date(2026, 1, 1),
            due_days=30,
            late_days=20,
            late_rate="11.15",
        )
        self.assertEqual(r.late_payment.due_date, "2026-01-31")
        self.assertEqual(r.late_payment.late_interest_eur, money("7.39"))
        self.assertEqual(r.late_payment.total_if_paid_late_eur, money("1217.39"))

    def test_invalid_inputs(self):
        with self.assertRaises(QuoteError):
            calculate_quote(client="", project="P", net_fee=100, hours=1)
        with self.assertRaises(QuoteError):
            calculate_quote(client="C", project="P", net_fee=0, hours=1)
        with self.assertRaises(QuoteError):
            calculate_quote(client="C", project="P", net_fee=100, hours=0)
        with self.assertRaises(QuoteError):
            calculate_quote(client="C", project="P", net_fee=100, hours=1, vat_rate=101)
        with self.assertRaises(QuoteError):
            calculate_quote(client="C", project="P", net_fee=100, hours=1, late_days=-1)


if __name__ == "__main__":
    unittest.main()
