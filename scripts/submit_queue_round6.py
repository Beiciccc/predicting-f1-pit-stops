#!/usr/bin/env python3
"""Submit the 2026-05-12 queue and wait for public scores."""

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
OUT = ROOT / "submissions_round6"


INITIAL_QUEUE = [
    ("x01_flex_ex02_direct.csv", "r6_loop01_x01_flex_ex02_direct"),
    ("x02_flex_cdn02_direct.csv", "r6_loop02_x02_flex_cdn02_direct"),
    ("x03_flex_cup02_direct.csv", "r6_loop03_x03_flex_cup02_direct"),
    ("x04_flex_d01_direct.csv", "r6_loop04_x04_flex_d01_direct"),
    ("x05_rank_s19_nina_geo_72_16_12.csv", "r6_loop05_x05_rank_s19_nina_geo"),
    ("x06_rank_s19_log_geo_nina_70_10_10_10.csv", "r6_loop06_x06_rank_s19_log_geo_nina"),
    ("x07_mikhail_0512_direct.csv", "r6_loop07_x07_mikhail_0512_direct"),
]


MIKHAIL_QUEUE = [
    ("x13_rank_s19_mikhail_95_05.csv", "r6_loop08_x13_rank_s19_mikhail_95_05"),
    ("x14_rank_s19_mikhail_90_10.csv", "r6_loop09_x14_rank_s19_mikhail_90_10"),
    ("x15_rank_s19_mikhail_nikita_86_10_04.csv", "r6_loop10_x15_rank_s19_mikhail_nikita"),
]


FALLBACK_QUEUE = [
    ("x08_flex_rs11_direct.csv", "r6_loop08_x08_flex_rs11_direct"),
    ("x09_flex_t02_direct.csv", "r6_loop09_x09_flex_t02_direct"),
    ("x10_raunak_log_tb_direct.csv", "r6_loop10_x10_raunak_log_tb_direct"),
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
        ["kaggle", "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "120"],
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


def submit_one(loop_idx: int, rel: str, description: str) -> SubmissionRow:
    path = OUT / rel
    validate(path)
    print(f"\n=== round6 loop {loop_idx}/10: {description} ===", flush=True)
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
    print(f"loop {loop_idx} result: {row.status} {row.public_score or 'NA'}", flush=True)
    return row


def score_value(row: SubmissionRow) -> float:
    try:
        return float(row.public_score)
    except ValueError:
        return float("nan")


def main() -> int:
    print("Initial recent submissions:")
    for row in submissions()[:25]:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")

    completed: list[SubmissionRow] = []
    for idx, (rel, description) in enumerate(INITIAL_QUEUE, 1):
        completed.append(submit_one(idx, rel, description))

    mikhail = completed[-1]
    mikhail_score = score_value(mikhail)
    if mikhail.status.endswith(".COMPLETE") and mikhail_score >= 0.95419:
        print("rule: new Mikhail output matched/exceeded current anchor; using Mikhail-centered final probes", flush=True)
        final_queue = MIKHAIL_QUEUE
    else:
        print("rule: new Mikhail output failed anchor threshold; using s19-family fallback probes", flush=True)
        final_queue = FALLBACK_QUEUE

    for idx, (rel, description) in enumerate(final_queue, 8):
        completed.append(submit_one(idx, rel, description))

    print("\nCompleted round6 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
