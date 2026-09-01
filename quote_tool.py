#!/usr/bin/env python3
"""CLI for the freelance quote and late-payment calculator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from quote_core import QuoteError, calculate_quote


def markdown(result) -> str:
    data = result.to_plain_dict()
    inv = data["invoice"]
    late = data["late_payment"]
    lines = [
        "# Freelance Quote Pack",
        "",
        f"- Client: {data['client']}",
        f"- Project: {data['project']}",
        f"- Money verified: {data['money_verified_eur']} EUR",
        "",
        "## Invoice breakdown",
        "",
        f"- Net fee: {inv['net_fee_eur']:.2f} EUR",
        f"- VAT ({inv['vat_rate_percent']}%): {inv['vat_eur']:.2f} EUR",
        f"- Withholding ({inv['withholding_rate_percent']}%): -{inv['withholding_eur']:.2f} EUR",
        f"- Total due: {inv['total_due_eur']:.2f} EUR",
        f"- Effective hourly after configurable buffer/platform fee: {inv['effective_hourly_eur']:.2f} EUR/h",
        f"- Margin status: {inv['margin_status']} (gap {inv['margin_gap_eur']:.2f} EUR)",
        "",
        "## Late-payment scenario",
        "",
        f"- Issue date: {late['issue_date']}",
        f"- Due date: {late['due_date']}",
        f"- Late days: {late['late_days']}",
        f"- Annual late rate: {late['annual_late_rate_percent']}%",
        f"- Informative late amount: {late['late_interest_eur']:.2f} EUR",
        f"- Total if paid late: {late['total_if_paid_late_eur']:.2f} EUR",
        "",
        "## Copyable proposal",
        "",
        data["proposal_text"],
        "",
        "## Copyable reminder",
        "",
        data["reminder_text"],
        "",
        "## Disclaimers",
        "",
    ]
    lines += [f"- {d}" for d in data["disclaimers"]]
    lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generate a local freelance quote pack.")
    p.add_argument("--client", required=True)
    p.add_argument("--project", required=True)
    p.add_argument("--net", required=True, type=str)
    p.add_argument("--hours", required=True, type=str)
    p.add_argument("--vat", default="21")
    p.add_argument("--withholding", default="15")
    p.add_argument("--platform-fee", default="0")
    p.add_argument("--buffer", default="10")
    p.add_argument("--min-hourly", default="35")
    p.add_argument("--due-days", default=30, type=int)
    p.add_argument("--late-days", default=0, type=int)
    p.add_argument("--late-rate", default="0")
    p.add_argument("--json", dest="json_path", required=True)
    p.add_argument("--markdown", dest="markdown_path", required=True)
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = calculate_quote(
            client=args.client,
            project=args.project,
            net_fee=args.net,
            hours=args.hours,
            vat_rate=args.vat,
            withholding_rate=args.withholding,
            platform_fee_rate=args.platform_fee,
            buffer_rate=args.buffer,
            min_hourly_rate=args.min_hourly,
            due_days=args.due_days,
            late_days=args.late_days,
            late_rate=args.late_rate,
        )
    except QuoteError as exc:
        raise SystemExit(f"input error: {exc}")

    json_path = Path(args.json_path)
    markdown_path = Path(args.markdown_path)
    json_path.write_text(json.dumps(result.to_plain_dict(), indent=2, ensure_ascii=False) + "\n")
    markdown_path.write_text(markdown(result))
    print(f"wrote {json_path} and {markdown_path}")
    print(f"total_due_eur={result.invoice.total_due_eur} late_amount_eur={result.late_payment.late_interest_eur} money_verified_eur=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
