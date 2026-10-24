from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    email: str = Field(min_length=5, max_length=200)
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=100)


class LoginIn(BaseModel):
    email: str
    password: str


class ReviewIn(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    channel: str = "social"
    use_ai: bool = False


class DraftIn(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
    channel: str = "social"
    intent: dict = {}
    findings: list[dict] = []  # only AI-suggested ones are trusted after re-verification


class DecisionIn(BaseModel):
    decision: str  # uphold | waive
    note: str = ""


class FinalizeIn(BaseModel):
    status: str  # approved | changes_requested


class EventIn(BaseModel):
    type: str  # accept | dispute
    rule_id: str | None = None
    draft_id: int | None = None


class FactPatch(BaseModel):
    value: float
    valid_until: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class RulePatch(BaseModel):
    approved: bool
