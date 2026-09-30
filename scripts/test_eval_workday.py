import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import eval_workday
from discovery.errors import CrawlError
from discovery.workday import fetch_workday_jobs
from test_workday import SOURCE, Session


class WorkdayEvaluationTests(unittest.TestCase):
    def test_combined_csv_maps_requisition_ids_and_selects_company(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'frozen.csv'
            path.write_text('company,job_id,title,locations,canonical_job_url,benchmark_status\n'
                            'Example,REQ1,Product Manager,US,https://example.com/1,FROZEN\n'
                            'Other,REQ2,Product Lead,India,https://example.com/2,FROZEN\n', encoding='utf-8-sig')
            before = path.read_bytes()
            rows = eval_workday.load_reference(path, 'Example')
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['external_job_id'], 'REQ1')
            self.assertEqual(rows[0]['location'], 'US')
            self.assertEqual(rows[0]['canonical_url'], 'https://example.com/1')
            self.assertEqual(path.read_bytes(), before)
            with path.open('a', encoding='utf-8') as stream:
                stream.write('Example,REQ1,Other title,India,https://example.com/3,FROZEN\n')
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                eval_workday.load_reference(path, 'Example')

    def test_saved_crawl_validation(self):
        jobs, telemetry = fetch_workday_jobs('example', SOURCE, Session())
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            eval_workday.atomic_jsonl(path / 'raw_all_jobs.jsonl', jobs)
            (path / 'crawl.json').write_text(json.dumps(telemetry))
            loaded, _ = eval_workday.load_saved_crawl(path, 'example', SOURCE['company'])
            self.assertEqual(loaded, jobs)
            with self.assertRaises(ValueError):
                eval_workday.load_saved_crawl(path, 'other', SOURCE['company'])
            telemetry['pagination_complete'] = False
            (path / 'crawl.json').write_text(json.dumps(telemetry))
            with self.assertRaises(ValueError):
                eval_workday.load_saved_crawl(path, 'example', SOURCE['company'])

    def invoke(self, reference_count=2, failure=False):
        jobs,telemetry=fetch_workday_jobs('example',SOURCE,Session())
        events=[]
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); reference=root/'reference.jsonl'; output=root/'output'
            refs=[dict(company='Example',external_job_id=i,title='Reference title',location='') for i in ('1','2')]
            reference.write_text(''.join(json.dumps(r)+'\n' for r in refs))
            before=reference.read_bytes()
            original=eval_workday.load_reference
            def crawl(*args):
                events.append('crawl')
                if failure: raise CrawlError(dict(telemetry,errors=['test failure']))
                return jobs,telemetry
            def load(*args):
                events.append('reference')
                return original(*args)
            argv=['eval_workday','--source','example','--reference',str(reference),
                  '--expected-count',str(reference_count),'--output-dir',str(output)]
            with patch('sys.argv',argv),patch('builtins.print'),patch.object(eval_workday,'load_job_sources',return_value={'example':dict(SOURCE,adapter='workday')}),patch.object(eval_workday,'fetch_workday_jobs',side_effect=crawl),patch.object(eval_workday,'load_reference',side_effect=load):
                if reference_count!=2:
                    with self.assertRaises(ValueError): eval_workday.main()
                else: eval_workday.main()
            self.assertEqual(before,reference.read_bytes())
            return json.loads((output/'summary.json').read_text()),events

    def test_independent_reference_raw_vs_filtered_recall_and_extras(self):
        result,events=self.invoke()
        self.assertEqual(events,['crawl','reference'])
        self.assertEqual(result['raw_benchmark_matches'],2)
        self.assertEqual(result['benchmark_matches'],1)
        self.assertEqual(result['extra_pm_candidates'],1)
        self.assertEqual(result['missing_benchmark_ids'],['2'])

    def test_crawl_failure_does_not_read_reference_or_report_stale_recall(self):
        result,events=self.invoke(failure=True)
        self.assertEqual(events,['crawl'])
        self.assertEqual(result['status'],'failed')
        self.assertIsNone(result['benchmark_recall'])

    def test_wrong_reference_count_is_not_scored(self):
        result,_=self.invoke(reference_count=99)
        self.assertEqual(result['status'],'evaluation_failed')
        self.assertIsNone(result['benchmark_recall'])


if __name__=='__main__': unittest.main()
