"""Core calculations for the freelance quote and late-payment calculator.

This module is dependency-free. It is not legal, tax, accounting, or
professional advice: rates are user-editable and outputs are planning aids only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List

CENT = Decimal("0.01")


class QuoteError(ValueError):
    """Raised when quote input is invalid."""


def money(value: Decimal | float | int | str) -> Decimal:
    """Return a Decimal rounded to cents with commercial half-up rounding."""
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def percent(value: Decimal | float | int | str) -> Decimal:
    return Decimal(str(value)) / Decimal("100")


def require_range(name: str, value: Decimal, minimum: Decimal, maximum: Decimal) -> None:
    if value < minimum or value > maximum:
        raise QuoteError(f"{name} must be between {minimum} and {maximum}")

@dataclass(frozen=True)
class InvoiceBreakdown:
    net_fee_eur: Decimal
    vat_rate_percent: Decimal
    vat_eur: Decimal
    withholding_rate_percent: Decimal
    withholding_eur: Decimal
    total_due_eur: Decimal
    effective_hourly_eur: Decimal
    platform_fee_eur: Decimal
    buffer_eur: Decimal
    estimated_takehome_before_income_tax_eur: Decimal
    margin_status: str
    margin_gap_eur: Decimal

@dataclass(frozen=True)
class LatePaymentScenario:
    issue_date: str
    due_date: str
    late_days: int
    annual_late_rate_percent: Decimal
    late_interest_eur: Decimal
    total_if_paid_late_eur: Decimal

@dataclass(frozen=True)
class QuoteResult:
    client: str
    project: str
    invoice: InvoiceBreakdown
    late_payment: LatePaymentScenario
    proposal_text: str
    reminder_text: str
    disclaimers: List[str]
    money_verified_eur: int = 0

    def to_plain_dict(self) -> Dict[str, object]:
        def convert(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            if hasattr(obj, "__dataclass_fields__"):
                return {k: convert(v) for k, v in asdict(obj).items()}
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [convert(v) for v in obj]
            return obj
        return convert(self)

def calculate_quote(
    *,
    client: str,
    project: str,
    net_fee: Decimal | float | int | str,
    hours: Decimal | float | int | str,
    vat_rate: Decimal | float | int | str = 21,
    withholding_rate: Decimal | float | int | str = 15,
    platform_fee_rate: Decimal | float | int | str = 0,
    buffer_rate: Decimal | float | int | str = 10,
    min_hourly_rate: Decimal | float | int | str = 35,
    issue_date: date | None = None,
    due_days: int = 30,
    late_days: int = 0,
    late_rate: Decimal | float | int | str = 0,
) -> QuoteResult:
    client = client.strip() if client is not None else ""
    project = project.strip() if project is not None else ""
    net = money(net_fee)
    hrs = Decimal(str(hours))
    vat = Decimal(str(vat_rate))
    withholding = Decimal(str(withholding_rate))
    platform_fee_pct = Decimal(str(platform_fee_rate))
    buffer_pct = Decimal(str(buffer_rate))
    min_hourly = money(min_hourly_rate)
    late_pct = Decimal(str(late_rate))

    if not client:
        raise QuoteError("client is required")
    if not project:
        raise QuoteError("project is required")
    require_range("net_fee", net, Decimal("1"), Decimal("1000000"))
    require_range("hours", hrs, Decimal("0.25"), Decimal("10000"))
    for name, value in [
        ("vat_rate", vat),
        ("withholding_rate", withholding),
        ("platform_fee_rate", platform_fee_pct),
        ("buffer_rate", buffer_pct),
        ("late_rate", late_pct),
    ]:
        require_range(name, value, Decimal("0"), Decimal("100"))
    require_range("min_hourly_rate", min_hourly, Decimal("0"), Decimal("10000"))
    if due_days < 0 or due_days > 365:
        raise QuoteError("due_days must be between 0 and 365")
    if late_days < 0 or late_days > 3650:
        raise QuoteError("late_days must be between 0 and 3650")

    vat_eur = money(net * percent(vat))
    withholding_eur = money(net * percent(withholding))
    platform_fee_eur = money(net * percent(platform_fee_pct))
    buffer_eur = money(net * percent(buffer_pct))
    total_due = money(net + vat_eur - withholding_eur)
    takehome_before_income_tax = money(net - platform_fee_eur - buffer_eur)
    effective_hourly = money(takehome_before_income_tax / hrs)
    target_takehome = money(min_hourly * hrs)
    margin_gap = money(max(Decimal("0"), target_takehome - takehome_before_income_tax))
    margin_status = "ok" if margin_gap == 0 else "below_target"

    issued = issue_date or date.today()
    due = issued + timedelta(days=due_days)
    late_interest = money(total_due * percent(late_pct) * Decimal(late_days) / Decimal("365"))
    total_late = money(total_due + late_interest)

    proposal = (
        f"Proposal for {client}: {project}. Net fee: {net} EUR. "
        f"Editable VAT: {vat}% ({vat_eur} EUR). Editable withholding: "
        f"{withholding}% ({withholding_eur} EUR). Total due: {total_due} EUR. "
        f"Estimated hours: {hrs}; effective pre-income-tax/gross-expense hourly amount: "
        f"{effective_hourly} EUR/h."
    )
    reminder = (
        f"Friendly reminder for {client}: the {project} invoice is due on {due.isoformat()} "
        f"for {total_due} EUR. If paid {late_days} days late at an editable annual rate "
        f"of {late_pct}%, the informational late amount would be {late_interest} EUR."
    )

    return QuoteResult(
        client=client,
        project=project,
        invoice=InvoiceBreakdown(net, vat, vat_eur, withholding, withholding_eur, total_due, effective_hourly, platform_fee_eur, buffer_eur, takehome_before_income_tax, margin_status, margin_gap),
        late_payment=LatePaymentScenario(issued.isoformat(), due.isoformat(), late_days, late_pct, late_interest, total_late),
        proposal_text=proposal,
        reminder_text=reminder,
        disclaimers=[
            "Informational planning tool: not legal, tax, accounting, collection, or professional advice.",
            "VAT, withholding, late-payment rates, due dates, and fees are editable assumptions that should be verified before use.",
        ],
    )
