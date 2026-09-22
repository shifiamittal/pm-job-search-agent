"""High-recall product-management candidate filter.

This filter is intentionally conservative: false positives can be removed by later
classification, while a false negative disappears from all downstream reasoning.
Every excluded job remains available in raw_all_jobs.jsonl for auditability.
"""

from __future__ import annotations

import re

# Strong PM-family signals. Product Marketing / Product Support / Product Operations
# are explicitly excluded below because they are separate job families.
PM_PATTERNS = [
    r"\bproduct\s+manager\b",
    r"\bproduct\s+management\b",
    r"\bprincipal\s+pm(?:-t)?\b",
    r"\bstaff\s+pm\b",
    r"\bgroup\s+product\s+manager\b",
    r"\bproduct\s+lead\b",
    r"\bproduct\s+owner\b",
    r"\bresearch\s+product\s+manager\b",
]

NON_PM_PATTERNS = [
    r"\bproduct\s+marketing\b",
    r"\bproduct\s+support\b",
    r"\bproduct\s+operations\b",
    r"\bproduct\s+designer\b",
    r"\bproduct\s+design\b",
    r"\bproduct\s+counsel\b",
]


def pm_candidate_decision(title: str) -> tuple[bool, str]:
    normalized = " ".join((title or "").casefold().split())
    for pattern in NON_PM_PATTERNS:
        if re.search(pattern, normalized):
            return False, f"excluded_non_pm_family:{pattern}"
    for pattern in PM_PATTERNS:
        if re.search(pattern, normalized):
            return True, f"included_pm_signal:{pattern}"
    return False, "no_pm_title_signal"
