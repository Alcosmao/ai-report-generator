import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def stub_file_io(monkeypatch):
    """Prevent the API from touching the real filesystem during tests."""
    monkeypatch.setattr(main_module, "setup_folders", lambda: None)
    monkeypatch.setattr(main_module, "save_json", lambda *a, **k: None)
    monkeypatch.setattr(main_module, "save_txt", lambda *a, **k: None)


@pytest.fixture
def mock_openai_success(monkeypatch, valid_report_json):
    monkeypatch.setattr(main_module, "load_api_key", lambda: "test-key")
    monkeypatch.setattr(
        main_module,
        "call_openai_structured",
        lambda api_key, note: valid_report_json,
    )


class TestRootAndHealth:
    def test_root_returns_running_message(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "running" in response.json()["message"].lower()

    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestFormatNoteSuccess:
    def test_returns_structured_report(self, mock_openai_success, valid_report):
        response = client.post("/format-note", json={"raw_note": "some note"})
        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "AI report created successfully"
        assert body["input_note"] == "some note"
        assert body["report"] == valid_report


class TestFormatNoteValidationErrors:
    def test_empty_note_returns_400(self, mock_openai_success):
        response = client.post("/format-note", json={"raw_note": "   "})
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()

    def test_missing_field_returns_422(self):
        response = client.post("/format-note", json={})
        assert response.status_code == 422


class TestFormatNoteServerErrors:
    def test_missing_api_key_returns_500(self, monkeypatch):
        monkeypatch.setattr(main_module, "load_api_key", lambda: None)
        response = client.post("/format-note", json={"raw_note": "note"})
        assert response.status_code == 500
        assert "key" in response.json()["detail"].lower()

    def test_unparseable_ai_output_returns_500(self, monkeypatch):
        monkeypatch.setattr(main_module, "load_api_key", lambda: "test-key")
        monkeypatch.setattr(
            main_module,
            "call_openai_structured",
            lambda api_key, note: "not valid json {",
        )
        response = client.post("/format-note", json={"raw_note": "note"})
        assert response.status_code == 500
        assert "parsed" in response.json()["detail"].lower()

    def test_invalid_ai_report_returns_500_with_details(self, monkeypatch):
        monkeypatch.setattr(main_module, "load_api_key", lambda: "test-key")
        monkeypatch.setattr(
            main_module,
            "call_openai_structured",
            lambda api_key, note: '{"summary": "only summary"}',
        )
        response = client.post("/format-note", json={"raw_note": "note"})
        assert response.status_code == 500
        detail = response.json()["detail"]
        assert detail["message"] == "AI output validation failed"
        assert "issue" in detail["missing_fields"]

    def test_unexpected_error_returns_500(self, monkeypatch):
        monkeypatch.setattr(main_module, "load_api_key", lambda: "test-key")

        def boom(api_key, note):
            raise ValueError("boom")

        monkeypatch.setattr(main_module, "call_openai_structured", boom)
        response = client.post("/format-note", json={"raw_note": "note"})
        assert response.status_code == 500
        assert response.json()["detail"] == "Unexpected server error"
