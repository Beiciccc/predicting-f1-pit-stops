#!/usr/bin/env python3
"""Submit the 2026-05-13 queue and wait for public scores."""

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
OUT = ROOT / "submissions_round7"


INITIAL_QUEUE = [
    ("y01_raunak_pow_tb_direct.csv", "r7_loop01_y01_raunak_pow_tb_direct"),
    ("y02_raunak_log_s18_direct.csv", "r7_loop02_y02_raunak_log_s18_direct"),
    ("y03_arun_blend_direct.csv", "r7_loop03_y03_arun_blend_direct"),
    ("y04_simarbir_direct.csv", "r7_loop04_y04_simarbir_direct"),
    ("y05_degnonguidi12_direct.csv", "r7_loop05_y05_degnonguidi12_direct"),
]


FRESH_GOOD_QUEUE = [
    ("y06_anthony_res_direct.csv", "r7_loop06_y06_anthony_res_direct"),
    ("y08_rank_s19_simarbir_95_05.csv", "r7_loop07_y08_rank_s19_simarbir_95_05"),
    ("y09_rank_s19_deg12_97_03.csv", "r7_loop08_y09_rank_s19_deg12_97_03"),
    ("y10_rank_s19_sim_deg_arun_90_05_03_02.csv", "r7_loop09_y10_rank_s19_sim_deg_arun"),
    ("y11_rank_s19_joseph_97_03.csv", "r7_loop10_y11_rank_s19_joseph_97_03"),
]


FALLBACK_QUEUE = [
    ("y06_anthony_res_direct.csv", "r7_loop06_y06_anthony_res_direct"),
    ("y07_rank_s19_arun_80_20.csv", "r7_loop07_y07_rank_s19_arun_80_20"),
    ("y11_rank_s19_joseph_97_03.csv", "r7_loop08_y11_rank_s19_joseph_97_03"),
    ("y12_rank_s19_nikita_97_03.csv", "r7_loop09_y12_rank_s19_nikita_97_03"),
    ("y13_rank_s19_sarvesh_99_01.csv", "r7_loop10_y13_rank_s19_sarvesh_99_01"),
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
                ["kaggle", "competitions", "submissions", "-c", COMPETITION, "-v", "--page-size", "40"],
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
        print(f"\n=== round7 loop {loop_idx}/10 already recorded: {description} {row.status} {row.public_score or 'NA'} ===", flush=True)
        return row
    print(f"\n=== round7 loop {loop_idx}/10: {description} ===", flush=True)
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

    simarbir = completed[-2]
    degnonguidi = completed[-1]
    simarbir_score = score_value(simarbir)
    degnonguidi_score = score_value(degnonguidi)
    if (
        simarbir.status.endswith(".COMPLETE")
        and degnonguidi.status.endswith(".COMPLETE")
        and simarbir_score >= 0.95418
        and degnonguidi_score >= 0.95418
    ):
        print("rule: fresh direct probes are close enough; using fresh-output small-rank probes", flush=True)
        final_queue = FRESH_GOOD_QUEUE
    else:
        print("rule: a fresh direct probe failed the close-anchor threshold; using conservative fallback probes", flush=True)
        final_queue = FALLBACK_QUEUE

    for idx, (rel, description) in enumerate(final_queue, 6):
        completed.append(submit_one(idx, rel, description))

    print("\nCompleted round7 queue:")
    for row in completed:
        print(f"{row.date},{row.description},{row.status},{row.public_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
