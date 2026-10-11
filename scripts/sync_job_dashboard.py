"""Job dashboard writes are blocked pending shortlist v1 integration.

The existing spreadsheet identity, remote tabs and feedback remain untouched.
This module has no OAuth/network/write path. Candidate-source Sheet export in
sync_google_sheets.py is a separate, unchanged subsystem.
"""
import argparse
from copy import deepcopy
from pathlib import Path

from shortlist_contract import ShortlistIntegrationPending, integration_pending


class DashboardError(ShortlistIntegrationPending):
    """Retained public error type for the disabled writer."""


def read_legacy_feedback(values_by_tab):
    """Preserve supplied historical tab values exactly, without decision conversion.

    Includes unknown job IDs, duplicate rows, columns and free-text feedback. This
    does not fetch remote tabs, resolve conflicts, or modify canonical records.
    """
    return deepcopy(values_by_tab)


def sync_dashboard(*args, **kwargs):
    try:
        integration_pending("Persistent job dashboard synchronization")
    except ShortlistIntegrationPending as exc:
        raise DashboardError(str(exc)) from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials", type=Path, default=None, help="Retained CLI spelling; no credentials are read")
    parser.add_argument("--token", type=Path, default=None, help="Retained CLI spelling; no token is read")
    parser.parse_args()
    try:
        sync_dashboard()
    except DashboardError as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    main()
