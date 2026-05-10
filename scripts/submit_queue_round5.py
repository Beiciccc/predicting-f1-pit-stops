#!/usr/bin/env python3
"""Submit the 2026-05-11 queue and wait for public scores."""

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
    ("submissions_round5/w01_flex_s19_direct.csv", "r5_loop01_w01_flex_s19_direct"),
    ("submissions_round5/w02_flex_d02_direct.csv", "r5_loop02_w02_flex_d02_direct"),
    ("submissions_round5/w03_flex_rtb02_direct.csv", "r5_loop03_w03_flex_rtb02_direct"),
    ("submissions_round5/w04_flex_cs02_direct.csv", "r5_loop04_w04_flex_cs02_direct"),
    ("submissions_round5/w05_raunak_log_s11_direct.csv", "r5_loop05_w05_raunak_log_s11_direct"),
    ("submissions_round5/w06_raunak_geo_s11_direct.csv", "r5_loop06_w06_raunak_geo_s11_direct"),
    ("submissions_round5/w07_nina_hb5_direct.csv", "r5_loop07_w07_nina_hb5_direct"),
    ("submissions_round5/w08_abd_s18_direct.csv", "r5_loop08_w08_abd_s18_direct"),
    ("submissions_round5/w09_masaya_mlp32_direct.csv", "r5_loop09_w09_masaya_mlp32_direct"),
    ("submissions_round5/w10_rank_s19_masaya_gkanamoto.csv", "r5_loop10_w10_rank_s19_masaya_gkanamoto"),
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
    pred = df[TARGET]
    if not pred.between(-1e-12, 1 + 1e-12).all() or not pred.notna().all():
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
    for row in submissions()[:20]:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")

    completed = []
    for idx, (rel, description) in enumerate(QUEUE, 1):
        path = ROOT / rel
        validate(path)
        print(f"\n=== round5 loop {idx}/10: {description} ===", flush=True)
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

    print("\nCompleted round5 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
