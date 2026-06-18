#!/usr/bin/env python3
"""Deterministic statute verifier — thin, offline-by-default wrapper over normattiva_fetch.

`normattiva_fetch.py` already fetches the official article text from Normattiva,
confirms the article marker and vigency, and emits a report-compatible record
(statuses verified / mismatch / not_found / unavailable / unsupported). This
wrapper wires that verification into the pipeline as an explicit step with a
strict network gate:

  - OFFLINE BY DEFAULT: it only reads article HTML/TXT already present in
    --articles-dir. No network call is made unless --allow-network is passed.
  - --allow-network honours the skill's route/privacy gate: a live Normattiva
    fetch is performed only when the user has approved the sources route.

The verifier confirms EXISTENCE and VIGENCY of the statute text, NOT the legal
relevance of how the candidate answer used it. Output is the same envelope as
`normattiva_fetch.run`, so it merges through `legal_panel.py report --sources`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import normattiva_fetch


def verify_statutes(
    *,
    sources_path: Path | None,
    cases_path: Path | None,
    articles_dir: Path,
    allow_network: bool,
    timeout: int = 40,
    sleep: float = 0.25,
    force: bool = False,
) -> dict[str, Any]:
    """Run normattiva_fetch in offline (default) or live mode and return its envelope."""
    args = SimpleNamespace(
        sources=str(sources_path) if sources_path else None,
        cases=str(cases_path) if cases_path else None,
        articles_dir=str(articles_dir),
        timeout=timeout,
        sleep=sleep,
        no_network=not allow_network,
        force=force,
    )
    return normattiva_fetch.run(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sources", help="source-verification JSON from legal_panel.py verify-sources.")
    group.add_argument("--cases", help="panel-input/cases JSON from extract or prepare-live.")
    parser.add_argument("--articles-dir", default="normattiva-articles", help="Directory with (cached or to-download) article files.")
    parser.add_argument(
        "--allow-network",
        action="store_true",
        help="Perform live Normattiva fetches. Requires the sources route to be approved. "
        "Without this flag the wrapper stays OFFLINE and only reads cached files.",
    )
    parser.add_argument("--timeout", type=int, default=40, help="HTTP timeout in seconds (live mode only).")
    parser.add_argument("--sleep", type=float, default=0.25, help="Delay between live requests (live mode only).")
    parser.add_argument("--force", action="store_true", help="Allow overwriting generated files.")
    parser.add_argument("--output", help="Write the verification JSON here (default: stdout).")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = verify_statutes(
        sources_path=Path(args.sources) if args.sources else None,
        cases_path=Path(args.cases) if args.cases else None,
        articles_dir=Path(args.articles_dir),
        allow_network=args.allow_network,
        timeout=args.timeout,
        sleep=args.sleep,
        force=args.force,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(json.dumps({
            "output": args.output,
            "status": result["status"],
            "mode": "live" if args.allow_network else "offline",
        }, ensure_ascii=False))
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
