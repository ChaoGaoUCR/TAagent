import os
import re
from typing import Any, Dict, List, Optional

import requests


class CanvasClient:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_token}"})

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        return resp

    def get_assignment(self, course_id: int, assignment_id: int) -> Dict[str, Any]:
        resp = self._get(f"/api/v1/courses/{course_id}/assignments/{assignment_id}")
        return resp.json()

    def list_submissions(self, course_id: int, assignment_id: int) -> List[Dict[str, Any]]:
        params = {
            "include[]": ["user", "attachments"],
            "per_page": 100,
        }
        submissions: List[Dict[str, Any]] = []
        next_url = f"{self.base_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions"
        while next_url:
            resp = self.session.get(next_url, params=params)
            resp.raise_for_status()
            submissions.extend(resp.json())
            next_url = _parse_next_link(resp.headers.get("Link", ""))
            params = None
        return submissions

    def download_attachment(self, attachment: Dict[str, Any], dest_dir: str) -> str:
        os.makedirs(dest_dir, exist_ok=True)
        url = attachment.get("url")
        filename = attachment.get("filename") or "submission.bin"
        path = os.path.join(dest_dir, filename)
        with self.session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return path


def _parse_next_link(link_header: str) -> Optional[str]:
    # Link: <url>; rel="next", <url>; rel="current"
    matches = re.findall(r"<([^>]+)>;\s*rel=\"([^\"]+)\"", link_header)
    for url, rel in matches:
        if rel == "next":
            return url
    return None
