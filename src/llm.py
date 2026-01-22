import json
from typing import Any, Dict


PROMPT_TEMPLATE = """You are a TA grading a document submission using the rubric below.

Rubric (JSON):
{rubric_json}

Document (text):
{text}

Return JSON only with this schema:
{{
  "summary": "overall feedback",
  "criteria": [
    {{"id": "criterion_id", "score": number, "comment": "short comment"}}
  ],
  "total_score": number
}}

Rules:
- Use rubric criteria ids.
- Scores must be between 0 and max_points for each criterion.
- Keep comments concise and specific.
"""


def score_document(text: str, rubric: Dict[str, Any], llm_cfg: Dict[str, Any]) -> Dict[str, Any]:
    provider = llm_cfg.get("provider")
    model = llm_cfg.get("model")
    api_key = llm_cfg.get("api_key")

    prompt = PROMPT_TEMPLATE.format(
        rubric_json=json.dumps(rubric, ensure_ascii=True),
        text=text[:12000],
    )

    if provider == "openai":
        return _score_with_openai(prompt, model, api_key)
    if provider == "anthropic":
        return _score_with_anthropic(prompt, model, api_key)
    raise ValueError("Unsupported LLM provider")


def _score_with_openai(prompt: str, model: str, api_key: str) -> Dict[str, Any]:
    from openai import OpenAI  # type: ignore

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a careful grader."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    return json.loads(content)


def _score_with_anthropic(prompt: str, model: str, api_key: str) -> Dict[str, Any]:
    from anthropic import Anthropic  # type: ignore

    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=1200,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join([b.text for b in resp.content if hasattr(b, "text")])
    text = text.strip() or "{}"
    return json.loads(text)
