from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


# =========================
# 1) Output schema
# =========================


class FlowixRisk(BaseModel):
    category: str = Field(..., description="Risk category, e.g., Technical, Timeline, Budget, Legal, Product")
    description: str = Field(..., description="Clear explanation of the risk in plain language")
    mitigation: str = Field(..., description="Practical mitigation/next step to reduce the risk")
    severity: str = Field(..., description="Low, Medium, or High")


class FlowixOutput(BaseModel):
    summary: str = Field("", description="1–3 sentence executive summary")
    scope: List[str] = Field(default_factory=list, description="In-scope deliverables/features")
    not_included: List[str] = Field(default_factory=list, description="Explicit out-of-scope items/boundaries")
    missing_info: List[str] = Field(default_factory=list, description="Info needed for accurate quote/timeline")
    risks: List[FlowixRisk] = Field(default_factory=list, description="Risks and mitigations")
    questions: List[str] = Field(default_factory=list, description="Questions to ask the client next")


class PhaseArtifacts(BaseModel):
    architect: str
    auditor: str
    strategist_raw: str
    output: FlowixOutput


# =========================
# 2) LLM config (LangChain)
# =========================


@dataclass(frozen=True)
class LLMConfig:
    provider: str  # "openai" | "groq"
    model: str
    temperature: float = 0.1
    timeout_s: float = 45.0


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def _build_llm(config: LLMConfig) -> ChatOpenAI:
    provider = (config.provider or "openai").lower().strip()
    if provider == "openai":
        return ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            timeout=config.timeout_s,
            api_key=_require_env("OPENAI_API_KEY"),
        )
    if provider == "groq":
        return ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            timeout=config.timeout_s,
            api_key=_require_env("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        )
    raise ValueError(f"Unknown provider: {config.provider}")


# =========================
# 3) Prompt flow: Architect → Auditor → Strategist
# =========================


SYSTEM_STYLE_RULES = """You are FlowixPro AI: a client-message clarity engine.

Hard rules:
- Output MUST be valid JSON when asked for JSON.
- Do NOT wrap JSON in markdown fences.
- Do NOT include any keys other than the requested schema.
- Use concise, professional phrasing.
- If info is missing, list it in missing_info and ask in questions.
- If user asks for unrealistic scope/time/budget, flag in risks with severity High.
"""

ARCHITECT_SYSTEM = (
    SYSTEM_STYLE_RULES
    + """
Role: Architect
Goal: Decode messy client input into crisp technical intent and requirements.
Output: Plain text bullets (not JSON).
Focus:
- What they want (features, users, platforms)
- Constraints (deadline, budget, stack, integrations)
- Success criteria and assumptions
"""
)

AUDITOR_SYSTEM = (
    SYSTEM_STYLE_RULES
    + """
Role: Auditor
Goal: Identify missing info, risks, and inconsistencies based on raw message + architect notes.
Output: Plain text bullets (not JSON).
Focus:
- Risks (technical, timeline, budget, legal/compliance, security, scope creep)
- Missing info required for accurate estimate
- Any red flags / contradictions
"""
)

STRATEGIST_SYSTEM = (
    SYSTEM_STYLE_RULES
    + """
Role: Strategist
Goal: Produce the final structured JSON for the client-message.

Return JSON with EXACT schema:
{{
  "summary": "",
  "scope": [],
  "not_included": [],
  "missing_info": [],
  "risks": [
    {{"category":"","description":"","mitigation":"","severity":""}}
  ],
  "questions": []
}}

Notes:
- scope/not_included/missing_info/questions are arrays of strings.
- risks is an array of objects with severity in ["Low","Medium","High"].
- Keep summary <= 3 sentences.
- If uncertain, be explicit in missing_info/questions, not in summary.
"""
)


def _extract_json_object(text: str) -> str:
    s = text.strip()
    if not s:
        return s
    start = s.find("{")
    if start == -1:
        return s
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start : i + 1]
    return s[start:]


class FlowixEngine:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.llm = _build_llm(config)

    def ask(self, system: str, user: str) -> str:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("user", user),
            ]
        )
        msg = (prompt | self.llm).invoke({})
        return getattr(msg, "content", "") or ""

    @staticmethod
    def parse_output(strategist_raw: str) -> FlowixOutput:
        candidate = _extract_json_object(strategist_raw)
        try:
            obj = json.loads(candidate)
        except Exception:
            obj = None

        if obj is not None:
            try:
                return FlowixOutput.model_validate(obj)
            except ValidationError:
                pass

        return FlowixOutput(
            summary="",
            scope=[],
            not_included=[],
            missing_info=["Failed to reliably parse model output into JSON."],
            risks=[],
            questions=["Can you re-send the request in 3–5 bullet points (goals, deadline, budget, platform)?"],
        )

    def run(self, client_message: str) -> PhaseArtifacts:
        architect = self.ask(ARCHITECT_SYSTEM, client_message)
        auditor = self.ask(AUDITOR_SYSTEM, f"RAW MESSAGE:\n{client_message}\n\nARCHITECT NOTES:\n{architect}")
        strategist_raw = self.ask(
            STRATEGIST_SYSTEM,
            (
                f"RAW MESSAGE:\n{client_message}\n\n"
                f"ARCHITECT NOTES:\n{architect}\n\n"
                f"AUDITOR NOTES:\n{auditor}\n\n"
                "Return ONLY the JSON object."
            ),
        )
        parsed = self.parse_output(strategist_raw)

        return PhaseArtifacts(
            architect=architect,
            auditor=auditor,
            strategist_raw=strategist_raw,
            output=parsed,
        )

# =========================
# 5) FastAPI service
# =========================


app = FastAPI(title="FlowixPro AI Prototype", version="0.1.0")
load_dotenv()

# Defaults are captured at startup so they appear correctly in Swagger/OpenAPI.
DEFAULT_PROVIDER = os.getenv("FLOWIX_PROVIDER", "openai")
DEFAULT_MODEL = os.getenv("FLOWIX_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = float(os.getenv("FLOWIX_TEMPERATURE", "0.1"))


class AnalyzeRequest(BaseModel):
    message: str = Field(..., description="Messy client message")
    provider: str = Field(default=DEFAULT_PROVIDER, description="LLM provider (OpenAI-compatible)")
    model: str = Field(default=DEFAULT_MODEL, description="Model name for the provider")
    temperature: float = Field(default=DEFAULT_TEMPERATURE, ge=0.0, le=1.0)


class AnalyzeResponse(BaseModel):
    summary: str = ""
    scope: List[str] = Field(default_factory=list)
    not_included: List[str] = Field(default_factory=list)
    missing_info: List[str] = Field(default_factory=list)
    risks: List[FlowixRisk] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    if not req.message.strip():
        return JSONResponse(status_code=400, content={"error": "message is required"})

    engine = FlowixEngine(
        LLMConfig(provider=req.provider, model=req.model, temperature=req.temperature),
    )
    artifacts = engine.run(req.message)
    return artifacts.output.model_dump()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)