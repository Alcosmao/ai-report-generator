import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    OpenAI,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIStatusError,
    BadRequestError,
)


BASE_DIR = Path(__file__).parent

NOTES_DIR = BASE_DIR / "notes"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

INPUT_FILE = NOTES_DIR / "raw_note.txt"
JSON_OUTPUT_FILE = REPORTS_DIR / "report.json"
TXT_OUTPUT_FILE = REPORTS_DIR / "report.txt"
LOG_FILE = LOGS_DIR / "app_log.txt"

MODEL_NAME = "gpt-5.4-mini"


REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "issue": {"type": "string"},
        "actions_taken": {
            "type": "array",
            "items": {"type": "string"},
        },
        "next_steps": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "summary",
        "issue",
        "actions_taken",
        "next_steps",
    ],
    "additionalProperties": False,
}


def setup_folders():
    NOTES_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)


def write_log(message, file_path):
    with open(file_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


def load_api_key():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return api_key


def read_input_file(file_path):
    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Input file not found: {file_path}")
        return None


def call_openai_structured(api_key, note_text):
    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=MODEL_NAME,
        instructions="""
You convert raw notes into structured automation reports.

Rules:
- Do not invent facts.
- Use simple professional English.
- If information is missing, do not guess.
""",
        input=f"""
Convert this raw note into a structured report.

Raw note:
{note_text}
""",
        text={
            "format": {
                "type": "json_schema",
                "name": "automation_report",
                "strict": True,
                "schema": REPORT_SCHEMA,
            }
        },
    )

    return response.output_text


def parse_ai_output(raw_output):
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("AI output is not valid JSON")
        return None


def validate_report(report_data):
    required_fields = {
        "summary": str,
        "issue": str,
        "actions_taken": list,
        "next_steps": list,
    }

    missing_fields = []
    wrong_type_fields = []

    for field, expected_type in required_fields.items():
        if field not in report_data:
            missing_fields.append(field)
        elif not isinstance(report_data[field], expected_type):
            wrong_type_fields.append(field)

    if missing_fields or wrong_type_fields:
        return False, missing_fields, wrong_type_fields

    for item in report_data["actions_taken"]:
        if not isinstance(item, str):
            return False, [], ["actions_taken must contain only strings"]

    for item in report_data["next_steps"]:
        if not isinstance(item, str):
            return False, [], ["next_steps must contain only strings"]

    return True, [], []


def save_json(data, file_path):
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


def save_txt(text, file_path):
    file_path.write_text(text, encoding="utf-8")


def main():
    print("-----------------------------")
    print("AI Report Generator")
    print("-----------------------------")

    setup_folders()
    write_log("Program started", LOG_FILE)

    print("Project folders ready")

    api_key = load_api_key()

    if api_key is None:
        print("API key is missing. Check your .env file.")
        write_log("ERROR: API key missing", LOG_FILE)
        return

    print("API key loaded successfully")
    write_log("API key loaded successfully", LOG_FILE)

    note_text = read_input_file(INPUT_FILE)

    if note_text is None:
        print("No input text to process.")
        write_log("ERROR: Input file missing", LOG_FILE)
        return

    print("Input file loaded successfully")
    write_log("Input file loaded successfully", LOG_FILE)

    print("-----------------------------")
    print("Input preview:")
    print(note_text[:300])
    print("-----------------------------")

    try:
        raw_ai_output = call_openai_structured(api_key, note_text)

    except AuthenticationError:
        print("Authentication error. Check your OPENAI_API_KEY.")
        write_log("ERROR: Authentication error", LOG_FILE)
        return

    except RateLimitError:
        print("Rate limit or quota error.")
        write_log("ERROR: Rate limit or quota error", LOG_FILE)
        return

    except APIConnectionError:
        print("Connection error. Check your internet connection.")
        write_log("ERROR: API connection error", LOG_FILE)
        return

    except BadRequestError as error:
        print("Bad request error.")
        print(error)
        write_log("ERROR: Bad request error", LOG_FILE)
        return

    except APIStatusError as error:
        print("OpenAI API returned an error status.")
        print("Status code:", error.status_code)
        write_log(f"ERROR: API status error {error.status_code}", LOG_FILE)
        return

    report_data = parse_ai_output(raw_ai_output)

    if report_data is None:
        print("Could not parse AI output.")
        write_log("ERROR: Could not parse AI output", LOG_FILE)
        return

    is_valid, missing, wrong_types = validate_report(report_data)

    if not is_valid:
        print("Validation failed")
        print(f"Missing fields: {missing}")
        print(f"Wrong type fields: {wrong_types}")
        write_log("ERROR: Validation failed", LOG_FILE)
        return

    print("Validation passed")
    write_log("Validation passed", LOG_FILE)

    save_json(report_data, JSON_OUTPUT_FILE)
    print("JSON report saved")

    txt_report = create_txt_report(report_data)
    save_txt(txt_report, TXT_OUTPUT_FILE)
    print("TXT report saved")

    write_log("Reports saved successfully", LOG_FILE)

    print("-----------------------------")
    print("Reports created successfully")
    print(f"JSON report: {JSON_OUTPUT_FILE}")
    print(f"TXT report: {TXT_OUTPUT_FILE}")
    print("-----------------------------")
    print("Summary:")
    print(report_data["summary"])
    print("")
    print("Issue:")
    print(report_data["issue"])
    print("-----------------------------")


if __name__ == "__main__":
    main()