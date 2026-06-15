import json

import pytest


@pytest.fixture
def valid_report():
    return {
        "summary": "Customer reported a missing invoice attachment.",
        "issue": "The invoice email did not include the PDF attachment.",
        "actions_taken": [
            "Reviewed the customer email",
            "Confirmed the attachment was missing",
        ],
        "next_steps": [
            "Reply to the customer",
            "Request a resend of the invoice file",
        ],
    }


@pytest.fixture
def valid_report_json(valid_report):
    return json.dumps(valid_report)
