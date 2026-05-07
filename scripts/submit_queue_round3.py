#!/usr/bin/env python3
"""Submit the 2026-05-07 queue and wait for scores."""

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
    ("submissions_round3/u01_flexon_tb.csv", "r3_loop01_u01_flexon_tb_known_95410"),
    ("submissions_round3/u02_flexon_h01.csv", "r3_loop02_u02_flexon_h01"),
    ("submissions_round3/u03_flexon_h02.csv", "r3_loop03_u03_flexon_h02"),
    ("submissions_round3/u04_flexon_t95.csv", "r3_loop04_u04_flexon_t95"),
    ("submissions_round3/u05_flexon_t85.csv", "r3_loop05_u05_flexon_t85"),
    ("submissions_round3/u06_flexon_hm1.csv", "r3_loop06_u06_flexon_hm1"),
    ("submissions_round3/u07_flexon_hm2.csv", "r3_loop07_u07_flexon_hm2"),
    ("submissions_round3/u08_nina_hb4.csv", "r3_loop08_u08_nina_hb4"),
    ("submissions_round3/u09_sohail_95407.csv", "r3_loop09_u09_sohail_95407"),
    ("submissions_round3/u10_mikhail_updated.csv", "r3_loop10_u10_mikhail_updated"),
]


@dataclass
class SubmissionRow:
    file_name: str
    date: str
    description: str
    status: str
    public_score: str


def submissions() -> list[SubmissionRow]:
    out = subprocess.check_output(
        ["kaggle", "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "90"],
        text=True,
    )
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
    if not df[TARGET].between(-1e-12, 1 + 1e-12).all() or not df[TARGET].notna().all():
        raise ValueError(f"{path} invalid predictions")


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


def main() -> int:
    print("Initial recent submissions:")
    for row in submissions()[:15]:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")

    completed = []
    for idx, (rel, description) in enumerate(QUEUE, 1):
        path = ROOT / rel
        validate(path)
        print(f"\n=== round3 loop {idx}/10: {description} ===", flush=True)
        result = subprocess.run(
            ["kaggle", "competitions", "submit", "-c", COMPETITION, "-f", str(path), "-m", description],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(result.stdout, flush=True)
        if result.returncode != 0:
            print(f"submit rejected: {description}", flush=True)
        row = wait_for_result(description, timeout_seconds=900 if result.returncode == 0 else 180)
        completed.append(row)
        print(f"loop {idx} result: {row.status} {row.public_score or 'NA'}", flush=True)

    print("\nCompleted round3 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
