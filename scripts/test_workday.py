import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

from discovery.errors import CrawlError
from discovery.workday import fetch_workday_jobs
from discover_jobs import run, retain_candidate

SOURCE = dict(company='Example', tenant='example', site='Careers',
              careers_url='https://example.wd5.myworkdayjobs.com/Careers', page_size=2)


def listing(i):
    return dict(title='Product Manager', externalPath=f'/job/Remote/Role_{i}', bulletFields=[str(i)])


class Session:
    def __init__(self, ids=(1, 2, 3), count=True, reset=True):
        self.ids, self.count, self.reset = list(ids), count, reset
        self.posts, self.gets = [], []
        self.transform = lambda payload, body: payload
        self.detail_transform = lambda payload: payload

    def post(self, url, json, timeout):
        self.posts.append((url, copy.deepcopy(json)))
        offset, limit = json['offset'], json['limit']
        selected = self.ids[offset:offset + limit]
        if offset >= len(self.ids) and self.reset:
            selected = self.ids[:limit]
        payload = dict(jobPostings=[listing(i) for i in selected])
        if self.count:
            payload['total'] = len(self.ids) if offset == 0 else 0
        response = Mock(status_code=200)
        response.json.return_value = self.transform(payload, json)
        return response

    def get(self, url, timeout):
        self.gets.append(url)
        i = url.rsplit('_', 1)[1]
        payload = dict(jobPostingInfo=dict(jobReqId=i, title='Product Manager' if i != '2' else 'Engineer',
            location='US, Remote', additionalLocations=['India, Pune', 'US, Remote'],
            externalUrl=f'https://example.wd5.myworkdayjobs.com/Careers/job/Remote/Role_{i}?utm_source=test',
            jobDescription='<p>Build <b>products</b> &amp; platforms.</p><p>Full requirements.</p>', startDate='2026-09-01'))
        response = Mock(status_code=200)
        response.json.return_value = self.detail_transform(payload)
        return response


