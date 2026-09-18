#!/usr/bin/env python3
"""Minimal PR01 completeness check (local stand-in for course-kit checker)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "pr01"
REPORT = ROOT / "report.json"

REQUIRED_EVIDENCE = (
    "doctor.txt",
    "graph.md",
    "environment.json",
    "pose-broken.txt",
    "pose-fixed.txt",
)

REQUIRED_FLAGS = (
    "public_tests_passed",
    "defect_reproduced",
    "defect_fixed",
)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def main() -> None:
    missing = [name for name in REQUIRED_EVIDENCE if not (EVIDENCE / name).is_file()]
    if missing:
        fail(f"missing evidence files: {', '.join(missing)}")

    try:
        env = json.loads((EVIDENCE / "environment.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"environment.json is not valid JSON: {exc}")

    for key in ("launch_method", "ros", "rmw", "domains"):
        if key not in env:
            fail(f"environment.json missing key: {key}")

    try:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"report.json is not valid JSON: {exc}")

    for key in REQUIRED_FLAGS:
        if key not in report:
            fail(f"report.json missing key: {key}")
        if not isinstance(report[key], bool):
            fail(f"report.json[{key}] must be boolean")

    if "tests" not in report or not isinstance(report["tests"], list) or not report["tests"]:
        fail("report.json.tests must be a non-empty list")

    doctor = (EVIDENCE / "doctor.txt").read_text(encoding="utf-8").strip()
    if len(doctor) < 40 or doctor.startswith("# Замените"):
        print("WARN: doctor.txt still looks like a stub — replace after ros2 doctor --report")

    print("OK: PR01 evidence layout and JSON look complete")
    print("Note: set report flags to true only after you run the live ROS checks.")


if __name__ == "__main__":
    main()
