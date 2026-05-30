#!/usr/bin/env python3
"""Create the 2026-05-29 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round21"


SOURCES = {
    "dr23": ROOT / "submissions_round15/ag02_dataregressor_20260523_direct.csv",
    "ag09": ROOT / "submissions_round15/ag09_rank_anth23_yekenot_pytab_995_005.csv",
    "ai04": ROOT / "submissions_round17/ai04_prob_dr23_hb12_995_005.csv",
    "ak10": ROOT / "submissions_round19/ak10_rank_dr23_jayhawk_djenk_parth_997_0015_001_0005.csv",
    "sarvesh29": ROOT / "public_outputs/sarvesh_eda_podium_20260529/submission.csv",
    "shamanth28": ROOT / "public_outputs/shamanth_predict_f1_20260528/submission.csv",
    "evridge29": ROOT / "public_outputs/evgen_tabm_blend_20260529/submission_ridge_final.csv",
    "evtabm29": ROOT / "public_outputs/evgen_tabm_blend_20260529/submission.csv",
    "sakuno29": ROOT / "public_outputs/sakuno_cv_cat_20260529/submission.csv",
    "parth29": ROOT / "public_outputs/parth_cat_xgb_blend_20260529/submission.csv",
    "djenk28": ROOT / "public_outputs/djenk_tabm_xgb_oof_20260528/submission.csv",
    "fullmetal29": ROOT / "public_outputs/fullmetal_tire_degradation_20260529/submission.csv",
}


DIRECT_QUEUE = [
    ("am01_sarvesh29_direct", "sarvesh29"),
]


RANK_BLEND_QUEUE = [
    ("am02_rank_dr23_sarvesh29_98_02", "dr23", {"dr23": 0.98, "sarvesh29": 0.02}),
    ("am03_rank_dr23_sarvesh29_95_05", "dr23", {"dr23": 0.95, "sarvesh29": 0.05}),
    ("am04_rank_dr23_shamanth28_9995_0005", "dr23", {"dr23": 0.9995, "shamanth28": 0.0005}),
    ("am05_rank_dr23_shamanth28_99_01", "dr23", {"dr23": 0.99, "shamanth28": 0.01}),
    ("am06_rank_dr23_evridge29_98_02", "dr23", {"dr23": 0.98, "evridge29": 0.02}),
    ("am07_rank_dr23_evtabm29_975_025", "dr23", {"dr23": 0.975, "evtabm29": 0.025}),
    ("am08_rank_dr23_sarvesh29_99_01", "dr23", {"dr23": 0.99, "sarvesh29": 0.01}),
    (
        "am09_rank_ai04_sarvesh29_99_01",
        "ai04",
        {"ai04": 0.99, "sarvesh29": 0.01},
    ),
    (
        "am10_rank_dr23_sarvesh29_parth29_985_010_005",
        "dr23",
        {"dr23": 0.985, "sarvesh29": 0.01, "parth29": 0.005},
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


def source_summary(name: str, arr: np.ndarray, preds: dict[str, pd.Series]) -> str:
    return (
        f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
        f"{np.corrcoef(preds['dr23'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['sarvesh29'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['shamanth28'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['evridge29'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['parth29'], arr)[0, 1]:.10f}"
    )


def describe(path: Path, preds: dict[str, pd.Series], seen_hashes: dict[str, list[str]]) -> str:
    arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
    duplicate = "|".join(seen_hashes.get(fingerprint(arr), []))
    return f"{path},{source_summary(path.stem, arr, preds).split(',', 1)[1]},{duplicate}"


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    header = "source,min,max,mean,std,corr_dr23,corr_sarvesh29,corr_shamanth28,corr_evridge29,corr_parth29"
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
