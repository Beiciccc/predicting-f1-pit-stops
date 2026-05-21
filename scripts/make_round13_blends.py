#!/usr/bin/env python3
"""Create the 2026-05-21 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round13"


SOURCES = {
    "tail53_top_05": ROOT / "public_outputs/raunak_blender_95453_20260521/outputs/max/tail53_top_05.csv",
    "s53_raw": ROOT / "public_outputs/raunak_blender_95453_20260521/outputs/max/s53_raw.csv",
    "tail53_bottom_05": ROOT / "public_outputs/raunak_blender_95453_20260521/outputs/max/tail53_bottom_05.csv",
    "tail53_dual_03": ROOT / "public_outputs/raunak_blender_95453_20260521/outputs/max/tail53_dual_03.csv",
    "anthony_20260521": ROOT / "public_outputs/anthony_nn_residual_20260521/submission.csv",
    "dataregressor_20260521": ROOT / "public_outputs/dataregressor_knock_20260521/submission.csv",
    "max52_46_02": ROOT / "submissions_round12/ad05_max52_46_02_direct.csv",
    "srp52_46_005": ROOT / "public_outputs/mojjeed_advanced_20260520/outputs/max/srp52_46_005.csv",
    "iso52_46_02": ROOT / "public_outputs/mojjeed_advanced_20260520/outputs/max/iso52_46_02.csv",
}


DIRECT_QUEUE = [
    ("ae01_tail53_top_05_direct", "tail53_top_05"),
    ("ae02_s53_raw_direct", "s53_raw"),
    ("ae03_dataregressor_20260521_direct", "dataregressor_20260521"),
    ("ae04_tail53_dual_03_direct", "tail53_dual_03"),
    ("ae05_tail53_bottom_05_direct", "tail53_bottom_05"),
    ("ae09_srp52_46_005_direct", "srp52_46_005"),
    ("ae10_iso52_46_02_direct", "iso52_46_02"),
]


RANK_BLEND_QUEUE = [
    ("ae08_rank_max52_s53_99_01", "max52_46_02", {"max52_46_02": 0.99, "s53_raw": 0.01}),
]


PROB_BLEND_QUEUE = [
    ("ae06_prob_max52_s53_99_01", {"max52_46_02": 0.99, "s53_raw": 0.01}),
    ("ae07_prob_max52_datareg_99_01", {"max52_46_02": 0.99, "dataregressor_20260521": 0.01}),
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


def rank_remap(anchor: pd.Series, weights: dict[str, float], preds: dict[str, pd.Series]) -> np.ndarray:
    total = sum(weights.values())
    blended = np.zeros(len(anchor), dtype=float)
    for source, weight in weights.items():
        blended += weight * rank_norm(preds[source])
    blended /= total
    order = np.argsort(blended, kind="mergesort")
    sorted_anchor = np.sort(anchor.to_numpy(dtype=float))
    out = np.empty(len(anchor), dtype=float)
    out[order] = sorted_anchor
    return out


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

    anchor = preds["tail53_top_05"].to_numpy()
    print("source,min,max,mean,std,corr_tail53_top")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated,min,max,mean,std,corr_tail53_top")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        print(describe(path, anchor))

    for name, anchor_source, weights in RANK_BLEND_QUEUE:
        final = rank_remap(preds[anchor_source], weights, preds)
        path = write_submission(name, final, sample)
        print(describe(path, anchor))

    for name, weights in PROB_BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * preds[source].to_numpy(dtype=float)
        blended /= total
        path = write_submission(name, blended, sample)
        print(describe(path, anchor))


if __name__ == "__main__":
    main()
