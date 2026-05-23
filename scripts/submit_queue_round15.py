#!/usr/bin/env python3
"""Submit the 2026-05-23 queue and wait for public scores."""

from __future__ import annotations

import csv
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


COMPETITION = "playground-series-s6e5"
TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round15"
LIVE_RESULTS = ROOT / "docs" / "round15_live_results.csv"


QUEUE = [
    ("ag01_anthony_20260523_direct.csv", "r15_loop01_ag01_anthony_20260523"),
    ("ag02_dataregressor_20260523_direct.csv", "r15_loop02_ag02_dataregressor_20260523"),
    ("ag03_prob_max52_anth23_995_005.csv", "r15_loop03_ag03_prob_max52_anth23"),
    ("ag04_prob_s53_anth23_995_005.csv", "r15_loop04_ag04_prob_s53_anth23"),
    ("ag05_prob_tail53_anth23_995_005.csv", "r15_loop05_ag05_prob_tail53_anth23"),
    ("ag06_rank_max52_anth23_995_005.csv", "r15_loop06_ag06_rank_max52_anth23"),
    ("ag07_rank_s53_anth23_995_005.csv", "r15_loop07_ag07_rank_s53_anth23"),
    ("ag08_prob_anth23_yekenot_pytab_995_005.csv", "r15_loop08_ag08_prob_anth23_yekenot"),
    ("ag09_rank_anth23_yekenot_pytab_995_005.csv", "r15_loop09_ag09_rank_anth23_yekenot"),
    ("ag10_mirza_sub8_optuna_direct.csv", "r15_loop10_ag10_mirza_sub8_optuna"),
]


@dataclass
class SubmissionRow:
    file_name: str
    date: str
    description: str
    status: str
    public_score: str


def submissions() -> list[SubmissionRow]:
    last_error: Exception | None = None
    for attempt in range(1, 6):
        try:
            out = subprocess.check_output(
                ["kaggle", "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "140"],
                text=True,
                stderr=subprocess.STDOUT,
                timeout=90,
            )
            break
        except Exception as exc:
            last_error = exc
            print(f"submissions retry {attempt}/5: {exc}", flush=True)
            time.sleep(20)
    else:
        raise RuntimeError("could not fetch submissions") from last_error
    return [
        SubmissionRow(row["fileName"], row["date"], row["description"], row["status"], row["publicScore"])
        for row in csv.DictReader(out.splitlines())
    ]


def validate(path: Path) -> None:
    sample = pd.read_csv(SAMPLE)
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} bad columns")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
        raise ValueError(f"{path} is not sample aligned")
    pred = df[TARGET]
    if not pred.between(-1e-12, 1 + 1e-12).all() or not pred.notna().all():
        raise ValueError(f"{path} invalid predictions")


def record_live(loop_idx: int, rel: str, row: SubmissionRow) -> None:
    exists = LIVE_RESULTS.exists()
    with LIVE_RESULTS.open("a", newline="") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["recorded_at_utc", "loop", "file", "description", "status", "public_score", "kaggle_date"])
        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
                loop_idx,
                rel,
                row.description,
                row.status,
                row.public_score,
                row.date,
            ]
        )


def wait_for_result(description: str, timeout_seconds: int = 900) -> SubmissionRow:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        matches = [row for row in submissions() if row.description == description]
        if matches:
            row = matches[0]
            print(f"poll {datetime.now():%H:%M:%S}: {description} {row.status} {row.public_score or 'NA'}", flush=True)
            if row.status.endswith(".COMPLETE") or row.status.endswith(".ERROR"):
                return row
        else:
            print(f"poll {datetime.now():%H:%M:%S}: waiting for list row {description}", flush=True)
        time.sleep(30)
    raise TimeoutError(description)


def submit_one(loop_idx: int, rel: str, description: str) -> SubmissionRow:
    path = OUT / rel
    validate(path)
    existing = [row for row in submissions() if row.description == description]
    if existing and (existing[0].status.endswith(".COMPLETE") or existing[0].status.endswith(".ERROR")):
        row = existing[0]
        print(f"\n=== round15 loop {loop_idx}/10 already recorded: {description} {row.status} {row.public_score or 'NA'} ===", flush=True)
        record_live(loop_idx, rel, row)
        return row

    print(f"\n=== round15 loop {loop_idx}/10: {description} ===", flush=True)
    returncode = 1
    for attempt in range(1, 4):
        result = subprocess.run(
            ["kaggle", "competitions", "submit", "-c", COMPETITION, "-f", str(path), "-m", description],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=240,
        )
        returncode = result.returncode
        print(result.stdout, flush=True)
        if returncode == 0:
            break
        existing = [row for row in submissions() if row.description == description]
        if existing:
            break
        print(f"submit attempt {attempt}/3 failed before a list row appeared: {description}", flush=True)
        time.sleep(30)
    if returncode != 0:
        print(f"submit command did not return success; using submission list as source of truth: {description}", flush=True)
    row = wait_for_result(description, timeout_seconds=900 if returncode == 0 else 240)
    print(f"loop {loop_idx} result: {row.status} {row.public_score or 'NA'}", flush=True)
    record_live(loop_idx, rel, row)
    return row


def main() -> int:
    print("Initial recent submissions:")
    for row in submissions()[:25]:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")

    completed: list[SubmissionRow] = []
    for idx, (rel, description) in enumerate(QUEUE, 1):
        completed.append(submit_one(idx, rel, description))

    print("\nCompleted round15 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
