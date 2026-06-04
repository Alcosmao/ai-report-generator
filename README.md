# AI Technical Note Formatter API

AI Technical Note Formatter API is a Python and FastAPI project that uses the OpenAI API to convert raw notes into structured reports.

The project can be used in two ways:

1. As a FastAPI API service using `POST /format-note`
2. As a local CLI script using `python cli.py`

The application accepts a raw business or technical note, sends it to OpenAI, receives structured JSON output, validates the result, returns the response through the API, and saves the final report as both JSON and TXT files.

This project was built as part of my learning path toward AI Automation, Junior AI Solutions, Copilot Studio, Power Platform, and Azure AI-related roles.

---

## Project overview

This project demonstrates a small AI automation workflow:

```text
raw note
→ FastAPI endpoint
→ OpenAI API
→ structured JSON output
→ validation
→ API response
→ JSON report
→ TXT report
```

The main goal of the project is to practise how Python, FastAPI, and the OpenAI API can be used to build a small AI-powered backend service.

The project is based on realistic notes such as:

* customer support notes
* missing invoice attachment reports
* technical maintenance notes
* field service engineering notes
* troubleshooting notes
* SOP-style notes

---

## Features

* FastAPI API application
* `GET /` root endpoint
* `GET /health` health check endpoint
* `POST /format-note` endpoint
* JSON request body
* JSON response body
* Pydantic request and response models
* OpenAI API integration
* Structured JSON output from OpenAI
* JSON schema for AI output
* Manual validation of AI-generated reports
* API error handling with HTTP status codes
* Specific OpenAI error handling
* Saves report as JSON
* Saves report as human-readable TXT
* CLI runner version
* Swagger UI documentation
* Example request, response, and report files
* Portfolio-ready project structure

---

## API flow

```text
Client / Swagger
→ POST /format-note
→ raw_note as JSON
→ FastAPI validates input
→ OpenAI generates structured report
→ Python parses AI output
→ Python validates report fields
→ API returns structured JSON response
→ project saves report.json and report.txt
```

---

## CLI flow

```text
notes/raw_note.txt
→ cli.py
→ load API key
→ call OpenAI API
→ receive structured JSON
→ parse JSON
→ validate data
→ save report.json
→ save report.txt
→ write logs
```

---

## API endpoints

### Root endpoint

```http
GET /
```

Example response:

```json
{
  "message": "AI Note Formatter API is running"
}
```

---

### Health check endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "AI Note Formatter API"
}
```

---

### Format note endpoint

```http
POST /format-note
```

Example request:

```json
{
  "raw_note": "Customer emailed the support team regarding invoice INV-1044. The customer stated that the invoice email was received, but the expected PDF attachment was missing. I checked the email thread and confirmed that no attachment was included. No payment issue was reported by the customer. The next action is to reply to the customer, apologize for the inconvenience, and request that they resend the missing invoice file or confirm if they want us to regenerate the invoice document."
}
```

Example response:

```json
{
  "message": "AI report created successfully",
  "input_note": "Customer emailed the support team regarding invoice INV-1044. The customer stated that the invoice email was received, but the expected PDF attachment was missing. I checked the email thread and confirmed that no attachment was included. No payment issue was reported by the customer. The next action is to reply to the customer, apologize for the inconvenience, and request that they resend the missing invoice file or confirm if they want us to regenerate the invoice document.",
  "report": {
    "summary": "The customer reported that invoice INV-1044 was received without the expected PDF attachment.",
    "issue": "The invoice email did not include the required PDF attachment.",
    "actions_taken": [
      "Reviewed the customer email regarding invoice INV-1044",
      "Confirmed that the expected PDF attachment was missing",
      "Confirmed that no payment issue was reported"
    ],
    "next_steps": [
      "Reply to the customer and apologize for the inconvenience",
      "Request that the customer resend the missing invoice file",
      "Ask the customer to confirm if they want the invoice document regenerated"
    ]
  }
}
```

---

## Output structure

The AI-generated report should return these fields:

```json
{
  "summary": "Short summary of the note",
  "issue": "Main issue found in the note",
  "actions_taken": [
    "Action already taken"
  ],
  "next_steps": [
    "Recommended next step"
  ]
}
```

The project checks that:

* `summary` exists and is text
* `issue` exists and is text
* `actions_taken` exists and is a list
* `next_steps` exists and is a list
* all items inside `actions_taken` are text
* all items inside `next_steps` are text

---

## Technologies used

* Python
* FastAPI
* Uvicorn
* OpenAI API
* OpenAI Python SDK
* Pydantic
* python-dotenv
* JSON
* pathlib
* Swagger UI
* try/except error handling
* file handling

---

## Project structure

```text
AI_Report_Generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI endpoints
│   ├── models.py        # Pydantic request and response models
│   ├── services.py      # OpenAI logic and AI output validation
│   └── file_utils.py    # File saving and folder utilities
│
├── examples/
│   ├── example_request.json
│   ├── example_response.json
│   └── example_report.txt
│
├── notes/
│   └── raw_note.txt
│
├── reports/
│   ├── report.json
│   └── report.txt
│
├── logs/
│   └── app_log.txt
│
├── cli.py
├── README.md
├── requirements.txt
├── .gitignore
└── .env
```

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd AI_Report_Generator
```

