import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from common import extract_html, save_report
from agents import SPECIALISTS
from run_emergency import audit_workflow, collect_result, load_inputs, print_progress


DOCUMENT = (
    '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
    '<title>Emergency plan</title><style>body{color:#222}</style></head>'
    '<body><h1>Flood exercise</h1><p>Demo only.</p></body></html>'
)


class ReportTests(unittest.TestCase):
    def test_extracts_complete_document_from_fence(self) -> None:
        self.assertEqual(extract_html(f"```html\n{DOCUMENT}\n```"), DOCUMENT + "\n")

    def test_rejects_truncation_and_missing_structure(self) -> None:
        for text in [DOCUMENT[:-7], "<html><body>Hi</body></html>", DOCUMENT.replace("<style>", "<div>")]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                extract_html(text)

    def test_rejects_active_content(self) -> None:
        for content in [
            '<script>alert(1)</script>', '<img src="x" onerror="alert(1)">',
            '<a href="javascript:alert(1)">Click</a>', '<iframe src="x"/>',
            '<meta http-equiv="refresh" content="0;url=https://example.com">',
        ]:
            with self.subTest(content=content), self.assertRaises(ValueError):
                extract_html(DOCUMENT.replace("</body>", content + "</body>"))

    def test_preserves_previous_report_on_failure_and_keeps_transcript(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            report = save_report(DOCUMENT, output)
            with self.assertRaises(ValueError):
                save_report("incomplete response", output)
            self.assertEqual(report.read_text(encoding="utf-8"), DOCUMENT + "\n")
            self.assertEqual(
                (output / "coordinator-transcript.txt").read_text(encoding="utf-8"),
                "incomplete response",
            )


class WorkflowTests(unittest.TestCase):
    def valid_events(self) -> list[dict]:
        events = []
        for spec in SPECIALISTS.values():
            events.extend([
                {"type": "agent.thread_message_sent", "to_agent_name": spec["name"]},
                {"type": "agent.thread_message_received", "from_agent_name": spec["name"]},
            ])
        return events

    def test_accepts_research_first_complete_team(self) -> None:
        self.assertTrue(audit_workflow(self.valid_events())["research_first"])

    def test_rejects_early_specialist_dispatch(self) -> None:
        events = self.valid_events()
        events[1], events[2] = events[2], events[1]
        with self.assertRaisesRegex(ValueError, "before researcher"):
            audit_workflow(events)

    def test_rejects_missing_reply(self) -> None:
        with self.assertRaisesRegex(ValueError, "Incomplete team"):
            audit_workflow(self.valid_events()[:-1])

    def test_progress_distinguishes_coordinator_from_medical_wait(self) -> None:
        output = StringIO()
        replied: set[str] = set()
        with redirect_stdout(output):
            for spec in SPECIALISTS.values():
                print_progress(SimpleNamespace(type="agent.thread_message_received", from_agent_name=spec["name"]), replied)
            print_progress(SimpleNamespace(type="agent.thinking"), replied)
        self.assertIn("All specialists replied; composing the final HTML", output.getvalue())
        self.assertIn("Final report reasoning/generation is still active", output.getvalue())

    def test_progress_does_not_claim_complete_before_last_reply(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            print_progress(SimpleNamespace(type="agent.thread_message_received", from_agent_name="Emergency Researcher"), set())
        self.assertNotIn("composing", output.getvalue())

    def test_demo_input_and_research_match(self) -> None:
        import json
        from common import BASE_DIR

        scenario = load_inputs(BASE_DIR / "synthetic-data" / "household-flood.json")
        research = json.loads((BASE_DIR / "skills" / "emergency-research" / "bulletins.json").read_text(encoding="utf-8"))
        self.assertEqual(scenario["incident_id"], research["incident_id"])
        self.assertTrue(research["exercise_only"])
        self.assertTrue(all(source["fictional"] for source in research["sources"]))

    def test_collection_saves_client_html_not_specialist_messages(self) -> None:
        events = self.valid_events() + [{
            "type": "agent.message", "content": [{"type": "text", "text": DOCUMENT}],
        }]
        client = Mock()
        client.beta.sessions.events.list.return_value = [
            Mock(model_dump=Mock(return_value=event)) for event in events
        ]
        client.beta.sessions.retrieve.return_value = SimpleNamespace(model_dump_json=lambda **kwargs: "{}")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch("run_emergency.OUTPUT_DIR", output), patch(
                "run_emergency.save_report", side_effect=lambda text: save_report(text, output)
            ):
                result = collect_result(client, "sesn_demo")
            self.assertEqual(result.read_text(encoding="utf-8"), DOCUMENT + "\n")
            self.assertTrue((output / "workflow-audit.json").exists())
            self.assertTrue((output / "specialist-findings.json").exists())
            client.beta.sessions.events.list.assert_called_once_with("sesn_demo", order="asc")


if __name__ == "__main__":
    unittest.main()