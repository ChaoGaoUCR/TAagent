from typing import Any, Dict, List


def validate_rubric(rubric: Dict[str, Any]) -> None:
    if "criteria" not in rubric or not isinstance(rubric["criteria"], list):
        raise ValueError("Rubric must have a 'criteria' list")
    for c in rubric["criteria"]:
        if "id" not in c or "max_points" not in c:
            raise ValueError("Each criterion must include 'id' and 'max_points'")


def total_possible(rubric: Dict[str, Any]) -> float:
    return float(sum(c.get("max_points", 0) for c in rubric.get("criteria", [])))


def normalize_scores(rubric: Dict[str, Any], scores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    max_map = {c["id"]: c.get("max_points", 0) for c in rubric.get("criteria", [])}
    out = []
    for s in scores:
        cid = s.get("id")
        if cid not in max_map:
            continue
        max_points = max_map[cid]
        score = s.get("score", 0)
        if score > max_points:
            score = max_points
        if score < 0:
            score = 0
        out.append({
            "id": cid,
            "score": score,
            "comment": s.get("comment", "")
        })
    return out
