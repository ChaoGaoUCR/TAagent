from typing import Any, Dict, List


def rubric_table_md(rubric: Dict[str, Any], scores: List[Dict[str, Any]]) -> str:
    score_map = {s["id"]: s for s in scores}
    lines = ["| Criterion | Score | Max | Comment |", "|---|---:|---:|---|"]
    for c in rubric.get("criteria", []):
        cid = c.get("id")
        s = score_map.get(cid, {})
        lines.append(
            f"| {c.get('name','')} | {s.get('score',0)} | {c.get('max_points',0)} | {s.get('comment','')} |"
        )
    return "\n".join(lines)


def render_report(template: str, data: Dict[str, Any]) -> str:
    out = template
    for k, v in data.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out
