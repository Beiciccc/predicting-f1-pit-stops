#!/usr/bin/env python3
"""Create the 2026-05-18 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round10"


SOURCES = {
    "s49": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/max/s49.csv",
    "lr46_02": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/max/lr46_02.csv",
    "r46_02": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/max/r46_02.csv",
    "r46_05": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/max/r46_05.csv",
    "d37_10": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/max/d37_10.csv",
    "hb49": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/max/hb49.csv",
    "c37": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/pro/c37.csv",
    "cc": ROOT / "public_outputs/raunak_blender_95449_20260518/outputs/pro/cc.csv",
    "giovanny": ROOT / "public_outputs/giovanny_95446_20260517/submission.csv",
    "mikhail": ROOT / "public_outputs/mikhail_latest_20260517/submission.csv",
}


DIRECT_QUEUE = [
    ("ab01_raunak_s49_direct", "s49"),
    ("ab02_raunak_lr46_02_direct", "lr46_02"),
    ("ab03_raunak_r46_02_direct", "r46_02"),
    ("ab04_raunak_r46_05_direct", "r46_05"),
    ("ab05_raunak_d37_10_direct", "d37_10"),
    ("ab06_raunak_hb49_direct", "hb49"),
    ("ab07_raunak_c37_direct", "c37"),
    ("ab08_raunak_cc_direct", "cc"),
]


RANK_BLEND_QUEUE = [
    ("ab09_rank_s49_giovanny_mikhail_80_15_05", {"s49": 0.80, "giovanny": 0.15, "mikhail": 0.05}),
    ("ab10_rank_s49_giovanny_mikhail_70_20_10", {"s49": 0.70, "giovanny": 0.20, "mikhail": 0.10}),
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


def rank_norm(values: pd.Series) -> np.ndarray:
    arr = values.to_numpy(dtype=float)
    return rankdata(arr, method="average") / len(arr)


def write_submission(name: str, pred: np.ndarray | pd.Series, sample: pd.DataFrame) -> Path:
    sub = sample.copy()
    sub[TARGET] = np.asarray(pred, dtype=float).clip(0, 1)
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

    anchor = preds["s49"].to_numpy()
    print("source,min,max,mean,std,corr_s49")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated,min,max,mean,std,corr_s49")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        print(describe(path, anchor))

    for name, weights in RANK_BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * rank_norm(preds[source])
        blended /= total
        final = rankdata(blended, method="average") / len(blended)
        path = write_submission(name, final, sample)
        print(describe(path, anchor))


if __name__ == "__main__":
    main()
