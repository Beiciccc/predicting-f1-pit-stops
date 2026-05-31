#!/usr/bin/env python3
"""Submit selected 2026-05-31 candidates and wait for public scores."""

from __future__ import annotations

import argparse
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
OUT = ROOT / "submissions_round23"
LIVE_RESULTS = ROOT / "docs" / "round23_live_results.csv"


QUEUE = [
    ("ao01_rank_dr23_kk31_999_001.csv", "r23_loop01_ao01_rank_dr23_kk31"),
    ("ao02_rank_dr23_kk31_995_005.csv", "r23_loop02_ao02_rank_dr23_kk31"),
    ("ao03_rank_dr23_emanuell31_999_001.csv", "r23_loop03_ao03_rank_dr23_emanuell31"),
    ("ao04_rank_dr23_evgen30_999_001.csv", "r23_loop04_ao04_rank_dr23_evgen30"),
    ("ao05_rank_dr23_masaya_l2_999_001.csv", "r23_loop05_ao05_rank_dr23_masaya_l2"),
    ("ao06_rank_dr23_parth30_999_001.csv", "r23_loop06_ao06_rank_dr23_parth30"),
    ("ao07_rank_s54_kk31_999_001.csv", "r23_loop07_ao07_rank_s54_kk31"),
    ("ao08_rank_dr23_consensus31_996_002_001_001.csv", "r23_loop08_ao08_rank_dr23_consensus31"),
    ("ao09_rank_dr23_teyrsp_999_001.csv", "r23_loop09_ao09_rank_dr23_teyrsp"),
    ("ao10_rank_dr23_jeffrank30_999_001.csv", "r23_loop10_ao10_rank_dr23_jeffrank30"),
    ("ao11_prob_dr23_an09_s54_equal.csv", "r23_loop11_ao11_prob_dr23_an09_s54_equal"),
    ("ao12_rank_dr23_kk_emanuell_masaya_997_001_001_001.csv", "r23_loop12_ao12_rank_dr23_kk_emanuell_masaya"),
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
                [KAGGLE, "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "300"],
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
        print(f"\n=== round23 loop {loop_idx}/10 already recorded: {description} {row.status} {row.public_score or 'NA'} ===", flush=True)
        record_live(loop_idx, rel, row)
        return row
    if existing:
        print(f"\n=== round23 loop {loop_idx}/10 already pending: {description} ===", flush=True)
        row = wait_for_result(description, timeout_seconds=900)
        print(f"loop {loop_idx} result: {row.status} {row.public_score or 'NA'}", flush=True)
        record_live(loop_idx, rel, row)
        return row

    print(f"\n=== round23 loop {loop_idx}/10: {description} ===", flush=True)
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


def selected_queue(args: argparse.Namespace) -> list[tuple[int, str, str]]:
    indexed = [(idx, rel, desc) for idx, (rel, desc) in enumerate(QUEUE, 1)]
    if args.only:
        want = {int(item) for item in args.only.split(",")}
        indexed = [item for item in indexed if item[0] in want]
    if args.start:
        indexed = [item for item in indexed if item[0] >= args.start]
    if args.limit is not None:
        indexed = indexed[: args.limit]
    return indexed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--only", help="comma-separated 1-based queue indexes")
    args = parser.parse_args()

    queue = selected_queue(args)
    print("Initial recent submissions:")
    for row in submissions()[:25]:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")

    completed: list[SubmissionRow] = []
    for idx, rel, description in queue:
        completed.append(submit_one(idx, rel, description))

    print("\nCompleted selected round23 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
