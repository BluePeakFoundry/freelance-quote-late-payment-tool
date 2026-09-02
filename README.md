# Freelance Quote & Late-Payment Calculator

Free, static browser tool for preparing a transparent freelance quote, checking an effective hourly margin after editable assumptions, setting a due date, and copying payment follow-up text.

Public site: https://bluepeakfoundry.github.io/freelance-quote-late-payment-tool/

## What it does

- Calculates net fee, editable VAT, editable withholding, total due, platform-fee/buffer impact, and effective EUR/hour.
- Creates copyable proposal and payment reminder text.
- Provides downloadable CSV and Markdown quote-prep templates for private use.
- Runs entirely in the browser; no accounts, server submissions, or stored inputs.
- Provides a public feedback channel for generalized product feedback only.

## Important limits

This is an informational planning tool, not legal, tax, accounting, debt-collection, or professional advice. VAT, withholding, late-payment rates, due dates, contract terms, and platform fees vary by jurisdiction and agreement. Verify current official guidance or professional advice before using any output.

Do not post client names, bank details, tax IDs, contracts, invoices, personal data, or confidential business information in public GitHub Issues.

## Local development checks

```bash
python3 -m unittest -q
python3 quote_tool.py --client "Client example" --project "Website audit" --net 1200 --hours 18 --vat 21 --withholding 15 --due-days 30 --late-days 20 --late-rate 11.15 --json sample_quote_20260901T140438Z.json --markdown sample_quote_20260901T140438Z.md
python3 validate_public_site.py
node --check app.js
node --check analytics.js
python3 -m json.tool manifest.json >/tmp/freelance_quote_manifest_check.json
```
