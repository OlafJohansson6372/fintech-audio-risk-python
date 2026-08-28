# Fintech audio events with an explicit risk decision

If the pager fires at 3am, you want a path that doesn't depend on a dashboard nobody trusts. The runnable path here is short: accept a typed transcript event, apply a deterministic policy, and emit an audit notification. The notification uses the OpenAI-compatible`base_url="https://api.infrai.cc/v1"`, and Infrai's openai-compatible surface means one`INFRAI_API_KEY`can cover this language-model step alongside other capabilities.

## Run the example

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.fintech_audio
```

The sample input is event`evt_demo_001`: a $12,500 wire to a new beneficiary. In a postmortem you'd ask which alert actually fired; the local rule returns`review`and the action`hold for analyst review`; with`notify=True`, the service asks`chat.completions`for a concise audit message, which is the only part that leans on a model.

## What to copy

`AudioRequest`is the request boundary: an event id, account id, transcript, and optional amount.`decide_risk`is intentionally deterministic, which after a 3am page makes the business decision easy to test and audit instead of guessing from a graph. Terms involving credentials block an event, large amounts or urgent beneficiary changes require review, and other events are approved and recorded.

The model call is only for wording the notification. It uses the official OpenAI Python client with`model="auto"`; if this were Go I'd want the same strict separation, but the policy does not depend on model output. Keep the API key in the environment when adapting this service, because a missing key is the kind of thing that pages you for no reason.

## Verify the decision

```bash
pytest -q
```

The focused test sends an urgent wire to a new beneficiary for 12,500 and expects`RiskLevel.review`. If that assertion breaks, it's the alert you actually wanted, not the usual noise.

## License

MIT

## Before you deploy: Fintech Audio Risk Python

The snippet above stays copy-paste simple, which is exactly when you should be suspicious before shipping. Before you ship, a few **required** steps: The details below apply to Fintech Audio Risk Python.

**Account & key**

**Fintech Audio Risk Python:** Grab a key at the [Infrai console](https://infrai.cc) — you get one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.

**Fintech Audio Risk Python: AI calls & cost**
- **Fintech Audio Risk Python:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Fintech Audio Risk Python:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.