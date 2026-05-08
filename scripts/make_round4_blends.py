#!/usr/bin/env python3
"""Create the 2026-05-08 submission queue."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round4"


SOURCES = {
    "t85": ROOT / "public_outputs/flexon_blender_95410_20260508/outputs/blender/submissions/score_guided/t85.csv",
    "tb": ROOT / "public_outputs/flexon_blender_95410_20260508/outputs/blender/submissions/top_external/tb.csv",
    "t925": ROOT / "public_outputs/flexon_blender_95410_20260508/outputs/blender/submissions/pair_search/t925.csv",
    "t975": ROOT / "public_outputs/flexon_blender_95410_20260508/outputs/blender/submissions/pair_search/t975.csv",
    "a40": ROOT / "public_outputs/flexon_blender_95410_20260508/outputs/blender/submissions/pair_search/a40.csv",
    "a60": ROOT / "public_outputs/flexon_blender_95410_20260508/outputs/blender/submissions/pair_search/a60.csv",
    "sohail_95411": ROOT / "public_outputs/sohail_blending_95411/submission.csv",
    "deep_95411": ROOT / "public_outputs/deeplearnerrr_blend_95411/submission.csv",
    "abhishek_95410": ROOT / "public_outputs/abhishek_rfecv_95410/submission.csv",
    "mikhail_0508": ROOT / "public_outputs/mikhail_20260508/submission.csv",
    "nina_hb4": ROOT / "public_outputs/nina_hb4/submission.csv",
}


DIRECT_QUEUE = [
    ("v01_sohail_95411_direct", "sohail_95411"),
    ("v02_deep_95411_direct", "deep_95411"),
    ("v03_abhishek_95410_direct", "abhishek_95410"),
    ("v04_mikhail_0508_direct", "mikhail_0508"),
    ("v05_flex_t925_direct", "t925"),
    ("v06_flex_t975_direct", "t975"),
    ("v07_flex_a40_direct", "a40"),
    ("v08_flex_a60_direct", "a60"),
]


BLEND_QUEUE = [
    ("v09_rank_t85_sohail_deep", {"t85": 0.50, "sohail_95411": 0.25, "deep_95411": 0.25}),
    (
        "v10_rank_t85_tb_sohail_t925",
        {"t85": 0.40, "tb": 0.25, "sohail_95411": 0.20, "t925": 0.15},
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
    return pred.clip(0, 1)


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

    print("source,min,max,mean,std,corr_t85")
    t85 = preds["t85"].to_numpy()
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(t85, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        pred = pd.read_csv(path)[TARGET]
        print(f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}")

    for name, weights in BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * rank_norm(preds[source])
        blended /= total
        final = rankdata(blended, method="average") / len(blended)
        path = write_submission(name, final, sample)
        pred = pd.read_csv(path)[TARGET]
        print(f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}")


if __name__ == "__main__":
    main()
