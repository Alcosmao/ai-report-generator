import json

from app.file_utils import create_txt_report, save_json, save_txt


class TestCreateTxtReport:
    def test_contains_all_sections(self, valid_report):
        text = create_txt_report(valid_report)
        assert "AI REPORT" in text
        assert "Summary:" in text
        assert "Issue:" in text
        assert "Actions taken:" in text
        assert "Next steps:" in text

    def test_includes_summary_and_issue_text(self, valid_report):
        text = create_txt_report(valid_report)
        assert valid_report["summary"] in text
        assert valid_report["issue"] in text

    def test_lists_actions_and_steps_as_bullets(self, valid_report):
        text = create_txt_report(valid_report)
        for action in valid_report["actions_taken"]:
            assert f"- {action}" in text
        for step in valid_report["next_steps"]:
            assert f"- {step}" in text

    def test_handles_empty_lists(self, valid_report):
        valid_report["actions_taken"] = []
        valid_report["next_steps"] = []
        text = create_txt_report(valid_report)
        assert "Actions taken:" in text
        assert "Next steps:" in text


class TestSaveFiles:
    def test_save_json_writes_valid_json(self, tmp_path, valid_report):
        target = tmp_path / "report.json"
        save_json(valid_report, target)
        assert target.exists()
        loaded = json.loads(target.read_text(encoding="utf-8"))
        assert loaded == valid_report

    def test_save_txt_writes_text(self, tmp_path):
        target = tmp_path / "report.txt"
        save_txt("hello report", target)
        assert target.read_text(encoding="utf-8") == "hello report"