---

### 2. Create and activate a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

### 3. Install required packages

```bash
python -m pip install -r requirements.txt
```

Required packages:

```text
fastapi
uvicorn
openai
python-dotenv
```

---

## Environment variables

Create a `.env` file in the main project folder:

```text
OPENAI_API_KEY=your_api_key_here
```

Do not share this file publicly.

For GitHub, use `.env.example` instead:

```text
OPENAI_API_KEY=your_api_key_here
```

---

## How to run the API version

Start the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Open the API in the browser:

```text
http://127.0.0.1:8000
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

In Swagger UI:

1. Open `POST /format-note`
2. Click `Try it out`
3. Paste JSON input
4. Click `Execute`
5. Check the JSON response

---

## How to run the CLI version

Add your raw note to:

```text
notes/raw_note.txt
```

Example input:

```text
Customer email received about missing invoice attachment.
Invoice number: INV-1044.
Attachment was not found in the email.
Need to request the customer to resend the invoice file.
```

Run:

```bash
python cli.py
```

After successful execution, the project creates:

```text
reports/report.json
reports/report.txt
logs/app_log.txt
```

---

## Generated files

The API and CLI versions can generate:

```text
reports/report.json
reports/report.txt
logs/app_log.txt
```

`report.json` is machine-readable output.

`report.txt` is human-readable output.

---

## Examples folder

The `examples/` folder contains safe demo files for portfolio purposes:

```text
examples/example_request.json
examples/example_response.json
examples/example_report.txt
```

These files show how the project works without exposing real user or business data.

The `examples/` folder should be committed to GitHub.

---

## Example TXT output

```text
AI REPORT
============================================================

Summary:
The customer reported that invoice INV-1044 was received without the expected PDF attachment.

Issue:
The invoice email did not include the required PDF attachment.

Actions taken:
- Reviewed the customer email regarding invoice INV-1044
- Confirmed that the expected PDF attachment was missing
- Confirmed that no payment issue was reported

Next steps:
- Reply to the customer and apologize for the inconvenience
- Request that the customer resend the missing invoice file
- Ask the customer to confirm if they want the invoice document regenerated
```

---

## Error handling

The API handles several common problems:

* missing `raw_note`
* empty `raw_note`
* missing OpenAI API key
* invalid AI JSON output
* failed AI output validation
* OpenAI authentication error
* OpenAI rate limit or quota error
* OpenAI API connection error
* OpenAI bad request error
* OpenAI API status error
* unexpected server errors

Example API error response:

```json
{
  "detail": "raw_note cannot be empty"
}
```

---

## Security notes

The OpenAI API key is stored in a local `.env` file.

The `.env` file should never be committed to GitHub.

Recommended `.gitignore` entries:

```text
.env
__pycache__/
*.pyc
logs/
reports/
.venv/
```

The `logs/` and `reports/` folders are local output folders. They may contain generated or sensitive data and should usually stay out of GitHub.

The `examples/` folder should be committed because it contains safe demo data.

---

## What I learned

This project helped me practise:

* building a FastAPI application
* creating GET and POST endpoints
* using Swagger UI for API testing
* receiving JSON input through request body
* returning JSON response body
* using Pydantic request and response models
* calling the OpenAI API from a backend service
* using JSON schema for structured AI output
* parsing AI output into Python data
* validating AI-generated data
* handling API errors with HTTP status codes
* handling OpenAI-specific errors
* saving JSON and TXT output files
* separating code into modules
* creating a CLI runner
* preparing a project for GitHub portfolio

---

## Portfolio value

This project demonstrates a realistic beginner-friendly AI automation workflow:

```text
API request
→ AI processing
→ structured data
→ validation
→ JSON response
→ saved reports
```

It shows how a Python script can be upgraded into a small API service.

This type of workflow is useful in:

* AI automation
* business operations
* support ticket processing
* technical note formatting
* maintenance reporting
* junior AI solutions projects
* future Power Platform or Copilot Studio integrations

---

## Future improvements

Possible future improvements:

* Add timestamped report filenames
* Add automated tests
* Add Docker support
* Add frontend form
* Add authentication
* Add database storage
* Add deployment instructions
* Add RAG-based document assistant functionality in a separate project
