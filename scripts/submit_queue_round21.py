#!/usr/bin/env python3
"""Submit the 2026-05-29 queue and wait for public scores."""

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
OUT = ROOT / "submissions_round21"
LIVE_RESULTS = ROOT / "docs" / "round21_live_results.csv"


QUEUE = [
    ("am01_sarvesh29_direct.csv", "r21_loop01_am01_sarvesh29_direct"),
    ("am02_rank_dr23_sarvesh29_98_02.csv", "r21_loop02_am02_rank_dr23_sarvesh29"),
    ("am03_rank_dr23_sarvesh29_95_05.csv", "r21_loop03_am03_rank_dr23_sarvesh29"),
    ("am04_rank_dr23_shamanth28_9995_0005.csv", "r21_loop04_am04_rank_dr23_shamanth28"),
    ("am05_rank_dr23_shamanth28_99_01.csv", "r21_loop05_am05_rank_dr23_shamanth28"),
    ("am06_rank_dr23_evridge29_98_02.csv", "r21_loop06_am06_rank_dr23_evridge29"),
    ("am07_rank_dr23_evtabm29_975_025.csv", "r21_loop07_am07_rank_dr23_evtabm29"),
    ("am08_rank_dr23_sarvesh29_99_01.csv", "r21_loop08_am08_rank_dr23_sarvesh29"),
    ("am09_rank_ai04_sarvesh29_99_01.csv", "r21_loop09_am09_rank_ai04_sarvesh29"),
    ("am10_rank_dr23_sarvesh29_parth29_985_010_005.csv", "r21_loop10_am10_rank_dr23_sarvesh29_parth29"),
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
    if exists:
        with LIVE_RESULTS.open(newline="") as f:
            for existing in csv.DictReader(f):
                if existing.get("description") == row.description:
                    return
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
        print(f"\n=== round21 loop {loop_idx}/10 already recorded: {description} {row.status} {row.public_score or 'NA'} ===", flush=True)
        record_live(loop_idx, rel, row)
        return row
    if existing:
        print(f"\n=== round21 loop {loop_idx}/10 already pending: {description} ===", flush=True)
        row = wait_for_result(description, timeout_seconds=900)
        print(f"loop {loop_idx} result: {row.status} {row.public_score or 'NA'}", flush=True)
        record_live(loop_idx, rel, row)
        return row

    print(f"\n=== round21 loop {loop_idx}/10: {description} ===", flush=True)
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

    print("\nCompleted round21 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
