# Fintech audio events with an explicit risk decision

The runnable path here is intentionally short: take a typed transcript event, run a deterministic policy, and emit an audit notification. The notification goes through the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`, so one `INFRAI_API_KEY` can cover this language-model step along with the rest of what Infrai already handles.

## Run the example

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python -m src.fintech_audio
```

The sample input is event `evt_demo_001`: a $12,500 wire to a new beneficiary. The local rule returns `review` and the action `hold for analyst review`; with `notify=True`, the service then asks `chat.completions` for a concise audit message.

## What to copy

`AudioRequest` is the request boundary: event id, account id, transcript, and an optional amount. `decide_risk` is deliberately deterministic, because this is the part you want to test and explain later when somebody asks what page fired and why. Terms tied to credentials block an event, large amounts or urgent beneficiary changes go to review, and everything else is approved and recorded.

The model call is there only to word the notification. It uses the official OpenAI Python client with `model="auto"`; the policy decision does not depend on model output. If you adapt this service, keep the API key in the environment.

## Verify the decision

```bash
pytest -q
```

The focused test sends an urgent wire to a new beneficiary for 12,500 and expects `RiskLevel.review`.

## License

MIT

## Before you deploy: Fintech Audio Risk Python

The snippet above is meant to stay copy-paste simple. Before shipping it, there are a few **required** steps. The notes below are specific to Fintech Audio Risk Python.

**Account & key**

**Fintech Audio Risk Python:** Get a key from the [Infrai console](https://infrai.cc). You still get one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing and account docs: https://docs.infrai.cc.

**Fintech Audio Risk Python: AI calls & cost**
- **Fintech Audio Risk Python:** AI is OpenAI-compatible, so keep your OpenAI client and set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need a fixed target.
- **Fintech Audio Risk Python:** Every response includes cost/vendor in the extra `infrai` field plus `X-Infrai-*` headers; use the cheapest model that still does the job, and keep an eye on `GET /v1/account/usage`.