"""
Generates the JSON audit report after export.
"""
import json
import datetime
from pathlib import Path
from collections import defaultdict


def generate_report(original_path: str,
                    output_path: str,
                    findings,
                    custom_patterns) -> dict:
    counts_by_cat = defaultdict(int)
    ignored_by_cat = defaultdict(int)

    for f in findings:
        if f.kept:
            counts_by_cat[f.category_id] += 1
        else:
            ignored_by_cat[f.category_id] += 1

    report = {
        "pii_shield_version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "source_file": str(Path(original_path).name),
        "output_file": str(Path(output_path).name),
        "total_findings": len(findings),
        "total_redacted": sum(1 for f in findings if f.kept),
        "total_ignored": sum(1 for f in findings if not f.kept),
        "redacted_by_category": dict(counts_by_cat),
        "ignored_by_category": dict(ignored_by_cat),
        "custom_patterns_used": [
            {"name": cp.get("name", ""), "pattern": cp.get("pattern", "")}
            for cp in custom_patterns if cp.get("pattern", "").strip()
        ],
        "note": "Original file was not modified. A new anonymized copy was created."
    }
    return report


def save_report(report: dict, report_path: str):
    Path(report_path).write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
