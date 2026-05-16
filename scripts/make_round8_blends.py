#!/usr/bin/env python3
"""Create the 2026-05-16 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round8"


SOURCES = {
    "raunak_s37": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/s37.csv",
    "raunak_r35": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/r35.csv",
    "raunak_l35": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/l35.csv",
    "raunak_ex35": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/ex35.csv",
    "raunak_c35": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/c35.csv",
    "raunak_log35": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/log35.csv",
    "raunak_lc": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/lc.csv",
    "raunak_r31": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/r31.csv",
    "raunak_hb37": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/hb37.csv",
    "sohail_95420": ROOT / "public_outputs/sohail_95420_20260516/submission.csv",
}


QUEUE = [
    ("z01_raunak_s37_direct", "raunak_s37"),
    ("z02_raunak_ex35_direct", "raunak_ex35"),
    ("z03_raunak_c35_direct", "raunak_c35"),
    ("z04_raunak_r35_direct", "raunak_r35"),
    ("z05_raunak_l35_direct", "raunak_l35"),
    ("z06_raunak_log35_direct", "raunak_log35"),
    ("z07_raunak_lc_direct", "raunak_lc"),
    ("z08_raunak_hb37_direct", "raunak_hb37"),
    ("z09_raunak_r31_direct", "raunak_r31"),
]


RANK_BLEND = [
    ("z10_rank_s37_hb37_sohail_97_02_01", {"raunak_s37": 0.97, "raunak_hb37": 0.02, "sohail_95420": 0.01}),
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


def rank_norm(values: pd.Series) -> np.ndarray:
    arr = values.to_numpy(dtype=float)
    return rankdata(arr, method="average") / len(arr)


def describe(path: Path) -> str:
    pred = pd.read_csv(path)[TARGET].astype(float)
    return f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}"


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}

    anchor = preds["raunak_s37"].to_numpy()
    print("source,min,max,mean,std,corr_s37")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated")
    for name, source in QUEUE:
        path = write_submission(name, preds[source], sample)
        print(describe(path))

    for name, weights in RANK_BLEND:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * rank_norm(preds[source])
        blended /= total
        final = pd.Series(rankdata(blended, method="average") / len(blended), index=sample.index)
        path = write_submission(name, final, sample)
        print(describe(path))


if __name__ == "__main__":
    main()
