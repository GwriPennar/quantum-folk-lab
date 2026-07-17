"""Verify submission-critical public Build Week invariants."""

from __future__ import annotations

import json
import re
from pathlib import Path

from quantum_folk_lab.build_week import DEFAULT_OPENAI_MODEL, export_json, run_guided_exact
from quantum_folk_lab.build_week.models import RESULT_ENVELOPE_SCHEMA, ResultEnvelope

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "build-week"
REQUIRED = (
    ROOT / "README.md",
    DOCS / "JUDGING-GUIDE.md",
    DOCS / "BEFORE-AND-AFTER.md",
    DOCS / "ARCHITECTURE.md",
    DOCS / "CODEX-AND-GPT56-EVIDENCE.md",
    DOCS / "DEMO-SCRIPT.md",
    DOCS / "SUBMISSION-CHECKLIST.md",
    DOCS / "KNOWN-LIMITATIONS.md",
    ROOT / "examples" / "build-week" / "guided-experiment-example.json",
)


def main() -> int:
    failures: list[str] = []
    for path in REQUIRED:
        if not path.is_file():
            failures.append(f"missing: {path.relative_to(ROOT)}")

    envelope = run_guided_exact()
    round_trip = ResultEnvelope.from_dict(json.loads(export_json(envelope)))
    if round_trip.schema_version != RESULT_ENVELOPE_SCHEMA:
        failures.append("result-envelope schema mismatch")
    if DEFAULT_OPENAI_MODEL != "gpt-5.6-sol":
        failures.append("unexpected default OpenAI model")

    if REQUIRED[-1].is_file():
        example = json.loads(REQUIRED[-1].read_text(encoding="utf-8"))
        ResultEnvelope.from_dict(example)
        if example != envelope.to_dict():
            failures.append("example export is stale")

    public_text = "\n".join(
        path.read_text(encoding="utf-8") for path in REQUIRED[:-1] if path.is_file()
    )
    if re.search(r"C:\\Users\\|/Users/|private/", public_text):
        failures.append("private or absolute path in release documentation")
    for phrase in (
        "quantum advantage is demonstrated",
        "proves a speedup",
        "authentic folk families",
    ):
        if phrase in public_text.lower():
            failures.append(f"unsupported claim: {phrase}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "docs/build-week/JUDGING-GUIDE.md" not in readme:
        failures.append("README judging-guide link missing")
    if "OPENAI_" + "API" + "_KEY" in public_text:
        failures.append("credential variable embedded in documentation")

    if failures:
        print("Build Week release verification failed:")
        print("\n".join(failures))
        return 1
    print("Build Week release verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
