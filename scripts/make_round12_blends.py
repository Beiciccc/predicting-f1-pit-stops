#!/usr/bin/env python3
"""Create the 2026-05-20 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round12"


SOURCES = {
    "s52_raw": ROOT / "public_outputs/raunak_blender_95452_20260520/outputs/max/s52_raw.csv",
    "lr52_46_01": ROOT / "public_outputs/raunak_blender_95452_20260520/outputs/max/lr52_46_01.csv",
    "lr52_46_02": ROOT / "public_outputs/raunak_blender_95452_20260520/outputs/max/lr52_46_02.csv",
    "d52_49_05": ROOT / "public_outputs/raunak_blender_95452_20260520/outputs/max/d52_49_05.csv",
    "max52_46_02": ROOT / "public_outputs/raunak_blender_95452_20260520/outputs/max/max52_46_02.csv",
    "pow52_49_10": ROOT / "public_outputs/raunak_blender_95452_20260520/outputs/max/pow52_49_10.csv",
    "harm52_46_02": ROOT / "public_outputs/mojjeed_advanced_20260520/outputs/max/harm52_46_02.csv",
    "geo52_46_02": ROOT / "public_outputs/mojjeed_advanced_20260520/outputs/max/geo52_46_02.csv",
    "srp52_46_001": ROOT / "public_outputs/mojjeed_advanced_20260520/outputs/max/srp52_46_001.csv",
    "gate52_49_top5": ROOT / "public_outputs/mojjeed_advanced_20260520/outputs/max/gate52_49_top5.csv",
}


QUEUE = [
    ("ad01_s52_raw_direct", "s52_raw"),
    ("ad02_lr52_46_01_direct", "lr52_46_01"),
    ("ad03_lr52_46_02_direct", "lr52_46_02"),
    ("ad04_d52_49_05_direct", "d52_49_05"),
    ("ad05_max52_46_02_direct", "max52_46_02"),
    ("ad06_pow52_49_10_direct", "pow52_49_10"),
    ("ad07_harm52_46_02_direct", "harm52_46_02"),
    ("ad08_geo52_46_02_direct", "geo52_46_02"),
    ("ad09_srp52_46_001_direct", "srp52_46_001"),
    ("ad10_gate52_49_top5_direct", "gate52_49_top5"),
]


def load_source(path: Path, sample: pd.DataFrame) -> pd.Series:
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} bad columns: {list(df.columns)}")
    if len(df) != len(sample):
        raise ValueError(f"{path} has wrong row count")
    if not df["id"].equals(sample["id"]):
        if df["id"].is_unique and set(df["id"]) == set(sample["id"]):
            df = df.set_index("id").loc[sample["id"]].reset_index()
        else:
            raise ValueError(f"{path} is not sample aligned")
    pred = df[TARGET].astype(float)
    if not np.isfinite(pred).all():
        raise ValueError(f"{path} non-finite predictions")
    return pred


def write_submission(name: str, pred: pd.Series, sample: pd.DataFrame) -> Path:
    sub = sample.copy()
    sub[TARGET] = pred.to_numpy(dtype=float).clip(0, 1)
    path = OUT / f"{name}.csv"
    sub.to_csv(path, index=False)
    return path


def describe(path: Path, anchor: np.ndarray) -> str:
    arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
    corr = np.corrcoef(anchor, arr)[0, 1]
    return f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}"


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}

    anchor = preds["s52_raw"].to_numpy()
    print("source,min,max,mean,std,corr_s52")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated,min,max,mean,std,corr_s52")
    for name, source in QUEUE:
        path = write_submission(name, preds[source], sample)
        print(describe(path, anchor))


if __name__ == "__main__":
    main()
