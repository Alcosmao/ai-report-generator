import json
import os

from dotenv import load_dotenv
from openai import OpenAI


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


def load_api_key():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    return api_key


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