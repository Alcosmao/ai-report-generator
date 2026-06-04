import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

NOTES_DIR = BASE_DIR / "notes"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

INPUT_FILE = NOTES_DIR / "raw_note.txt"
JSON_OUTPUT_FILE = REPORTS_DIR / "report.json"
TXT_OUTPUT_FILE = REPORTS_DIR / "report.txt"
LOG_FILE = LOGS_DIR / "app_log.txt"


def setup_folders():
    NOTES_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)


def write_log(message, file_path=LOG_FILE):
    with open(file_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


def read_input_file(file_path=INPUT_FILE):
    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def save_json(data, file_path=JSON_OUTPUT_FILE):
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)


def create_txt_report(report_data):
    lines = []

    lines.append("AI REPORT")
    lines.append("=" * 60)
    lines.append("")

    lines.append("Summary:")
    lines.append(report_data["summary"])
    lines.append("")

    lines.append("Issue:")
    lines.append(report_data["issue"])
    lines.append("")

    lines.append("Actions taken:")
    for action in report_data["actions_taken"]:
        lines.append(f"- {action}")

    lines.append("")

    lines.append("Next steps:")
    for step in report_data["next_steps"]:
        lines.append(f"- {step}")

    lines.append("")

    return "\n".join(lines)


def save_txt(text, file_path=TXT_OUTPUT_FILE):
    file_path.write_text(text, encoding="utf-8")