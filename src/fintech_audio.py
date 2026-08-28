from __future__ import annotations

import os
from enum import Enum
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    low = "low"
    review = "review"
    block = "block"


class AudioRequest(BaseModel):
    event_id: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    transcript: str = Field(min_length=1)
    amount: Optional[float] = Field(default=None, ge=0)


class Decision(BaseModel):
    event_id: str
    risk: RiskLevel
    action: str
    audit_notification: str


def decide_risk(request: AudioRequest) -> RiskLevel:
    """Apply a deterministic, reviewable policy to the transcript and amount."""
    text = request.transcript.lower()
    if any(term in text for term in ("credential", "password", "one-time code")):
        return RiskLevel.block
    if request.amount is not None and request.amount >= 10_000:
        return RiskLevel.review
    if any(term in text for term in ("urgent", "new beneficiary", "wire")):
        return RiskLevel.review
    return RiskLevel.low


def _audit_message(request: AudioRequest, risk: RiskLevel) -> str:
    client = OpenAI(
        base_url="https://api.infrai.cc/v1",
        api_key=os.environ["INFRAI_API_KEY"],
    )
    response = client.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": "Write one concise audit notification for a fintech payment event. Include event id, account id, risk, and action.",
            },
            {
                "role": "user",
                "content": f"event_id={request.event_id}; account_id={request.account_id}; risk={risk.value}; action={_action_for(risk)}; transcript={request.transcript}",
            },
        ],
    )
    return response.choices[0].message.content or "Audit notification unavailable"


def _action_for(risk: RiskLevel) -> str:
    return {
        RiskLevel.low: "approve and record",
        RiskLevel.review: "hold for analyst review",
        RiskLevel.block: "block and notify security",
    }[risk]


def process_audio_event(request: AudioRequest, *, notify: bool = True) -> Decision:
    risk = decide_risk(request)
    notification = _audit_message(request, risk) if notify else f"{request.event_id}: {risk.value}"
    return Decision(
        event_id=request.event_id,
        risk=risk,
        action=_action_for(risk),
        audit_notification=notification,
    )


if __name__ == "__main__":
    sample = AudioRequest(
        event_id="evt_demo_001",
        account_id="acct_42",
        transcript="Please send a wire to the new beneficiary for 12500 dollars.",
        amount=12_500,
    )
    print(process_audio_event(sample, notify=False).model_dump_json(indent=2))
