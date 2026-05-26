#!/usr/bin/env python3
"""Submit the 2026-05-26 queue and wait for public scores."""

from __future__ import annotations

import csv
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


KAGGLE = "/opt/anaconda3/bin/kaggle"
COMPETITION = "playground-series-s6e5"
TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round18"
LIVE_RESULTS = ROOT / "docs" / "round18_live_results.csv"


QUEUE = [
    ("aj01_rank_dr23_yek26_995_005.csv", "r18_loop01_aj01_rank_dr23_yek26"),
    ("aj02_rank_dr23_yek26_99_01.csv", "r18_loop02_aj02_rank_dr23_yek26"),
    ("aj03_rank_dr23_yek26_98_02.csv", "r18_loop03_aj03_rank_dr23_yek26"),
    ("aj04_rank_dr23_ruihao_cpu_995_005.csv", "r18_loop04_aj04_rank_dr23_ruihao_cpu"),
    ("aj05_rank_dr23_ruihao_cpu_99_01.csv", "r18_loop05_aj05_rank_dr23_ruihao_cpu"),
    ("aj06_rank_dr23_yek26_cpu_990_005_005.csv", "r18_loop06_aj06_rank_dr23_yek26_cpu"),
    ("aj07_prob_dr23_yek26_999_001.csv", "r18_loop07_aj07_prob_dr23_yek26"),
    ("aj08_rank_ai04_yek26_995_005.csv", "r18_loop08_aj08_rank_ai04_yek26"),
    ("aj09_rank_ah10_yek26_cpu_lz_990_005_003_002.csv", "r18_loop09_aj09_rank_ah10_yek_cpu_lz"),
    ("aj10_rank_dr23_meta_full_999_001.csv", "r18_loop10_aj10_rank_dr23_meta_full"),
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
                [KAGGLE, "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "200"],
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
        print(f"\n=== round18 loop {loop_idx}/10 already recorded: {description} {row.status} {row.public_score or 'NA'} ===", flush=True)
        record_live(loop_idx, rel, row)
        return row

    print(f"\n=== round18 loop {loop_idx}/10: {description} ===", flush=True)
    returncode = 1
    for attempt in range(1, 4):
        result = subprocess.run(
            [KAGGLE, "competitions", "submit", "-c", COMPETITION, "-f", str(path), "-m", description],
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

    print("\nCompleted round18 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
