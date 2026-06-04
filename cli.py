from openai import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APIStatusError,
    BadRequestError,
)

from app.services import (
    load_api_key,
    call_openai_structured,
    parse_ai_output,
    validate_report,
)

from app.file_utils import (
    setup_folders,
    write_log,
    read_input_file,
    save_json,
    create_txt_report,
    save_txt,
    INPUT_FILE,
    JSON_OUTPUT_FILE,
    TXT_OUTPUT_FILE,
    LOG_FILE,
)


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
        print(f"Input file not found: {INPUT_FILE}")
        print("No input text to process.")
        write_log("ERROR: Input file missing", LOG_FILE)
        return

    if not note_text.strip():
        print("Input file is empty.")
        write_log("ERROR: Input file is empty", LOG_FILE)
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

    except Exception as error:
        print("Unexpected error.")
        print(error)
        write_log("ERROR: Unexpected error", LOG_FILE)
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