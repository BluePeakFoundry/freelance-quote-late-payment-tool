#!/usr/bin/env python3
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

BASE = Path(__file__).resolve().parent
REQUIRED_FILES = [
    "index.html",
    "style.css",
    "app.js",
    "analytics.js",
    "README.md",
    "robots.txt",
    "sitemap.xml",
    "manifest.json",
    ".github/ISSUE_TEMPLATE/feedback.yml",
]
FORBIDDEN_PUBLIC_TERMS = ["R" + "ex", "Ser" + "gi", "autonomous", "money generated"]
REQUIRED_HTML_MARKERS = [
    "https://bluepeakfoundry.github.io/freelance-quote-late-payment-tool/",
    "bluepeakfoundry.goatcounter.com/count",
    "cta:freelance:start",
    "cta:freelance:copy-proposal",
    "cta:freelance:copy-reminder",
    "lead:freelance-feedback",
    "SoftwareApplication",
    "Do not include client names",
]
REQUIRED_FEEDBACK_MARKERS = [
    "Do not post client names",
    "bank details",
    "tax IDs",
    "contracts",
    "personal data",
    "confidential business information",
]

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.scripts = []
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "a" and "href" in data:
            self.links.append(data["href"])
        if tag == "script":
            self.scripts.append(data.get("src", "inline"))

def read(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8")

def main() -> int:
    missing = [rel for rel in REQUIRED_FILES if not (BASE / rel).exists()]
    if missing:
        raise SystemExit(f"missing files: {missing}")
    combined = "\n".join(read(rel) for rel in REQUIRED_FILES if rel.endswith((".html", ".js", ".md", ".yml", ".json", ".txt", ".xml")))
    forbidden = [term for term in FORBIDDEN_PUBLIC_TERMS if term.lower() in combined.lower()]
    if forbidden:
        raise SystemExit(f"forbidden public terms: {forbidden}")
    html = read("index.html")
    missing_html = [m for m in REQUIRED_HTML_MARKERS if m not in html]
    if missing_html:
        raise SystemExit(f"missing html markers: {missing_html}")
    parser = LinkParser(); parser.feed(html)
    if "https://github.com/BluePeakFoundry/freelance-quote-late-payment-tool/issues/new?template=feedback.yml" not in parser.links:
        raise SystemExit("feedback issue-form link missing")
    feedback = read(".github/ISSUE_TEMPLATE/feedback.yml")
    missing_feedback = [m for m in REQUIRED_FEEDBACK_MARKERS if m not in feedback]
    if missing_feedback:
        raise SystemExit(f"missing feedback safety markers: {missing_feedback}")
    manifest = json.loads(read("manifest.json"))
    if manifest.get("money_verified_eur") != 0:
        raise SystemExit("manifest money_verified_eur must be 0")
    if len(manifest.get("external_actions_performed", [])) < 4:
        raise SystemExit("manifest external actions are incomplete")
    print(f"FREELANCE_PUBLIC_SITE_OK files={len(REQUIRED_FILES)} money_verified_eur=0 external_actions={len(manifest['external_actions_performed'])}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
