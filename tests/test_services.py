import json

from app.services import parse_ai_output, validate_report


class TestParseAiOutput:
    def test_parses_valid_json(self, valid_report_json, valid_report):
        result = parse_ai_output(valid_report_json)
        assert result == valid_report

    def test_returns_none_on_invalid_json(self):
        assert parse_ai_output("not a json {") is None

    def test_returns_none_on_empty_string(self):
        assert parse_ai_output("") is None


class TestValidateReport:
    def test_valid_report_passes(self, valid_report):
        is_valid, missing, wrong_types = validate_report(valid_report)
        assert is_valid is True
        assert missing == []
        assert wrong_types == []

    def test_detects_missing_field(self, valid_report):
        del valid_report["issue"]
        is_valid, missing, wrong_types = validate_report(valid_report)
        assert is_valid is False
        assert "issue" in missing

    def test_detects_multiple_missing_fields(self):
        is_valid, missing, wrong_types = validate_report({})
        assert is_valid is False
        assert set(missing) == {"summary", "issue", "actions_taken", "next_steps"}

    def test_detects_wrong_type_for_string_field(self, valid_report):
        valid_report["summary"] = 123
        is_valid, missing, wrong_types = validate_report(valid_report)
        assert is_valid is False
        assert "summary" in wrong_types

    def test_detects_wrong_type_for_list_field(self, valid_report):
        valid_report["actions_taken"] = "not a list"
        is_valid, missing, wrong_types = validate_report(valid_report)
        assert is_valid is False
        assert "actions_taken" in wrong_types

    def test_detects_non_string_items_in_actions_taken(self, valid_report):
        valid_report["actions_taken"] = ["ok", 5]
        is_valid, missing, wrong_types = validate_report(valid_report)
        assert is_valid is False
        assert wrong_types == ["actions_taken must contain only strings"]

    def test_detects_non_string_items_in_next_steps(self, valid_report):
        valid_report["next_steps"] = [None]
        is_valid, missing, wrong_types = validate_report(valid_report)
        assert is_valid is False
        assert wrong_types == ["next_steps must contain only strings"]

    def test_accepts_empty_lists(self, valid_report):
        valid_report["actions_taken"] = []
        valid_report["next_steps"] = []
        is_valid, _, _ = validate_report(valid_report)
        assert is_valid is True
