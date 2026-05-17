#!/usr/bin/env python3
"""Create the remaining 2026-05-17 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round9"


SOURCES = {
    "mikhail_latest": ROOT / "public_outputs/mikhail_latest_20260517/submission.csv",
    "giovanny_95446": ROOT / "public_outputs/giovanny_95446_20260517/submission.csv",
    "raunak_s37": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/s37.csv",
    "nina_hb10": ROOT / "public_outputs/nina_hb10_20260516/submission.csv",
    "karlton_tabpfn3": ROOT / "public_outputs/karlton_tabpfn3_20260517/submission.csv",
}


DIRECT_QUEUE = [
    ("aa06_mikhail_latest_direct", "mikhail_latest"),
]


RANK_BLEND_QUEUE = [
    (
        "aa07_rank_mikhail_giovanny_s37_70_20_10",
        {"mikhail_latest": 0.70, "giovanny_95446": 0.20, "raunak_s37": 0.10},
    ),
    (
        "aa08_rank_mikhail_giovanny_nina_85_10_05",
        {"mikhail_latest": 0.85, "giovanny_95446": 0.10, "nina_hb10": 0.05},
    ),
    (
        "aa09_rank_giovanny_mikhail_s37_70_20_10",
        {"giovanny_95446": 0.70, "mikhail_latest": 0.20, "raunak_s37": 0.10},
    ),
    (
        "aa10_rank_mikhail_karlton_giovanny_90_05_05",
        {"mikhail_latest": 0.90, "karlton_tabpfn3": 0.05, "giovanny_95446": 0.05},
    ),
]


def load_source(path: Path, sample: pd.DataFrame) -> pd.Series:
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} bad columns: {list(df.columns)}")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
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


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}

    anchor = preds["mikhail_latest"].to_numpy()
    print("source,min,max,mean,std,corr_mikhail")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated,min,max,mean,std,corr_mikhail")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    for name, weights in RANK_BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * rank_norm(preds[source])
        blended /= total
        final = rankdata(blended, method="average") / len(blended)
        path = write_submission(name, final, sample)
        arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")


if __name__ == "__main__":
    main()
