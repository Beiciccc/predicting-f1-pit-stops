#!/usr/bin/env python3
"""Submit a queue of Kaggle files and wait for public scores after each upload."""

from __future__ import annotations

import csv
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd


COMPETITION = "playground-series-s6e5"
TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"


QUEUE = [
    ("submissions/s01_sohail_direct.csv", "loop01_s01_sohail_direct_public_rank"),
    ("submissions/s02_huzaifa_direct.csv", "loop02_s02_huzaifa_direct_public_rank"),
    ("submissions/s03_ravi_direct.csv", "loop03_s03_ravi_direct_public_rank"),
    ("submissions/s04_mikhail_direct.csv", "loop04_s04_mikhail_direct_public_rank"),
    ("submissions/s05_nina_sohail_rank_5050.csv", "loop05_s05_nina_sohail_rank_5050"),
    ("submissions/s06_public_strong_rank.csv", "loop06_s06_public_strong_rank"),
    ("submissions/s07_diverse_rank_all.csv", "loop07_s07_diverse_rank_all"),
    ("submissions/s08_hgb_sohail_nina_rank.csv", "loop08_s08_hgb_sohail_nina_rank"),
    ("submissions/s09_leon_small_diversifier.csv", "loop09_s09_leon_small_diversifier"),
    ("submissions/s10_realmlp_hgb_public_rank.csv", "loop10_s10_realmlp_hgb_public_rank"),
]


@dataclass
class SubmissionRow:
    file_name: str
    date: str
    description: str
    status: str
    public_score: str


def run(args: list[str]) -> str:
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n", flush=True)
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(args)}")
    return result.stdout


def submissions() -> list[SubmissionRow]:
    out = subprocess.check_output(
        ["kaggle", "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "50"],
        text=True,
    )
    rows = []
    for row in csv.DictReader(out.splitlines()):
        rows.append(
            SubmissionRow(
                row["fileName"],
                row["date"],
                row["description"],
                row["status"],
                row["publicScore"],
            )
        )
    return rows


def validate(path: Path) -> None:
    sample = pd.read_csv(SAMPLE)
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} has bad columns: {list(df.columns)}")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
        raise ValueError(f"{path} is not aligned with sample_submission")
    if not df[TARGET].between(-1e-12, 1 + 1e-12).all():
        raise ValueError(f"{path} predictions outside [0, 1]")
    if not df[TARGET].notna().all():
        raise ValueError(f"{path} contains NaN predictions")


def wait_for_result(description: str, start_seen_count: int, timeout_seconds: int = 900) -> SubmissionRow:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        rows = submissions()
        matches = [row for row in rows if row.description == description]
        if matches:
            row = matches[0]
            print(
                f"poll {datetime.now():%H:%M:%S}: {description} "
                f"status={row.status} publicScore={row.public_score or 'NA'}",
                flush=True,
            )
            if row.status.endswith(".COMPLETE") or row.status.endswith(".ERROR"):
                return row
        else:
            print(f"poll {datetime.now():%H:%M:%S}: waiting for list row {description}", flush=True)
        if len(rows) < start_seen_count:
            print("warning: submission list returned fewer rows than before", flush=True)
        time.sleep(30)
    raise TimeoutError(f"timed out waiting for {description}")


def main() -> int:
    before = submissions()
    print("Initial recent submissions:")
    for row in before[:10]:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")

    completed = []
    for index, (relative_path, description) in enumerate(QUEUE, start=1):
        path = ROOT / relative_path
        validate(path)
        print(f"\n=== loop {index}/10: {description} ===", flush=True)
        print(f"file={path}", flush=True)
        seen_count = len(submissions())
        try:
            run(["kaggle", "competitions", "submit", "-c", COMPETITION, "-f", str(path), "-m", description])
        except Exception as exc:
            print(f"submit command rejected for {description}: {exc}", flush=True)
            row = wait_for_result(description, seen_count, timeout_seconds=180)
        else:
            row = wait_for_result(description, seen_count)
        completed.append(row)
        if row.status.endswith(".ERROR"):
            print(f"loop {index} ended with ERROR; continuing after recorded failure analysis gate", flush=True)
        else:
            print(f"loop {index} complete: publicScore={row.public_score}", flush=True)

    print("\nCompleted queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
