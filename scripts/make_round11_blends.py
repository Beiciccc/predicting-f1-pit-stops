#!/usr/bin/env python3
"""Create the 2026-05-19 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round11"


SOURCES = {
    "s49": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/max/s49.csv",
    "max46_05": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/max/max46_05.csv",
    "max31_05": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/max/max31_05.csv",
    "ex37": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/pro/ex37.csv",
    "r37_05": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/pro/r37_05.csv",
    "d31_05": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/pro/d31_05.csv",
    "d37_05": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/pro/d37_05.csv",
    "min31_05": ROOT / "public_outputs/raunak_blender_95450_20260519/outputs/pro/min31_05.csv",
    "dataregressor": ROOT / "public_outputs/dataregressor_knock_20260519/submission.csv",
    "nina_hb11": ROOT / "public_outputs/nina_hb11_20260519/submission.csv",
    "giovanny": ROOT / "public_outputs/giovanny_95446_20260517/submission.csv",
    "mikhail": ROOT / "public_outputs/mikhail_latest_20260519/submission.csv",
}


DIRECT_QUEUE = [
    ("ac01_raunak_max46_05_direct", "max46_05"),
    ("ac02_dataregressor_knock_direct", "dataregressor"),
    ("ac03_nina_hb11_direct", "nina_hb11"),
    ("ac04_raunak_max31_05_direct", "max31_05"),
    ("ac05_raunak_ex37_direct", "ex37"),
    ("ac06_raunak_r37_05_direct", "r37_05"),
    ("ac07_raunak_d31_05_direct", "d31_05"),
    ("ac08_raunak_d37_05_direct", "d37_05"),
    ("ac09_raunak_min31_05_direct", "min31_05"),
]


RANK_BLEND_QUEUE = [
    ("ac10_rank_max46_dataregressor_98_02", {"max46_05": 0.98, "dataregressor": 0.02}),
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
