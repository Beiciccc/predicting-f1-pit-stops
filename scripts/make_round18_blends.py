#!/usr/bin/env python3
"""Create the 2026-05-26 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round18"


SOURCES = {
    "dr23": ROOT / "submissions_round15/ag02_dataregressor_20260523_direct.csv",
    "s54_raw": ROOT / "submissions_round16/ah01_s54_raw_direct.csv",
    "s54_rank": ROOT / "submissions_round16/ah10_rank_ag09_s54raw_995_005.csv",
    "dr23_hb12": ROOT / "submissions_round17/ai04_prob_dr23_hb12_995_005.csv",
    "yek26": ROOT / "public_outputs/yekenot_realmlp_pytorch_20260526/submission.csv",
    "ruihao_cpu": ROOT / "public_outputs/ruihao_realmlp_pytorch_cpu_20260526/submission.csv",
    "lz26": ROOT / "public_outputs/lzsecurity_predicting_20260526/submission.csv",
    "meta_full": ROOT / "public_outputs/ruihao_meta_stack_full_20260526/submission.csv",
}


PROB_BLEND_QUEUE = [
    ("aj07_prob_dr23_yek26_999_001", {"dr23": 0.999, "yek26": 0.001}),
]


RANK_BLEND_QUEUE = [
    ("aj01_rank_dr23_yek26_995_005", "dr23", {"dr23": 0.995, "yek26": 0.005}),
    ("aj02_rank_dr23_yek26_99_01", "dr23", {"dr23": 0.99, "yek26": 0.01}),
    ("aj03_rank_dr23_yek26_98_02", "dr23", {"dr23": 0.98, "yek26": 0.02}),
    ("aj04_rank_dr23_ruihao_cpu_995_005", "dr23", {"dr23": 0.995, "ruihao_cpu": 0.005}),
    ("aj05_rank_dr23_ruihao_cpu_99_01", "dr23", {"dr23": 0.99, "ruihao_cpu": 0.01}),
    ("aj06_rank_dr23_yek26_cpu_990_005_005", "dr23", {"dr23": 0.99, "yek26": 0.005, "ruihao_cpu": 0.005}),
    ("aj08_rank_ai04_yek26_995_005", "dr23_hb12", {"dr23_hb12": 0.995, "yek26": 0.005}),
    ("aj09_rank_ah10_yek26_cpu_lz_990_005_003_002", "s54_rank", {"s54_rank": 0.99, "yek26": 0.005, "ruihao_cpu": 0.003, "lz26": 0.002}),
    ("aj10_rank_dr23_meta_full_999_001", "dr23", {"dr23": 0.999, "meta_full": 0.001}),
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
    corr_dr = np.corrcoef(preds["dr23"], arr)[0, 1]
    corr_yek = np.corrcoef(preds["yek26"], arr)[0, 1]
    corr_cpu = np.corrcoef(preds["ruihao_cpu"], arr)[0, 1]
    corr_lz = np.corrcoef(preds["lz26"], arr)[0, 1]
    return (
        f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
        f"{corr_dr:.10f},{corr_yek:.10f},{corr_cpu:.10f},{corr_lz:.10f},{duplicate}"
    )


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    print("source,min,max,mean,std,corr_dr23,corr_yek26,corr_ruihao_cpu,corr_lz26")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        print(
            f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
            f"{np.corrcoef(preds['dr23'], arr)[0, 1]:.10f},{np.corrcoef(preds['yek26'], arr)[0, 1]:.10f},"
            f"{np.corrcoef(preds['ruihao_cpu'], arr)[0, 1]:.10f},{np.corrcoef(preds['lz26'], arr)[0, 1]:.10f}"
        )

    print("\ncreated,min,max,mean,std,corr_dr23,corr_yek26,corr_ruihao_cpu,corr_lz26,duplicate_previous")
    for name, anchor_source, weights in RANK_BLEND_QUEUE:
        final = rank_remap(preds[anchor_source], weights, preds)
        path = write_submission(name, final, sample)
        print(describe(path, preds, seen_hashes))

    for name, weights in PROB_BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * preds[source].to_numpy(dtype=float)
        blended /= total
        path = write_submission(name, blended, sample)
        print(describe(path, preds, seen_hashes))


if __name__ == "__main__":
    main()
