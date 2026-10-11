"""Classified-job finalization is blocked pending shared shortlist v1 persistence integration.

Raw discovery in scripts/discover_jobs.py is unaffected. No input is read, merged,
reclassified, persisted or synchronized through this retired entrypoint.
"""
import argparse
from pathlib import Path

from shortlist_contract import ShortlistIntegrationPending, integration_pending


def merge_jobs(*args, **kwargs):
    integration_pending("Legacy classified-job merge")


def finalize(*args, **kwargs):
    integration_pending("Classified-job finalization")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Retained CLI spelling; finalization is blocked")
    parser.parse_args()
    try:
        finalize()
    except ShortlistIntegrationPending as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    main()
