#!/usr/bin/env python3
"""Submit the 2026-05-06 Kaggle queue and wait for scores."""

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
    ("submissions_round2/t01_mojjeed_direct.csv", "r2_loop01_t01_mojjeed_direct"),
    ("submissions_round2/t02_pilkwang_stack_direct.csv", "r2_loop02_t02_pilkwang_stack_direct"),
    ("submissions_round2/t03_oof_rank_moj40_pilk30_yek30.csv", "r2_loop03_t03_oof_rank_moj40_pilk30_yek30"),
    ("submissions_round2/t04_oof_rank_moj50_pilk30_yek20.csv", "r2_loop04_t04_oof_rank_moj50_pilk30_yek20"),
    ("submissions_round2/t05_oof_rank_moj35_pilk35_yek30.csv", "r2_loop05_t05_oof_rank_moj35_pilk35_yek30"),
    ("submissions_round2/t06_pilkwang_learner_rank.csv", "r2_loop06_t06_pilkwang_learner_rank"),
    ("submissions_round2/t07_roman_v8_solo_direct.csv", "r2_loop07_t07_roman_v8_solo_direct"),
    ("submissions_round2/t08_rank_moj50_romanv8_25_sohail25.csv", "r2_loop08_t08_rank_moj50_romanv8_25_sohail25"),
    ("submissions_round2/t09_rank_sohail35_moj30_pilk25_leon10.csv", "r2_loop09_t09_rank_sohail35_moj30_pilk25_leon10"),
    ("submissions_round2/t10_rank_moj40_pilk25_mikhail15_hgb10_leon10.csv", "r2_loop10_t10_rank_moj40_pilk25_mikhail15_hgb10_leon10"),
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
        ["kaggle", "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "80"],
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
        raise ValueError(f"{path} bad columns: {list(df.columns)}")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
        raise ValueError(f"{path} is not sample aligned")
    if not df[TARGET].between(-1e-12, 1 + 1e-12).all() or not df[TARGET].notna().all():
        raise ValueError(f"{path} has invalid predictions")


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
        print(f"\n=== round2 loop {idx}/10: {description} ===", flush=True)
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

    print("\nCompleted round2 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
