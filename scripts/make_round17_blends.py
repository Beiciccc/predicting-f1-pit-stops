#!/usr/bin/env python3
"""Create the 2026-05-25 submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round17"


SOURCES = {
    "dr23": ROOT / "submissions_round15/ag02_dataregressor_20260523_direct.csv",
    "anth_yek_prob": ROOT / "submissions_round15/ag08_prob_anth23_yekenot_pytab_995_005.csv",
    "anth_yek_rank": ROOT / "submissions_round15/ag09_rank_anth23_yekenot_pytab_995_005.csv",
    "s54_raw": ROOT / "submissions_round16/ah01_s54_raw_direct.csv",
    "rasulbek": ROOT / "submissions_round16/ah05_rasulbek_best7_direct.csv",
    "s54_rank": ROOT / "submissions_round16/ah10_rank_ag09_s54raw_995_005.csv",
    "mikhail25": ROOT / "public_outputs/mikhail_ensemble_20260525/submission.csv",
    "ruihao_hrank": ROOT / "public_outputs/ruihao_blend_our_preds_20260525/blends/h_rank.csv",
    "ruihao_hb12": ROOT / "public_outputs/ruihao_blend_our_preds_20260525/blends/hb12_style.csv",
    "ruihao_best2": ROOT / "public_outputs/ruihao_blend_our_preds_20260525/blends/best2.csv",
    "ruihao_tyrelife": ROOT / "public_outputs/ruihao_tyrelife_norm_compound_20260525/submission.csv",
}


DIRECT_QUEUE = [
    ("ai01_ruihao_hb12_style_direct", "ruihao_hb12"),
    ("ai02_ruihao_h_rank_direct", "ruihao_hrank"),
    ("ai03_ruihao_best2_direct", "ruihao_best2"),
]


PROB_BLEND_QUEUE = [
    ("ai04_prob_dr23_hb12_995_005", {"dr23": 0.995, "ruihao_hb12": 0.005}),
    ("ai06_prob_s54raw_hb12_995_005", {"s54_raw": 0.995, "ruihao_hb12": 0.005}),
    ("ai07_prob_rasulbek_hb12_995_005", {"rasulbek": 0.995, "ruihao_hb12": 0.005}),
    ("ai08_prob_s54rank_hb12_995_005", {"s54_rank": 0.995, "ruihao_hb12": 0.005}),
    ("ai09_prob_dr23_hrank_999_001", {"dr23": 0.999, "ruihao_hrank": 0.001}),
    ("ai10_prob_dr23_tyrelife_9995_0005", {"dr23": 0.9995, "ruihao_tyrelife": 0.0005}),
]


RANK_BLEND_QUEUE = [
    ("ai05_rank_dr23_hb12_995_005", "dr23", {"dr23": 0.995, "ruihao_hb12": 0.005}),
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
    corr_mikhail = np.corrcoef(preds["mikhail25"], arr)[0, 1]
    corr_hrank = np.corrcoef(preds["ruihao_hrank"], arr)[0, 1]
    return (
        f"{path},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
        f"{corr_dr:.10f},{corr_s54:.10f},{corr_mikhail:.10f},{corr_hrank:.10f},{duplicate}"
    )


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    seen_hashes = previous_submission_hashes()

    print("source,min,max,mean,std,corr_dr23,corr_s54_raw,corr_mikhail25,corr_ruihao_hrank")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        print(
            f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
            f"{np.corrcoef(preds['dr23'], arr)[0, 1]:.10f},{np.corrcoef(preds['s54_raw'], arr)[0, 1]:.10f},"
            f"{np.corrcoef(preds['mikhail25'], arr)[0, 1]:.10f},{np.corrcoef(preds['ruihao_hrank'], arr)[0, 1]:.10f}"
        )

    print("\ncreated,min,max,mean,std,corr_dr23,corr_s54_raw,corr_mikhail25,corr_ruihao_hrank,duplicate_previous")
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
