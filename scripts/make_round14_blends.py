#!/usr/bin/env python3
"""Create the 2026-05-22 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round14"


SOURCES = {
    "tail53_top_05": ROOT / "submissions_round13/ae01_tail53_top_05_direct.csv",
    "s53_raw": ROOT / "submissions_round13/ae02_s53_raw_direct.csv",
    "max52_46_02": ROOT / "submissions_round12/ad05_max52_46_02_direct.csv",
    "dataregressor_20260522": ROOT / "public_outputs/dataregressor_knock_20260522/submission.csv",
}


DIRECT_QUEUE = [
    ("af01_dataregressor_20260522_direct", "dataregressor_20260522"),
]


PROB_BLEND_QUEUE = [
    ("af02_prob_max52_datareg22_995_005", {"max52_46_02": 0.995, "dataregressor_20260522": 0.005}),
    ("af03_prob_max52_datareg22_99_01", {"max52_46_02": 0.99, "dataregressor_20260522": 0.01}),
    ("af04_prob_s53_datareg22_995_005", {"s53_raw": 0.995, "dataregressor_20260522": 0.005}),
    ("af05_prob_tail53_datareg22_995_005", {"tail53_top_05": 0.995, "dataregressor_20260522": 0.005}),
    ("af09_prob_max52_s53_50_50", {"max52_46_02": 0.50, "s53_raw": 0.50}),
    ("af10_prob_max52_tail53_50_50", {"max52_46_02": 0.50, "tail53_top_05": 0.50}),
]


RANK_BLEND_QUEUE = [
    ("af06_rank_max52_datareg22_995_005", "max52_46_02", {"max52_46_02": 0.995, "dataregressor_20260522": 0.005}),
    ("af07_rank_max52_datareg22_99_01", "max52_46_02", {"max52_46_02": 0.99, "dataregressor_20260522": 0.01}),
    ("af08_rank_s53_datareg22_995_005", "s53_raw", {"s53_raw": 0.995, "dataregressor_20260522": 0.005}),
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


def fingerprint(values: np.ndarray) -> str:
    return hashlib.md5(np.round(values, 12).tobytes()).hexdigest()


def describe(path: Path, anchors: dict[str, pd.Series], seen_hashes: dict[str, list[str]]) -> str:
    arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
    duplicate = "|".join(seen_hashes.get(fingerprint(arr), []))
    corr_tail = np.corrcoef(anchors["tail53_top_05"], arr)[0, 1]
    corr_max = np.corrcoef(anchors["max52_46_02"], arr)[0, 1]
    return (
        f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},"
        f"{arr.std():.8f},{corr_tail:.10f},{corr_max:.10f},{duplicate}"
    )


def previous_submission_hashes() -> dict[str, list[str]]:
    hashes: dict[str, list[str]] = {}
    for path in sorted(ROOT.glob("submissions*/**/*.csv")):
        if OUT in path.parents:
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if TARGET not in df.columns:
            continue
        arr = df[TARGET].astype(float).to_numpy()
        hashes.setdefault(fingerprint(arr), []).append(str(path.relative_to(ROOT)))
    return hashes


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    print("source,min,max,mean,std,corr_tail53_top,corr_max52")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr_tail = np.corrcoef(preds["tail53_top_05"], arr)[0, 1]
        corr_max = np.corrcoef(preds["max52_46_02"], arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr_tail:.10f},{corr_max:.10f}")

    print("\ncreated,min,max,mean,std,corr_tail53_top,corr_max52,duplicate_previous")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        print(describe(path, preds, seen_hashes))

    for name, weights in PROB_BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * preds[source].to_numpy(dtype=float)
        blended /= total
        path = write_submission(name, blended, sample)
        print(describe(path, preds, seen_hashes))

    for name, anchor_source, weights in RANK_BLEND_QUEUE:
        final = rank_remap(preds[anchor_source], weights, preds)
        path = write_submission(name, final, sample)
        print(describe(path, preds, seen_hashes))


if __name__ == "__main__":
    main()
