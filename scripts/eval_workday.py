"""Workday evaluation; reference data enters only after discovery and PM filtering."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from discovery.errors import CrawlError
from discovery.io import atomic_jsonl, load_job_sources, write_csv
from discovery.models import validate_raw_jobs, utc_now_iso
from discovery.workday import fetch_workday_jobs
from discover_jobs import retain_candidate
from eval_discovery import evaluate, load_jsonl

ROOT = Path(__file__).resolve().parents[1]


def load_reference(path, company, sheet=None):
    if path.suffix.lower() == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            required = {'company', 'job_id', 'title', 'locations', 'canonical_job_url'}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError('CSV reference is missing required columns')
            rows = list(reader)
        if any(not (r.get('company') or '').strip() or not (r.get('job_id') or '').strip() for r in rows):
            raise ValueError('CSV reference requires company and requisition ID on every row')
        keys = [(r['company'], r['job_id']) for r in rows]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate identities in CSV reference')
        # Combined frozen references are partitioned only inside this evaluator.
        return [dict(r, external_job_id=r['job_id'], location=r['locations'],
                     canonical_url=r['canonical_job_url']) for r in rows if r['company'] == company]
    elif path.suffix.lower() == '.xlsx':
        import openpyxl
        if not sheet:
            raise ValueError('A reviewed worksheet name is required for XLSX references')
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            values = iter(workbook[sheet].values)
            header = next(values)
            rows = [dict(zip(header, row)) for row in values if any(v is not None for v in row)]
        finally:
            workbook.close()
    else:
        rows = load_jsonl(path)
    if any(row.get('company', company) != company for row in rows):
        raise ValueError('Reference contains a different company')
    return [dict(row, company=company, location=row.get('location', row.get('primary_location', ''))) for row in rows]


def load_saved_crawl(directory, source_key, company):
    telemetry = json.loads((directory / 'crawl.json').read_text(encoding='utf-8'))
    jobs = load_jsonl(directory / 'raw_all_jobs.jsonl')
    validate_raw_jobs(jobs)
    if (telemetry.get('status') != 'success' or telemetry.get('pagination_complete') is not True
            or telemetry.get('source_key') != source_key or telemetry.get('company') != company
            or telemetry.get('jobs_extracted') != len(jobs)
            or telemetry.get('source_failures') or telemetry.get('detail_failures')):
        raise ValueError('Saved crawl must be successful, complete, and match the configured source')
    if any(j['source_key'] != source_key or j['company'] != company or j['source_type'] != 'workday' for j in jobs):
        raise ValueError('Saved jobs contain a different source')
    return jobs, telemetry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--sheet')
    parser.add_argument('--expected-count', type=int, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--saved-crawl-dir', type=Path, help='Evaluate saved raw discovery without network access')
    args = parser.parse_args()
    source = load_job_sources(ROOT / 'config/job_sources.yaml')[args.source]
    if source['adapter'] != 'workday':
        raise ValueError('Expected a Workday source')
    output = args.output_dir
    if args.saved_crawl_dir and output.resolve() == args.saved_crawl_dir.resolve():
        raise ValueError('Saved-crawl evaluation requires a separate output directory')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'summary.json').write_text(json.dumps(dict(status='running', company=source['company'])), encoding='utf-8')
    try:
        if args.saved_crawl_dir:
            jobs, telemetry = load_saved_crawl(args.saved_crawl_dir, args.source, source['company'])
        else:
            jobs, telemetry = fetch_workday_jobs(args.source, source)
    except CrawlError as exc:
        (output / 'crawl.json').write_text(json.dumps(exc.telemetry, indent=2), encoding='utf-8')
        (output / 'summary.json').write_text(json.dumps(dict(status='failed', company=source['company'],
            errors=exc.telemetry['errors'], benchmark_recall=None)), encoding='utf-8')
        print(json.dumps(exc.telemetry), flush=True)
        return 1
    candidates = [j for j in jobs if retain_candidate(j)]
    telemetry['pm_candidates'] = len(candidates)
    (output / 'crawl.json').write_text(json.dumps(telemetry, indent=2), encoding='utf-8')
    atomic_jsonl(output / 'raw_all_jobs.jsonl', jobs)
    atomic_jsonl(output / 'raw_pm_candidates.jsonl', candidates)
    # Deliberate separation: neither the adapter nor the title filter sees these rows.
    try:
        before = hashlib.sha256(args.reference.read_bytes()).hexdigest()
        reference = load_reference(args.reference, source['company'], args.sheet)
        if len(reference) != args.expected_count:
            raise ValueError(f'Reference count {len(reference)} does not match expected {args.expected_count}')
        result = evaluate(reference, candidates)
        raw_result = evaluate(reference, jobs)
    except (OSError, ValueError, KeyError) as exc:
        (output / 'summary.json').write_text(json.dumps(dict(status='evaluation_failed',
            company=source['company'], raw_jobs=len(jobs), pm_candidates=len(candidates),
            errors=[str(exc)], benchmark_recall=None)), encoding='utf-8')
        raise
    raw_ids = {j['external_job_id'] for j in jobs}
    missing = [dict(r, failure_category='title_filter' if r['external_job_id'] in raw_ids else 'raw_retrieval_or_source_drift') for r in result['missed']]
    summary = dict(status='success', company=source['company'], raw_jobs=len(jobs), pm_candidates=len(candidates),
                   benchmark_count=len(reference), benchmark_matches=result['found_count'],
                   benchmark_recall=result['known_positive_recall'], raw_benchmark_matches=raw_result['found_count'],
                   extra_pm_candidates=result['extra_count'], missing_benchmark_ids=[r['external_job_id'] for r in missing],
                   duplicate_job_ids=telemetry['duplicate_job_ids'], duplicate_listing_paths=telemetry['duplicate_listing_paths'],
                   pagination_complete=telemetry['pagination_complete'], source_failures=telemetry['source_failures'],
                   detail_failures=telemetry['detail_failures'], reference_path=str(args.reference.resolve()),
                   reference_sheet=args.sheet, reference_sha256=before, crawl_started_at=telemetry['started_at'],
                   crawl_completed_at=telemetry['completed_at'], extras_are_unreviewed=True)
    summary.update(evaluated_at=utc_now_iso(), evaluation_mode='saved_crawl' if args.saved_crawl_dir else 'live',
                   saved_crawl_dir=str(args.saved_crawl_dir.resolve()) if args.saved_crawl_dir else None)
    assert hashlib.sha256(args.reference.read_bytes()).hexdigest() == before
    atomic_jsonl(output / 'missing_benchmark_jobs.jsonl', missing)
    atomic_jsonl(output / 'extra_pm_candidates.jsonl', result['extras'])
    write_csv(output / 'extra_pm_candidates.csv', result['extras'], ['company','external_job_id','title','location','canonical_url'])
    (output / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