class WorkdayTests(unittest.TestCase):
    def test_counted_two_pass_reset_and_full_description(self):
        session = Session()
        jobs, t = fetch_workday_jobs('example', SOURCE, session)
        self.assertEqual([j['external_job_id'] for j in jobs], ['1', '2', '3'])
        self.assertEqual([p[1]['offset'] for p in session.posts], [0, 2, 3, 0, 2, 3])
        self.assertEqual(t['passes'][0]['stop_reason'], 'count_and_repeated_probe')
        self.assertTrue(t['pagination_complete'])
        self.assertEqual(t['request_count'], 9)
        self.assertEqual(json.loads(jobs[0]['all_locations']), ['US, Remote', 'India, Pune'])
        self.assertEqual(jobs[0]['primary_location'], 'US, Remote')
        self.assertIn('<b>products</b>', jobs[0]['full_job_description_raw'])
        self.assertIn('Full requirements.', jobs[0]['description'])
        self.assertEqual(jobs[0]['posting_date'], '2026-09-01')
        self.assertEqual(jobs[0]['job_id'], 'example:1')
        self.assertNotIn('utm_', jobs[0]['canonical_url'])
        self.assertEqual(len([j for j in jobs if retain_candidate(j)]), 2)

    def test_empty_board(self):
        jobs, t = fetch_workday_jobs('example', SOURCE, Session(ids=[]))
        self.assertEqual(jobs, [])
        self.assertTrue(t['pagination_complete'])

    def test_unknown_count_requires_empty_page(self):
        jobs, t = fetch_workday_jobs('example', SOURCE, Session(count=False, reset=False))
        self.assertEqual(len(jobs), 3)
        self.assertIsNone(t['source_count'])
        with self.assertRaises(CrawlError):
            fetch_workday_jobs('example', SOURCE, Session(count=False))

    def test_repeat_before_count_fails_without_details(self):
        session = Session()
        session.transform = lambda p,b: dict(total=3 if b['offset']==0 else 0, jobPostings=[listing(1), listing(2)])
        with self.assertRaises(CrawlError) as caught:
            fetch_workday_jobs('example', SOURCE, session)
        self.assertFalse(caught.exception.telemetry['pagination_complete'])
        self.assertEqual(caught.exception.telemetry['duplicate_listing_paths'], 2)
        self.assertEqual(session.gets, [])

    def test_count_drift_and_new_terminal_records_fail(self):
        for change in [lambda p,b: dict(p,total=4) if b['offset'] else p,
                       lambda p,b: dict(p,jobPostings=[listing(99)]) if b['offset']==3 else p]:
            session = Session(); session.transform = change
            with self.assertRaises(CrawlError):
                fetch_workday_jobs('example', SOURCE, session)

    def test_second_pass_must_match_ids(self):
        session = Session()
        def change(p,b):
            if len(session.posts)>3:
                p['jobPostings']=[listing(4) if j['externalPath'].endswith('_3') else j for j in p['jobPostings']]
            return p
        session.transform = change
        with self.assertRaisesRegex(CrawlError,'passes disagree'):
            fetch_workday_jobs('example', SOURCE, session)

    def test_malformed_or_capped_search_fails(self):
        for p in [{}, {'jobPostings':{}}, {'jobPostings':[], 'total':2000}, {'jobPostings':[listing(1)],'total':0}]:
            session=Session(); session.transform=lambda x,b: p
            with self.subTest(p=p), self.assertRaises(CrawlError):
                fetch_workday_jobs('example', SOURCE, session)

    def test_detail_failure_collects_and_withholds_output(self):
        session=Session(); session.detail_transform=lambda p: {} if p['jobPostingInfo']['jobReqId']=='2' else p
        with self.assertRaises(CrawlError) as caught:
            fetch_workday_jobs('example', SOURCE, session)
        self.assertEqual(len(session.gets),3)
        self.assertEqual(len(caught.exception.telemetry['detail_failures']),1)
        self.assertEqual(caught.exception.telemetry['jobs_extracted'],2)

    def test_missing_description_and_offsite_canonical_fail(self):
        for changes in [dict(jobDescription=''),dict(externalUrl='https://example.com/job/1')]:
            session=Session(ids=[1])
            session.detail_transform=lambda p: dict(jobPostingInfo=dict(p['jobPostingInfo'],**changes))
            with self.subTest(changes=changes),self.assertRaises(CrawlError):
                fetch_workday_jobs('example',SOURCE,session)

    def test_malformed_listing_is_audited_and_valid_neighbors_survive(self):
        for field in ('title', 'externalPath'):
            with self.subTest(field=field):
                session = Session()
                def change(payload, body):
                    for item in payload['jobPostings']:
                        if item['bulletFields'] == ['2']:
                            item.pop(field)
                    return payload
                session.transform = change
                jobs, t = fetch_workday_jobs('example', SOURCE, session)
                self.assertEqual([j['external_job_id'] for j in jobs], ['1', '3'])
                self.assertEqual(len(session.gets), 2)
                self.assertEqual([p[1]['offset'] for p in session.posts], [0, 2, 3, 0, 2, 3])
                self.assertEqual(t['malformed_records_skipped'], 1)
                diagnostic = t['malformed_records'][0]
                self.assertEqual(diagnostic['failure_reason'], 'malformed_source_record')
                self.assertEqual(diagnostic['raw_record']['bulletFields'], ['2'])
                self.assertTrue(any(field in reason for reason in diagnostic['reasons']))
                self.assertEqual({o['pass_number'] for o in diagnostic['observations']}, {1, 2})
                self.assertTrue(t['pagination_complete'])
                self.assertFalse(t['extraction_complete'])
                self.assertEqual(t['source_count'], 3)
                self.assertEqual(t['detail_failures'], [])
                self.assertEqual(t['status'], 'success')

    def test_missing_both_fields_blank_title_and_nonobject_are_skipped(self):
        for malformed in ({'bulletFields': ['2']}, dict(listing(2), title='  '), None):
            with self.subTest(malformed=malformed):
                session = Session()
                session.transform = lambda p,b: dict(p,jobPostings=[malformed if j['bulletFields']==['2'] else j for j in p['jobPostings']])
                jobs,t = fetch_workday_jobs('example', SOURCE, session)
                self.assertEqual([j['external_job_id'] for j in jobs], ['1','3'])
                self.assertEqual(t['malformed_records_skipped'], 1)

    def test_required_detail_identity_or_title_is_audited_not_invented(self):
        for field in ('jobReqId', 'title'):
            with self.subTest(field=field):
                session = Session()
                def change(payload):
                    if payload['jobPostingInfo']['jobReqId']=='2':
                        payload['jobPostingInfo'].pop(field)
                    return payload
                session.detail_transform = change
                jobs,t = fetch_workday_jobs('example',SOURCE,session)
                self.assertEqual([j['external_job_id'] for j in jobs], ['1','3'])
                self.assertEqual(len(session.gets), 3)
                self.assertEqual(t['malformed_records_skipped'], 1)
                self.assertEqual(t['malformed_records'][0]['failure_reason'], 'malformed_source_record')
                self.assertIn('detail', t['malformed_records'][0]['raw_record'])

    def test_malformed_records_do_not_mask_count_shortfall_or_pass_drift(self):
        session=Session(ids=[1,2,2])
        session.transform=lambda p,b: dict(p,jobPostings=[{'bulletFields':['2']} if j['bulletFields']==['2'] else j for j in p['jobPostings']])
        with self.assertRaises(CrawlError):
            fetch_workday_jobs('example',SOURCE,session)
        session=Session()
        def change(payload,body):
            if len(session.posts)<=3:
                for item in payload['jobPostings']:
                    if item['bulletFields']==['2']: item.pop('title')
            return payload
        session.transform=change
        with self.assertRaisesRegex(CrawlError,'passes disagree'):
            fetch_workday_jobs('example',SOURCE,session)

    def test_conflicting_requisition_ids_fail(self):
        session=Session()
        session.detail_transform=lambda p: dict(jobPostingInfo=dict(p['jobPostingInfo'],jobReqId='same'))
        with self.assertRaises(CrawlError) as caught:
            fetch_workday_jobs('example',SOURCE,session)
        self.assertEqual(caught.exception.telemetry['duplicate_job_ids'],2)

    def test_duplicate_requisition_aliases_are_returned_once(self):
        session=Session(ids=[1,3])
        session.detail_transform=lambda p: dict(jobPostingInfo=dict(p['jobPostingInfo'],jobReqId='same',
            externalUrl='https://example.wd5.myworkdayjobs.com/Careers/job/Remote/Canonical_same'))
        jobs,t=fetch_workday_jobs('example',SOURCE,session)
        self.assertEqual(len(jobs),1)
        self.assertEqual(t['duplicate_job_ids'],1)

    def test_detail_posting_identity_mismatch(self):
        session=Session(ids=[1])
        session.detail_transform=lambda p: dict(jobPostingInfo=dict(p['jobPostingInfo'],jobPostingId='Different_99'))
        with self.assertRaises(CrawlError) as caught:
            fetch_workday_jobs('example',SOURCE,session)
        self.assertIn('identity mismatch',caught.exception.telemetry['detail_failures'][0]['error'])

    def test_max_pages_guard_and_source_configuration_validation(self):
        with self.assertRaisesRegex(CrawlError,'max_pages'):
            fetch_workday_jobs('example',dict(SOURCE,max_pages=1),Session())
        for changes in [dict(tenant='../wrong'),dict(site='Wrong'),dict(page_size=100),
                        dict(applied_facets={'family':'not-a-list'}),dict(careers_url='https://other.example/Careers')]:
            with self.subTest(changes=changes),self.assertRaises(CrawlError):
                fetch_workday_jobs('example',dict(SOURCE,**changes),Session())

    def test_transient_http_retry_exhaustion(self):
        response=Mock(status_code=503)
        response.raise_for_status.side_effect=requests.HTTPError('unavailable',response=response)
        with patch('discovery.workday.time.sleep'), self.assertRaises(CrawlError) as caught:
            fetch_workday_jobs('example',SOURCE,Mock(post=Mock(return_value=response)))
        self.assertEqual(caught.exception.telemetry['request_count'],3)
        self.assertEqual(caught.exception.telemetry['retries'],2)

    def test_source_filters_forwarded_and_dates_not_estimated(self):
        session=Session(ids=[1])
        session.detail_transform=lambda p: dict(jobPostingInfo={k:v for k,v in p['jobPostingInfo'].items() if k not in ('startDate','externalUrl')})
        jobs,_=fetch_workday_jobs('example',dict(SOURCE,search_text='arbitrary',applied_facets={'family':['x']}),session)
        self.assertEqual(session.posts[0][1]['appliedFacets'],{'family':['x']})
        self.assertEqual(session.posts[0][1]['searchText'],'arbitrary')
        self.assertEqual(jobs[0]['posting_date'],'')
        self.assertTrue(jobs[0]['canonical_url'].endswith('/job/Remote/Role_1'))

    def test_retry_timeout_and_permanent_http_error(self):
        session=Session(ids=[1]); original=session.post
        session.post=Mock(side_effect=[requests.Timeout('slow'),original('',dict(offset=0,limit=2),45)])
        # Other requests continue through the original mock implementation.
        responses=iter(session.post.side_effect)
        def post(*a,**kw):
            try: result=next(responses)
            except StopIteration: return original(*a,**kw)
            if isinstance(result,Exception): raise result
            return result
        session.post=post
        with patch('discovery.workday.time.sleep'):
            _,t=fetch_workday_jobs('example',SOURCE,session)
        self.assertEqual(t['retries'],1)
        response=Mock(status_code=404)
        response.raise_for_status.side_effect=requests.HTTPError('missing',response=response)
        with self.assertRaises(CrawlError) as caught:
            fetch_workday_jobs('example',SOURCE,Mock(post=Mock(return_value=response)))
        self.assertEqual(caught.exception.telemetry['request_count'],1)

    def test_run_dispatch_preserves_previous_snapshot_on_failure(self):
        jobs,t=fetch_workday_jobs('example',SOURCE,Session())
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'config').mkdir()
            (root/'config/job_sources.yaml').write_text('sources:\n  example:\n    company: Example\n    adapter: workday\n')
            with patch('discover_jobs.fetch_workday_jobs',return_value=(jobs,t)):
                self.assertFalse(run(['example'],root)['failures'])
            path=root/'data/discovery/raw_all_jobs.jsonl'; before=path.read_bytes()
            with patch('discover_jobs.fetch_workday_jobs',side_effect=CrawlError(dict(t,errors=['failure']))):
                self.assertTrue(run(['example'],root)['failures'])
            self.assertEqual(before,path.read_bytes())


if __name__=='__main__': unittest.main()
