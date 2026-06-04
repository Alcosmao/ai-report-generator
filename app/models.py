from pydantic import BaseModel


class NoteRequest(BaseModel):
    raw_note: str


class ReportData(BaseModel):
    summary: str
    issue: str
    actions_taken: list[str]
    next_steps: list[str]


class NoteResponse(BaseModel):
    message: str
    input_note: str
    report: ReportData