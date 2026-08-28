from src.fintech_audio import AudioRequest, RiskLevel, decide_risk


def test_new_beneficiary_large_wire_requires_review():
    request = AudioRequest(
        event_id="evt_7",
        account_id="acct_7",
        transcript="Urgent wire to a new beneficiary",
        amount=12_500,
    )
    assert decide_risk(request) is RiskLevel.review
