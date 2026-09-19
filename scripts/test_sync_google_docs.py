"""Offline sync regression tests; no OAuth or Drive calls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from sync_google_docs import SyncError, fetch_markdown, load_source, normalize, save_snapshot


class SyncTests(unittest.TestCase):
    def test_first_unchanged_then_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            output, state_path = root / "snapshot.md", root / "state.json"
            source = {"logical_name": "example", "drive_id": "test-id", "title": "Example", "type": "google_doc"}
            state = {"schema_version": 1, "sources": {"other": {"latest_content_hash": "untouched"}}}
            body = "# Heading\r\n\r\n- Bullet\r\n1. Numbered\r\n\r\n| A | B |\r\n| --- | --- |\r\n| 1 | 2 |\r\n"
            first_hash, status = save_snapshot(source, output, state_path, state, body, "2026-01-01T00:00:00Z")
            self.assertEqual(status, "changed")
            before, mtime = output.read_bytes(), output.stat().st_mtime_ns
            same_hash, status = save_snapshot(source, output, state_path, state, normalize(body), "2026-01-02T00:00:00Z")
            self.assertEqual((same_hash, status), (first_hash, "unchanged"))
            self.assertEqual((output.read_bytes(), output.stat().st_mtime_ns), (before, mtime))
            self.assertEqual(state["sources"]["example"]["last_successful_sync_at"], "2026-01-02T00:00:00Z")
            next_hash, status = save_snapshot(source, output, state_path, state, body + "New paragraph\n", "2026-01-03T00:00:00Z")
            self.assertEqual(status, "changed")
            self.assertNotEqual(first_hash, next_hash)
            self.assertIn("| 1 | 2 |", output.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(state_path.read_text())["sources"]["other"], {"latest_content_hash": "untouched"})

    def test_export_uses_only_selected_id_and_markdown(self):
        session = Mock()
        session.get.side_effect = [
            Mock(status_code=200, json=lambda: {"mimeType": "application/vnd.google-apps.document", "trashed": False}),
            Mock(status_code=200, content=b"# Heading\r\n- Item\r\n"),
        ]
        self.assertEqual(fetch_markdown(session, {"drive_id": "selected"}), "# Heading\n- Item\n")
        self.assertEqual(session.get.call_count, 2)
        self.assertTrue(all("/selected" in call.args[0] for call in session.get.call_args_list))
        self.assertEqual(session.get.call_args.kwargs["params"], {"mimeType": "text/markdown"})

    def test_api_failure_does_not_echo_response_body(self):
        session = Mock()
        session.get.return_value = Mock(status_code=403, text="sensitive response")
        with self.assertRaises(SyncError) as error:
            fetch_markdown(session, {"drive_id": "selected"})
        self.assertNotIn("sensitive", str(error.exception))
        self.assertEqual(session.get.call_count, 1)

    def test_registry_rejects_output_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sources").mkdir()
            (root / "sources/source_registry.yaml").write_text(
                "sources:\n  - logical_name: example\n    drive_id: test\n    title: Example\n"
                "    type: google_doc\n    output: profile/career_evidence.md\n", encoding="utf-8")
            with self.assertRaises(SyncError):
                load_source(root, "example")


if __name__ == "__main__":
    unittest.main()
