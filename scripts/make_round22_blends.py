#!/usr/bin/env python3
"""Create the 2026-05-30 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round22"


SOURCES = {
    "dr23": ROOT / "submissions_round15/ag02_dataregressor_20260523_direct.csv",
    "ai04": ROOT / "submissions_round17/ai04_prob_dr23_hb12_995_005.csv",
    "varad30": ROOT / "public_outputs/varad_xgb_lgb_20260530/xgb_lgb_wLR.csv",
    "ruihao_full30": ROOT / "public_outputs/ruihao_catboost_gpu_full_20260530/submission.csv",
    "sarvesh_triple30": ROOT / "public_outputs/sarvesh_triple_boost_20260530/submission.csv",
    "sarvesh_lgbm30": ROOT / "public_outputs/sarvesh_lgbm_blending_20260530/submission.csv",
    "parth30": ROOT / "public_outputs/parth_cat_xgb_blend_20260530/submission.csv",
}


DIRECT_QUEUE = [
    ("an01_varad30_direct", "varad30"),
    ("an02_ruihao_gpu_full30_direct", "ruihao_full30"),
    ("an06_sarvesh_lgbm30_direct", "sarvesh_lgbm30"),
    ("an06_sarvesh_triple30_direct", "sarvesh_triple30"),
]


RANK_BLEND_QUEUE = [
    ("an03_rank_dr23_varad30_95_05", "dr23", {"dr23": 0.95, "varad30": 0.05}),
    ("an04_rank_dr23_varad30_90_10", "dr23", {"dr23": 0.90, "varad30": 0.10}),
    ("an05_rank_dr23_varad30_80_20", "dr23", {"dr23": 0.80, "varad30": 0.20}),
    ("an07_rank_dr23_sarvesh_lgbm30_80_20", "dr23", {"dr23": 0.80, "sarvesh_lgbm30": 0.20}),
    ("an09_rank_dr23_sarvesh_triple30_98_02", "dr23", {"dr23": 0.98, "sarvesh_triple30": 0.02}),
]


PROB_BLEND_QUEUE = [
    ("an07_prob_dr23_sarvesh_triple30_80_20", {"dr23": 0.80, "sarvesh_triple30": 0.20}),
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
    return rankdata(values.to_numpy(dtype=float), method="average") / len(values)


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


def source_summary(name: str, arr: np.ndarray, preds: dict[str, pd.Series]) -> str:
    return (
        f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
        f"{np.corrcoef(preds['dr23'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['varad30'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['ruihao_full30'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['sarvesh_triple30'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['parth30'], arr)[0, 1]:.10f}"
    )


def describe(path: Path, preds: dict[str, pd.Series], seen_hashes: dict[str, list[str]]) -> str:
    arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
    duplicate = "|".join(seen_hashes.get(fingerprint(arr), []))
    return f"{path},{source_summary(path.stem, arr, preds).split(',', 1)[1]},{duplicate}"


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("an*.csv"):
        old.unlink()
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    header = "source,min,max,mean,std,corr_dr23,corr_varad30,corr_ruihao_full30,corr_sarvesh_triple30,corr_parth30"
    print(header)
    for name, pred in preds.items():
        print(source_summary(name, pred.to_numpy(), preds))

    print(f"\ncreated,{header.split(',', 1)[1]},duplicate_previous")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        print(describe(path, preds, seen_hashes))

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
