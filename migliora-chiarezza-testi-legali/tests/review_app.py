#!/usr/bin/env python3
"""Interfaccia locale per la revisione umana dei casi di chiarezza legale."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from clarity_eval import DEFAULT_CASES, EvalResult, evaluate_output, load_cases


BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "review_app.html"
DEFAULT_RAW_DIR = Path("/private/tmp/skill-legali-opus-glm-eval")
DEFAULT_REVIEW_PATH = BASE_DIR / "human_reviews.json"
MODELS = (
    {"id": "opus", "label": "Opus locale"},
    {"id": "glm52", "label": "GLM 5.2"},
)
PRIORITY_CASES = {"C002", "C007", "C009", "C010", "C011", "C012"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def item_to_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        if "description" in item:
            prefix = item.get("code")
            severity = item.get("severity")
            chunks = [str(item["description"])]
            if prefix or severity:
                chunks.append(f"({prefix or 'senza codice'}, severita': {severity or 'n.d.'})")
            return " ".join(chunks)
        if "text" in item:
            label = item.get("label")
            return f"{label}: {item['text']}" if label else str(item["text"])
    return json.dumps(item, ensure_ascii=False)


def list_to_text(items: Any) -> list[str]:
    if not isinstance(items, list):
        return [item_to_text(items)] if items else []
    return [item_to_text(item) for item in items]


def case_for_review(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": case["id"],
        "title": case["title"],
        "document_type": case["document_type"],
        "input_text": case["input_text"],
        "adjudication_status": case["adjudication_status"],
        "expected_issues": list_to_text(case.get("expected_issues")),
        "legal_invariants": list_to_text(case.get("legal_invariants")),
        "forbidden_changes": list_to_text(case.get("forbidden_changes")),
        "acceptable_rewrites": list_to_text(case.get("acceptable_rewrites")),
        "human_notes": case.get("human_notes", ""),
        "validation_rationale": case.get("validation_rationale", ""),
        "priority": case["id"] in PRIORITY_CASES,
    }


def missing_output(model_id: str, case_id: str, path: Path) -> dict[str, Any]:
    return {
        "model": model_id,
        "case_id": case_id,
        "path": str(path),
        "available": False,
        "output": "",
        "duration_s": None,
        "returncode": None,
        "automatic_check": EvalResult(case_id=case_id, fatal_failures=["Output non trovato."]).as_dict(),
        "stderr": "",
    }


def load_model_output(case: dict[str, Any], model_id: str, raw_dir: Path) -> dict[str, Any]:
    path = raw_dir / f"{model_id}_{case['id']}.json"
    if not path.exists():
        return missing_output(model_id, case["id"], path)

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = EvalResult(case_id=case["id"], fatal_failures=[f"Output non leggibile: {exc}"])
        return {
            "model": model_id,
            "case_id": case["id"],
            "path": str(path),
            "available": False,
            "output": "",
            "duration_s": None,
            "returncode": None,
            "automatic_check": result.as_dict(),
            "stderr": "",
        }

    output = str(payload.get("output", ""))
    automatic = evaluate_output(case, output).as_dict() if output else EvalResult(
        case_id=case["id"], fatal_failures=["Output vuoto."]
    ).as_dict()
    return {
        "model": model_id,
        "case_id": case["id"],
        "path": str(path),
        "available": True,
        "output": output,
        "duration_s": payload.get("duration_s"),
        "returncode": payload.get("returncode"),
        "automatic_check": automatic,
        "stderr": payload.get("stderr", ""),
    }


def build_review_data(
    cases_path: Path = DEFAULT_CASES,
    raw_dir: Path = DEFAULT_RAW_DIR,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> dict[str, Any]:
    cases = load_cases(cases_path)
    outputs: dict[str, dict[str, Any]] = {}
    for case in cases:
        outputs[case["id"]] = {
            model["id"]: load_model_output(case, model["id"], raw_dir)
            for model in MODELS
        }

    return {
        "created_at": utc_now(),
        "cases_path": str(cases_path),
        "raw_dir": str(raw_dir),
        "review_path": str(review_path),
        "models": MODELS,
        "priority_cases": sorted(PRIORITY_CASES),
        "cases": [case_for_review(case) for case in cases],
        "outputs": outputs,
        "status_options": [
            {"value": "", "label": "Da decidere"},
            {"value": "gold", "label": "Gold"},
            {"value": "ambiguous", "label": "Ambiguo"},
            {"value": "expert_review_only", "label": "Solo revisione esperta"},
            {"value": "rewrite", "label": "Da riscrivere"},
        ],
    }


def load_reviews(review_path: Path = DEFAULT_REVIEW_PATH) -> dict[str, Any]:
    if not review_path.exists():
        return {"version": 1, "updated_at": None, "reviews": {}}
    with review_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("reviews"), dict):
        raise ValueError("human_reviews.json non contiene una revisione valida.")
    payload.setdefault("version", 1)
    payload.setdefault("updated_at", None)
    return payload


def save_reviews(payload: dict[str, Any], review_path: Path = DEFAULT_REVIEW_PATH) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("La revisione deve essere un oggetto JSON.")
    reviews = payload.get("reviews")
    if not isinstance(reviews, dict):
        raise ValueError("Campo reviews mancante o non valido.")

    data = {
        "version": 1,
        "updated_at": utc_now(),
        "reviews": reviews,
    }
    review_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = review_path.with_suffix(review_path.suffix + ".tmp")
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(review_path)
    return data


class ReviewHandler(BaseHTTPRequestHandler):
    server_version = "ClarityReview/1.0"

    @property
    def raw_dir(self) -> Path:
        return self.server.raw_dir  # type: ignore[attr-defined]

    @property
    def review_path(self) -> Path:
        return self.server.review_path  # type: ignore[attr-defined]

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, status: HTTPStatus = HTTPStatus.OK, content_type: str = "text/html") -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message: str, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> None:
        self.send_json({"error": message}, status)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path in {"/", "/index.html"}:
                self.send_text(HTML_PATH.read_text(encoding="utf-8"))
                return
            if path == "/api/review-data":
                self.send_json(build_review_data(raw_dir=self.raw_dir, review_path=self.review_path))
                return
            if path == "/api/reviews":
                self.send_json(load_reviews(self.review_path))
                return
            self.send_error_json("Risorsa non trovata.", HTTPStatus.NOT_FOUND)
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self.send_error_json(str(exc), HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/reviews":
            self.send_error_json("Risorsa non trovata.", HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            self.send_json(save_reviews(payload, self.review_path))
        except Exception as exc:  # pragma: no cover - defensive HTTP boundary
            self.send_error_json(str(exc), HTTPStatus.BAD_REQUEST)


def run_server(host: str, port: int, raw_dir: Path, review_path: Path) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), ReviewHandler)
    server.raw_dir = raw_dir  # type: ignore[attr-defined]
    server.review_path = review_path  # type: ignore[attr-defined]
    return server


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("CLARITY_REVIEW_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("CLARITY_REVIEW_PORT", "8791")))
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path(os.environ.get("CLARITY_REVIEW_RAW_DIR", str(DEFAULT_RAW_DIR))),
        help="Cartella con i file opus_C001.json e glm52_C001.json.",
    )
    parser.add_argument(
        "--reviews",
        type=Path,
        default=Path(os.environ.get("CLARITY_REVIEW_FILE", str(DEFAULT_REVIEW_PATH))),
        help="File in cui salvare la revisione umana.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    server = run_server(args.host, args.port, args.raw_dir, args.reviews)
    print(f"Review app: http://{args.host}:{args.port}/")
    print(f"Output modelli: {args.raw_dir}")
    print(f"File revisione: {args.reviews}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
