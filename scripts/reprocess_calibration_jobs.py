"""Retired calibration reprocessor. Reads history; never regenerates decisions."""
import argparse
from pathlib import Path

import yaml

from job_framework import ROOT
from shortlist_contract import ShortlistIntegrationPending, integration_pending


def annotations(root=ROOT):
    """Read historical annotations unchanged; not validated against a live rubric."""
    return yaml.safe_load((Path(root) / "data/calibration_annotations.yaml").read_text(encoding="utf-8"))


def migrate_job(*args, **kwargs):
    integration_pending("Legacy calibration decision conversion")


def reprocess(*args, **kwargs):
    integration_pending("Legacy calibration reprocessing")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-sheet", action="store_true", help="Retained CLI spelling; reprocessing is blocked")
    parser.parse_args()
    try:
        reprocess()
    except ShortlistIntegrationPending as exc:
        parser.exit(2, f"{exc}\n")


if __name__ == "__main__":
    main()
