#!/usr/bin/env python3
"""Create the 2026-05-23 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round15"


SOURCES = {
    "max52_46_02": ROOT / "submissions_round12/ad05_max52_46_02_direct.csv",
    "s53_raw": ROOT / "submissions_round13/ae02_s53_raw_direct.csv",
    "tail53_top_05": ROOT / "submissions_round13/ae01_tail53_top_05_direct.csv",
    "anthony_20260523": ROOT / "public_outputs/anthony_nn_residual_20260523/submission.csv",
    "dataregressor_20260523": ROOT / "public_outputs/dataregressor_knock_20260523/submission.csv",
    "yekenot_pytabkit_20260523": ROOT / "public_outputs/yekenot_pytabkit_20260523/submission.csv",
    "mirza_sub8_optuna": ROOT / "public_outputs/mirza_best_20260523/outputs/subs/sub_8_optuna.csv",
}


DIRECT_QUEUE = [
    ("ag01_anthony_20260523_direct", "anthony_20260523"),
    ("ag02_dataregressor_20260523_direct", "dataregressor_20260523"),
    ("ag10_mirza_sub8_optuna_direct", "mirza_sub8_optuna"),
]


PROB_BLEND_QUEUE = [
    ("ag03_prob_max52_anth23_995_005", {"max52_46_02": 0.995, "anthony_20260523": 0.005}),
    ("ag04_prob_s53_anth23_995_005", {"s53_raw": 0.995, "anthony_20260523": 0.005}),
    ("ag05_prob_tail53_anth23_995_005", {"tail53_top_05": 0.995, "anthony_20260523": 0.005}),
    ("ag08_prob_anth23_yekenot_pytab_995_005", {"anthony_20260523": 0.995, "yekenot_pytabkit_20260523": 0.005}),
]


RANK_BLEND_QUEUE = [
    ("ag06_rank_max52_anth23_995_005", "max52_46_02", {"max52_46_02": 0.995, "anthony_20260523": 0.005}),
    ("ag07_rank_s53_anth23_995_005", "s53_raw", {"s53_raw": 0.995, "anthony_20260523": 0.005}),
    ("ag09_rank_anth23_yekenot_pytab_995_005", "anthony_20260523", {"anthony_20260523": 0.995, "yekenot_pytabkit_20260523": 0.005}),
]


def load_source(path: Path, sample: pd.DataFrame) -> pd.Series:
    df = pd.read_csv(path)
    if "id" not in df.columns:
        raise ValueError(f"{path} does not contain id")
    pred_col = TARGET if TARGET in df.columns else [col for col in df.columns if col != "id"][0]
    df = df[["id", pred_col]].rename(columns={pred_col: TARGET})
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


def describe(path: Path, preds: dict[str, pd.Series], seen_hashes: dict[str, list[str]]) -> str:
    arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
    duplicate = "|".join(seen_hashes.get(fingerprint(arr), []))
    corr_anth = np.corrcoef(preds["anthony_20260523"], arr)[0, 1]
    corr_max = np.corrcoef(preds["max52_46_02"], arr)[0, 1]
    corr_s53 = np.corrcoef(preds["s53_raw"], arr)[0, 1]
    return (
        f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},"
        f"{arr.std():.8f},{corr_anth:.10f},{corr_max:.10f},{corr_s53:.10f},{duplicate}"
    )


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    print("source,min,max,mean,std,corr_anth23,corr_max52,corr_s53")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr_anth = np.corrcoef(preds["anthony_20260523"], arr)[0, 1]
        corr_max = np.corrcoef(preds["max52_46_02"], arr)[0, 1]
        corr_s53 = np.corrcoef(preds["s53_raw"], arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr_anth:.10f},{corr_max:.10f},{corr_s53:.10f}")

    print("\ncreated,min,max,mean,std,corr_anth23,corr_max52,corr_s53,duplicate_previous")
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
