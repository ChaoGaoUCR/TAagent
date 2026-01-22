# TA Agent (Canvas + LLM)

Downloads Canvas submissions for one assignment, scores document submissions using a JSON rubric and OpenAI/Anthropic, and writes Markdown reports + a grades CSV.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure

Copy `config.example.json` to `config.json` and fill in:
- Canvas base URL, course_id, assignment_id, API token
- Rubric path (JSON)
- LLM provider + model + API key

Example:

```json
{
  "canvas": {
    "base_url": "https://canvas.yourschool.edu",
    "course_id": 12345,
    "assignment_id": 67890,
    "api_token": "CANVAS_API_TOKEN"
  },
  "rubric_path": "rubric.json",
  "output_dir": "outputs",
  "llm": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "api_key": "OPENAI_API_KEY"
  }
}
```

## Run

```bash
python -m src.main --config config.json
```

Outputs:
- `outputs/submission_<id>/report.md`
- `outputs/grades.csv`

## Notes
- Supports `.txt`, `.md`, `.docx`, `.pdf` (via optional deps in `requirements.txt`).
- For `.zip` submissions, the first readable document found will be scored.
