import argparse
import csv
import os
import zipfile
from typing import Any, Dict, List

from .canvas import CanvasClient
from .llm import score_document
from .report import render_report, rubric_table_md
from .rubric import normalize_scores, total_possible, validate_rubric
from .utils import ensure_dir, extract_text, load_json


def _unzip_if_needed(path: str, dest_dir: str) -> List[str]:
    if not path.lower().endswith(".zip"):
        return [path]
    files = []
    with zipfile.ZipFile(path, "r") as z:
        z.extractall(dest_dir)
        for name in z.namelist():
            files.append(os.path.join(dest_dir, name))
    return files


def _load_template(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = load_json(args.config)
    rubric = load_json(cfg["rubric_path"])
    validate_rubric(rubric)

    output_dir = cfg.get("output_dir", "outputs")
    ensure_dir(output_dir)

    llm_cfg = cfg["llm"]
    canvas_cfg = cfg["canvas"]

    client = CanvasClient(canvas_cfg["base_url"], canvas_cfg["api_token"])
    assignment = client.get_assignment(canvas_cfg["course_id"], canvas_cfg["assignment_id"])
    assignment_name = assignment.get("name", "Assignment")

    submissions = client.list_submissions(canvas_cfg["course_id"], canvas_cfg["assignment_id"])

    max_sub = cfg.get("limits", {}).get("max_submissions")
    if max_sub:
        submissions = submissions[: int(max_sub)]

    template = _load_template(os.path.join("templates", "report.md"))
    grades_path = os.path.join(output_dir, "grades.csv")

    with open(grades_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["submission_id", "user_id", "student_name", "score", "max_score", "report_path"])

        for sub in submissions:
            attachments = sub.get("attachments") or []
            if not attachments:
                continue

            user = sub.get("user") or {}
            student_name = user.get("name", "Unknown")
            submission_id = sub.get("id")
            user_id = sub.get("user_id")

            sub_dir = os.path.join(output_dir, f"submission_{submission_id}")
            ensure_dir(sub_dir)

            local_files: List[str] = []
            for att in attachments:
                path = client.download_attachment(att, sub_dir)
                local_files.extend(_unzip_if_needed(path, sub_dir))

            # Score first readable document
            doc_text = ""
            doc_name = ""
            for path in local_files:
                if os.path.isdir(path):
                    continue
                text = extract_text(path)
                if text.strip():
                    doc_text = text
                    doc_name = os.path.basename(path)
                    break

            if not doc_text:
                continue

            llm_result = score_document(doc_text, rubric, llm_cfg)
            scores = normalize_scores(rubric, llm_result.get("criteria", []))
            max_score = total_possible(rubric)
            total_score = llm_result.get("total_score")
            if total_score is None:
                total_score = sum(s.get("score", 0) for s in scores)

            report_body = render_report(
                template,
                {
                    "student_name": student_name,
                    "assignment_name": assignment_name,
                    "submission_id": submission_id,
                    "user_id": user_id,
                    "file_name": doc_name,
                    "total_score": total_score,
                    "total_possible": max_score,
                    "summary": llm_result.get("summary", ""),
                    "rubric_table": rubric_table_md(rubric, scores),
                },
            )

            report_path = os.path.join(sub_dir, "report.md")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report_body)

            writer.writerow([submission_id, user_id, student_name, total_score, max_score, report_path])


if __name__ == "__main__":
    main()
