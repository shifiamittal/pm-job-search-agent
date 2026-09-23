import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from discovery.source_detection import detect_source, extract_links, url_signal
from detect_sources import compare_identifier, evaluate_row, run, summarize


def document(url, body="", status=200, final=None):
    return dict(url=url, final_url=final or url, html=body, status=status, redirects=[])


class SourceDetectionTests(unittest.TestCase):
    def test_provider_urls_and_reusable_identifiers(self):
        cases = [
            ("https://job-boards.greenhouse.io/example/jobs/123", ("greenhouse", "example")),
            ("https://boards.greenhouse.io/embed/job_board?for=sample", ("greenhouse", "sample")),
            ("https://boards-api.greenhouse.io/v1/boards/sample/jobs", ("greenhouse", "sample")),
            ("https://jobs.ashbyhq.com/sample/uuid", ("ashby", "sample")),
            ("https://acme.wd5.myworkdayjobs.com/en-US/External/job/City/Role_123", ("workday", "acme/External")),
            ("https://acme.wd5.myworkdayjobs.com/wday/cxs/acme/External/jobs", ("workday", "acme/External")),
            ("https://jobs.lever.co/sample/uuid", ("lever", "sample")),
            ("https://ats.rippling.com/en-US/sample/jobs/uuid", ("rippling", "sample")),
            ("https://apply.careers.microsoft.com/api/pcsx/search?domain=microsoft.com", ("microsoft_custom", "microsoft.com")),
        ]
        for url, expected in cases:
            with self.subTest(url=url):
                self.assertEqual(url_signal(url), expected)
                result = detect_source("Unrelated display name", url, fetcher=lambda u: document(u))
                self.assertEqual(result["detected_source_type"], expected[0])
                self.assertEqual(result["confidence"], "high")

    def test_lookalike_domains_and_brand_name_not_evidence(self):
        for url in ["https://jobs.ashbyhq.com.evil.example/sample", "https://greenhouse.io/blog", "https://example.com/greenhouse/jobs"]:
            self.assertIsNone(url_signal(url))
        result = detect_source("Anthropic", "https://example.com", fetcher=lambda u: document(u, "Welcome Anthropic Greenhouse"))
        self.assertEqual(result["detected_source_type"], "unknown")

    def test_follow_job_link_and_embedded_provider(self):
        start = "https://example.com/careers"
        detail = "https://example.com/jobs/123"
        pages = {start: document(start, '<a href="/jobs/123">PM</a>'),
                 detail: document(detail, '<a href="https://jobs.ashbyhq.com/acme/uuid">Apply</a>')}
        fetch = Mock(side_effect=lambda url: pages[url])
        result = detect_source("Acme", start, fetcher=fetch)
        self.assertEqual(result["detected_source_type"], "ashby")
        self.assertEqual(result["detected_source_identifier"], "acme")
        self.assertTrue(result["adapter_available"])
        self.assertEqual(result["evidence"][0]["found_on"], detail)
        self.assertEqual(fetch.call_count, 2)

    def test_redirect_is_direct_evidence_even_when_provider_blocks(self):
        result = detect_source("Acme", "https://example.com/careers", fetcher=lambda u: document(u, status=403, final="https://jobs.lever.co/acme"))
        self.assertEqual(result["detected_source_type"], "lever")
        self.assertFalse(result["adapter_available"])

    def test_blocked_html_not_used_as_job_evidence(self):
        for code in [403, 406, 429, 500]:
            result = detect_source("Acme", "https://example.com/careers", fetcher=lambda u: document(u, '<a href="https://jobs.ashbyhq.com/acme">Try this</a>', code))
            self.assertEqual(result["detected_source_type"], "unknown")
            self.assertEqual(result["confidence"], "low")

    def test_company_native_fallback_requires_jobs_evidence(self):
        result = detect_source("Acme", "https://example.com/careers", max_documents=1,
                               fetcher=lambda u: document(u, '<a href="/jobs/123">PM</a><a href="/jobs/456">Engineer</a>'))
        self.assertEqual(result["detected_source_type"], "company_native_custom")
        self.assertEqual(result["confidence"], "medium")
        self.assertEqual(result["detected_source_identifier"], "")
        self.assertFalse(result["adapter_available"])

    def test_script_inspection_and_escaped_metadata(self):
        start = "https://example.com/careers"
        script = "https://example.com/careers.js"
        pages = {start: document(start, '<script src="/careers.js"></script>'),
                 script: document(script, r'const url="https:\/\/boards-api.greenhouse.io\/v1\/boards\/acme\/jobs";')}
        result = detect_source("Acme", start, fetcher=lambda u: pages[u])
        self.assertEqual(result["detected_source_identifier"], "acme")
        self.assertEqual(result["detection_method"], "script_url")

    def test_multiple_boards_not_invented_and_not_ready(self):
        result = detect_source("Acme", "https://example.com", fetcher=lambda u: document(u,
            '<a href="https://jobs.ashbyhq.com/one">One</a><a href="https://jobs.ashbyhq.com/two">Two</a>'))
        self.assertEqual(result["detected_source_type"], "ashby")
        self.assertEqual(result["detected_source_identifier"], "")
        self.assertTrue(result["adapter_available"])
        self.assertFalse(result["source_ready"])
        self.assertEqual(result["confidence"], "medium")

    def test_conflicting_providers_require_review(self):
        result = detect_source("Acme", "https://example.com", fetcher=lambda u: document(u,
            '<a href="https://jobs.ashbyhq.com/one">One</a><a href="https://jobs.lever.co/two">Two</a>'))
        self.assertEqual(result["detected_source_type"], "unknown")
        self.assertEqual(result["detection_method"], "conflicting_providers")

    def test_bounded_crawl_and_deduplicated_urls(self):
        fetch = Mock(side_effect=lambda u: document(u, '<a href="/jobs/123">A</a><a href="/jobs/123#x">B</a><a href="/jobs/456">C</a>'))
        result = detect_source("Acme", "https://example.com/careers", fetcher=fetch, max_documents=2)
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(result["inspected_documents"], 2)

    def test_html_base_relative_jobs_and_locale_query_deduplication(self):
        links = extract_links('<base href="/careers/"><a href="jobs/123">Role</a>', "https://example.com/careers/search/")
        self.assertIn(("https://example.com/careers/jobs/123", "link"), links)
        fetch = Mock(side_effect=lambda u: document(u, '<a href="/fr/careers/jobs?x=1">Locale</a><a href="/careers/jobs?x=2">Query</a>'))
        detect_source("Acme", "https://example.com/careers/jobs", fetcher=fetch)
        self.assertEqual(fetch.call_count, 1)

    def test_structured_provider_ids_do_not_invent_board_token(self):
        result = detect_source("Acme", "https://example.com/careers", fetcher=lambda u: document(u, '{"listings":[{"greenhouseId":123},{"greenhouseId":456}]}'))
        self.assertEqual(result["detected_source_type"], "greenhouse")
        self.assertEqual(result["confidence"], "medium")
        self.assertEqual(result["detected_source_identifier"], "")
        self.assertTrue(result["adapter_available"])
        self.assertFalse(result["source_ready"])

    def test_exposed_jobs_subdomain_followed_and_aggregator_not_followed(self):
        start = "https://example.com/careers"
        dest = "https://jobs.example.com/careers"
        fetch = Mock(side_effect=lambda u: document(u, '<a href="https://jobs.example.com/careers">Jobs</a><a href="https://www.linkedin.com/company/acme/jobs/">Social</a>' if u == start else '<a href="https://acme.wd5.myworkdayjobs.com/External">Apply</a>'))
        result = detect_source("Acme", start, fetcher=fetch)
        self.assertEqual(result["detected_source_type"], "workday")
        self.assertEqual([call.args[0] for call in fetch.call_args_list], [start, dest])

    def test_identifier_comparison_explicit_partial_workday(self):
        self.assertEqual(compare_identifier("acme", "acme/External", "workday"), "PARTIAL_COMPONENT_MATCH")
        self.assertEqual(compare_identifier("External", "acme/External", "workday"), "PARTIAL_COMPONENT_MATCH")
        self.assertEqual(compare_identifier("wrong", "acme", "ashby"), "MISMATCH")
        self.assertEqual(compare_identifier("acme", "", "ashby"), "NOT_COMPARABLE")

    def test_medium_benchmark_disagreement_separate_from_high_failure(self):
        detected = detect_source("Acme", "https://jobs.ashbyhq.com/acme", fetcher=lambda u: document(u))
        ref = dict(company="Acme", careers_url="https://example.com", source_type="Greenhouse", source_identifier="acme", confidence="Medium")
        result = evaluate_row(ref, detected)
        self.assertEqual(result["match_status"], "BENCHMARK_REVIEW")
        self.assertEqual(result["identifier_comparison"], "MISMATCH")
        summary = summarize([result])
        self.assertEqual(len(summary["proposed_benchmark_corrections"]), 1)
        self.assertEqual(summary["high_confidence_source_type_accuracy"]["denominator"], 0)
        self.assertEqual(evaluate_row(dict(ref, confidence="High"), detected)["match_status"], "TYPE_MISMATCH")

    def test_runner_does_not_pass_labels_to_detector_or_mutate_benchmark(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            benchmark = root / "reference.csv"
            benchmark.write_text("company,careers_url,source_type,source_identifier,confidence\nAcme,https://example.com,Greenhouse,secret-expected,High\n", encoding="utf-8")
            before = benchmark.read_bytes()
            result = detect_source("Acme", "https://example.com", fetcher=lambda u: document(u))
            detector = Mock(return_value=result)
            summary = run(benchmark, root / "out", detector=detector)
            detector.assert_called_once_with("Acme", "https://example.com")
            self.assertEqual(benchmark.read_bytes(), before)
            self.assertEqual(summary["benchmark_sha256"], hashlib.sha256(before).hexdigest())
            self.assertEqual(summary["unknown_rate"]["rate"], 1)
            self.assertEqual(summary["identifier_accuracy"]["denominator"], 0)
            with (root / "out/results.csv").open(newline="", encoding="utf-8") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 1)


if __name__ == "__main__":
    unittest.main()
