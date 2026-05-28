#!/usr/bin/env python3
"""Create the 2026-05-28 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round20"


SOURCES = {
    "dr23": ROOT / "submissions_round15/ag02_dataregressor_20260523_direct.csv",
    "ag09": ROOT / "submissions_round15/ag09_rank_anth23_yekenot_pytab_995_005.csv",
    "ai04": ROOT / "submissions_round17/ai04_prob_dr23_hb12_995_005.csv",
    "ak01": ROOT / "submissions_round19/ak01_rank_dr23_jayhawk_stack_999_001.csv",
    "ak10": ROOT / "submissions_round19/ak10_rank_dr23_jayhawk_djenk_parth_997_0015_001_0005.csv",
    "parth28": ROOT / "public_outputs/parth_cat_xgb_blend_20260528/submission.csv",
    "koushik28": ROOT / "public_outputs/koushik_prediction_20260528/submission.csv",
    "djenk28": ROOT / "public_outputs/djenk_tabm_xgb_oof_20260528/submission.csv",
    "evgen28": ROOT / "public_outputs/evgen_blending_20260528/submission.csv",
    "alunji28": ROOT / "public_outputs/alunji_predictingnextpit_20260528/submission.csv",
    "yeonseok28": ROOT / "public_outputs/yeonseok_divide_conquer_20260528/submission.csv",
    "sarvesh28": ROOT / "public_outputs/sarvesh_lgbm_blending_20260528/submission.csv",
    "mikhail28": ROOT / "public_outputs/mikhail_ensemble_20260528/submission.csv",
}


DIRECT_QUEUE = []


RANK_BLEND_QUEUE = [
    ("al01_rank_dr23_sarvesh28_999_001", "dr23", {"dr23": 0.999, "sarvesh28": 0.001}),
    ("al02_rank_dr23_sarvesh28_998_002", "dr23", {"dr23": 0.998, "sarvesh28": 0.002}),
    ("al03_rank_ai04_sarvesh28_999_001", "ai04", {"ai04": 0.999, "sarvesh28": 0.001}),
    ("al04_rank_ak10_sarvesh28_999_001", "ak10", {"ak10": 0.999, "sarvesh28": 0.001}),
    (
        "al05_rank_dr23_djenk_sarvesh_9985_001_0005",
        "dr23",
        {"dr23": 0.9985, "djenk28": 0.001, "sarvesh28": 0.0005},
    ),
    ("al06_rank_dr23_evgen28_9995_0005", "dr23", {"dr23": 0.9995, "evgen28": 0.0005}),
    ("al07_rank_dr23_alunji28_9995_0005", "dr23", {"dr23": 0.9995, "alunji28": 0.0005}),
    ("al08_rank_dr23_parth28_999_001", "dr23", {"dr23": 0.999, "parth28": 0.001}),
    ("al09_rank_dr23_yeonseok28_9998_0002", "dr23", {"dr23": 0.9998, "yeonseok28": 0.0002}),
    (
        "al10_rank_ag09_mikhail_sarvesh_9988_001_0002",
        "ag09",
        {"ag09": 0.9988, "mikhail28": 0.001, "sarvesh28": 0.0002},
    ),
]


PROB_BLEND_QUEUE = []


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
    corr_parth = np.corrcoef(preds["parth28"], arr)[0, 1]
    corr_koushik = np.corrcoef(preds["koushik28"], arr)[0, 1]
    corr_evgen = np.corrcoef(preds["evgen28"], arr)[0, 1]
    return (
        f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
        f"{corr_dr:.10f},{corr_parth:.10f},{corr_koushik:.10f},{corr_evgen:.10f},{duplicate}"
    )


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    print("source,min,max,mean,std,corr_dr23,corr_parth28,corr_koushik28,corr_evgen28")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        print(
            f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
            f"{np.corrcoef(preds['dr23'], arr)[0, 1]:.10f},"
            f"{np.corrcoef(preds['parth28'], arr)[0, 1]:.10f},"
            f"{np.corrcoef(preds['koushik28'], arr)[0, 1]:.10f},"
            f"{np.corrcoef(preds['evgen28'], arr)[0, 1]:.10f}"
        )

    print("\ncreated,min,max,mean,std,corr_dr23,corr_parth28,corr_koushik28,corr_evgen28,duplicate_previous")
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
