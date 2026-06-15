from fastapi import FastAPI, HTTPException
from openai import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIStatusError,
    BadRequestError,
)

from app.models import NoteRequest, NoteResponse
from app.services import (
    load_api_key,
    call_openai_structured,
    parse_ai_output,
    validate_report,
)
from app.file_utils import (
    setup_folders,
    save_json,
    create_txt_report,
    save_txt,
    build_report_paths,
)


app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "AI Note Formatter API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "AI Note Formatter API"
    }


@app.post("/format-note", response_model=NoteResponse)
def format_note(request: NoteRequest):
    try:
        if not request.raw_note.strip():
            raise HTTPException(
                status_code=400,
                detail="raw_note cannot be empty"
            )

        api_key = load_api_key()

        if api_key is None:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key is missing"
            )

        raw_ai_output = call_openai_structured(api_key, request.raw_note)

        report_data = parse_ai_output(raw_ai_output)

        if report_data is None:
            raise HTTPException(
                status_code=500,
                detail="AI output could not be parsed"
            )

        is_valid, missing, wrong_types = validate_report(report_data)

        if not is_valid:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "AI output validation failed",
                    "missing_fields": missing,
                    "wrong_type_fields": wrong_types
                }
            )

        setup_folders()

        json_path, txt_path = build_report_paths()

        save_json(report_data, json_path)

        txt_report = create_txt_report(report_data)
        save_txt(txt_report, txt_path)

        return {
            "message": "AI report created successfully",
            "input_note": request.raw_note,
            "report": report_data
        }

    except HTTPException:
        raise

    except AuthenticationError:
        raise HTTPException(
            status_code=500,
            detail="OpenAI authentication failed. Check the API key."
        )

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="OpenAI rate limit or quota error. Try again later."
        )

    except APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to OpenAI. Check network connection."
        )

    except BadRequestError:
        raise HTTPException(
            status_code=500,
            detail="OpenAI request configuration error."
        )

    except APIStatusError as error:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "OpenAI returned an error status.",
                "openai_status_code": error.status_code
            }
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )