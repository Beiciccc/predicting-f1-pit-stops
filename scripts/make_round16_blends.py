#!/usr/bin/env python3
"""Create the 2026-05-24 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round16"


SOURCES = {
    "dr23": ROOT / "submissions_round15/ag02_dataregressor_20260523_direct.csv",
    "anth23": ROOT / "submissions_round15/ag01_anthony_20260523_direct.csv",
    "anth_yek_prob": ROOT / "submissions_round15/ag08_prob_anth23_yekenot_pytab_995_005.csv",
    "anth_yek_rank": ROOT / "submissions_round15/ag09_rank_anth23_yekenot_pytab_995_005.csv",
    "s54_raw": ROOT / "public_outputs/raunak_blender_95454_20260524/outputs/max/s54_raw.csv",
    "s54_asym_core": ROOT / "public_outputs/raunak_blender_95454_20260524/outputs/max/s54_asym_core.csv",
    "s54_ultra_narrow": ROOT / "public_outputs/raunak_blender_95454_20260524/outputs/max/s54_ultra_narrow.csv",
    "s54_micro_booster": ROOT / "public_outputs/raunak_blender_95454_20260524/outputs/max/s54_micro_booster.csv",
    "rasulbek_best7": ROOT / "public_outputs/rasulbek_best7_20260524/submission.csv",
}


DIRECT_QUEUE = [
    ("ah01_s54_raw_direct", "s54_raw"),
    ("ah02_s54_asym_core_direct", "s54_asym_core"),
    ("ah03_s54_ultra_narrow_direct", "s54_ultra_narrow"),
    ("ah04_s54_micro_booster_direct", "s54_micro_booster"),
    ("ah05_rasulbek_best7_direct", "rasulbek_best7"),
]


PROB_BLEND_QUEUE = [
    ("ah06_prob_dr23_s54raw_50_50", {"dr23": 0.50, "s54_raw": 0.50}),
    ("ah07_prob_ag08_s54raw_995_005", {"anth_yek_prob": 0.995, "s54_raw": 0.005}),
    ("ah08_prob_dr23_rasulbek_50_50", {"dr23": 0.50, "rasulbek_best7": 0.50}),
]


RANK_BLEND_QUEUE = [
    ("ah09_rank_dr23_s54raw_50_50", "dr23", {"dr23": 0.50, "s54_raw": 0.50}),
    ("ah10_rank_ag09_s54raw_995_005", "anth_yek_rank", {"anth_yek_rank": 0.995, "s54_raw": 0.005}),
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
    corr_s54 = np.corrcoef(preds["s54_raw"], arr)[0, 1]
    corr_ag08 = np.corrcoef(preds["anth_yek_prob"], arr)[0, 1]
    return f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr_dr:.10f},{corr_s54:.10f},{corr_ag08:.10f},{duplicate}"


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    print("source,min,max,mean,std,corr_dr23,corr_s54_raw,corr_ag08")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        print(
            f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
            f"{np.corrcoef(preds['dr23'], arr)[0, 1]:.10f},{np.corrcoef(preds['s54_raw'], arr)[0, 1]:.10f},"
            f"{np.corrcoef(preds['anth_yek_prob'], arr)[0, 1]:.10f}"
        )

    print("\ncreated,min,max,mean,std,corr_dr23,corr_s54_raw,corr_ag08,duplicate_previous")
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
