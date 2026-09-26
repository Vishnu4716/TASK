import json
import re
import requests
import urllib3

from config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, PROXIES

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LLMError(RuntimeError):
    pass


def call_llm(messages, temperature=0):
    if not LLM_BASE_URL:
        raise LLMError("LLM_BASE_URL is not configured.")
    if not LLM_API_KEY:
        raise LLMError("LLM_API_KEY is not configured.")

    url = f"{LLM_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        proxies=PROXIES or None,
        verify=False,
        timeout=90,
    )
    response.raise_for_status()

    body = response.json()
    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise LLMError(f"Unexpected LLM response: {body}") from exc


def extract_json(text):
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.S | re.I)
    if fenced:
        text = fenced.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


def interpret_request(request_row):
    system = """You are the interpretation component of a fare-dispute resolution agent.

Return ONLY valid JSON with exactly these keys:
intent, requested_resolution, requested_amount, claimed_reason, trip_id, confidence.

Allowed intent values:
- OVERCHARGE
- SURGE_OVERCHARGE
- ROUTE_DEVIATION
- INCORRECT_DROPOFF
- DRIVER_CANCELLED
- RIDER_CANCELLED
- OTHER

Allowed requested_resolution values:
- REFUND
- CREDIT
- REPLACEMENT_RIDE_CREDIT
- UNKNOWN

requested_amount must be a number or null.
confidence must be a number from 0 to 1.

Do not decide eligibility. Do not invent trip facts. The trip_id supplied in the input is authoritative unless the request text explicitly contains a different trip ID."""
    user = f"""Interpret this dispute request:

request_id: {request_row['request_id']}
rider_name: {request_row['rider_name']}
rider_tier: {request_row['rider_tier']}
trip_id: {request_row['trip_id']}
request_text: {request_row['request_text']}
"""
    raw = call_llm(
        [{"role": "system", "content": system}, {"role": "user", "content": user}]
    )
    data = extract_json(raw)

    data["trip_id"] = str(data.get("trip_id") or request_row["trip_id"])

    try:
        data["requested_amount"] = (
            None if data.get("requested_amount") is None
            else float(data["requested_amount"])
        )
    except (TypeError, ValueError):
        data["requested_amount"] = None

    try:
        data["confidence"] = float(data.get("confidence", 0))
    except (TypeError, ValueError):
        data["confidence"] = 0.0

    return data
