#!/usr/bin/env python3
"""Create the 2026-05-12 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round6"


SOURCES = {
    "s19": ROOT / "public_outputs/flexon_blender_95419/outputs/max/s19.csv",
    "mikhail_0512": ROOT / "public_outputs/mikhail_20260512/submission.csv",
    "nikita_cat": ROOT / "public_outputs/nikita_catboost_20260511/submission.csv",
    "simon_stack": ROOT / "public_outputs/simon_stacking_20260512/submission_stacking.csv",
    "gkanamoto": ROOT / "public_outputs/gkanamoto_s6e5_ensemble/submission.csv",
    "nina_hb5": ROOT / "public_outputs/nina_hb5_95419/submission.csv",
    "raunak_log_s11": ROOT / "public_outputs/raunak_diversity_correction/outputs/max/log_s11.csv",
    "raunak_geo_s11": ROOT / "public_outputs/raunak_diversity_correction/outputs/max/geo_s11.csv",
    "flex_d01": ROOT / "public_outputs/flexon_blender_95419/outputs/pro/d01.csv",
    "flex_t02": ROOT / "public_outputs/flexon_blender_95419/outputs/pro/t02.csv",
    "flex_rs11": ROOT / "public_outputs/flexon_blender_95419/outputs/pro/rs11.csv",
    "flex_cup02": ROOT / "public_outputs/flexon_blender_95419/outputs/pro/cup02.csv",
    "flex_cdn02": ROOT / "public_outputs/flexon_blender_95419/outputs/pro/cdn02.csv",
    "flex_ex02": ROOT / "public_outputs/flexon_blender_95419/outputs/pro/ex02.csv",
    "raunak_log_tb": ROOT / "public_outputs/raunak_diversity_correction/outputs/max/log_tb.csv",
    "raunak_pow_tb": ROOT / "public_outputs/raunak_diversity_correction/outputs/pro/pow_tb.csv",
    "raunak_log_s18": ROOT / "public_outputs/raunak_diversity_correction/outputs/pro/log_s18.csv",
}


DIRECT = [
    ("x01_flex_ex02_direct", "flex_ex02"),
    ("x02_flex_cdn02_direct", "flex_cdn02"),
    ("x03_flex_cup02_direct", "flex_cup02"),
    ("x04_flex_d01_direct", "flex_d01"),
    ("x07_mikhail_0512_direct", "mikhail_0512"),
    ("x08_flex_rs11_direct", "flex_rs11"),
    ("x09_flex_t02_direct", "flex_t02"),
    ("x10_raunak_log_tb_direct", "raunak_log_tb"),
    ("x11_raunak_pow_tb_direct", "raunak_pow_tb"),
    ("x12_raunak_log_s18_direct", "raunak_log_s18"),
]


RANK_BLEND = [
    ("x05_rank_s19_nina_geo_72_16_12", {"s19": 0.72, "nina_hb5": 0.16, "raunak_geo_s11": 0.12}),
    (
        "x06_rank_s19_log_geo_nina_70_10_10_10",
        {"s19": 0.70, "raunak_log_s11": 0.10, "raunak_geo_s11": 0.10, "nina_hb5": 0.10},
    ),
    ("x13_rank_s19_mikhail_95_05", {"s19": 0.95, "mikhail_0512": 0.05}),
    ("x14_rank_s19_mikhail_90_10", {"s19": 0.90, "mikhail_0512": 0.10}),
    ("x15_rank_s19_mikhail_nikita_86_10_04", {"s19": 0.86, "mikhail_0512": 0.10, "nikita_cat": 0.04}),
    ("x16_rank_s19_mikhail_simon_86_12_02", {"s19": 0.86, "mikhail_0512": 0.12, "simon_stack": 0.02}),
    ("x17_rank_s19_mikhail_gkanamoto_90_08_02", {"s19": 0.90, "mikhail_0512": 0.08, "gkanamoto": 0.02}),
]


PROB_BLEND = [
    ("x18_prob_s19_mikhail_90_10", {"s19": 0.90, "mikhail_0512": 0.10}),
]


def load_source(path: Path, sample: pd.DataFrame) -> pd.Series:
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} bad columns: {list(df.columns)}")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
        raise ValueError(f"{path} is not sample aligned")
    pred = df[TARGET].astype(float)
    if not np.isfinite(pred).all():
        raise ValueError(f"{path} non-finite predictions")
    return pred


def rank_norm(values: pd.Series) -> np.ndarray:
    arr = values.to_numpy(dtype=float)
    return rankdata(arr, method="average") / len(arr)


def write_submission(name: str, pred: np.ndarray | pd.Series, sample: pd.DataFrame) -> Path:
    arr = np.asarray(pred, dtype=float)
    sub = sample.copy()
    sub[TARGET] = arr.clip(0, 1)
    path = OUT / f"{name}.csv"
    sub.to_csv(path, index=False)
    return path


def describe(path: Path) -> str:
    pred = pd.read_csv(path)[TARGET].astype(float)
    return f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}"


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}

    anchor = preds["s19"].to_numpy()
    print("source,min,max,mean,std,corr_s19")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated")
    for name, source in DIRECT:
        path = write_submission(name, preds[source], sample)
        print(describe(path))

    for name, weights in RANK_BLEND:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * rank_norm(preds[source])
        blended /= total
        final = rankdata(blended, method="average") / len(blended)
        path = write_submission(name, final, sample)
        print(describe(path))

    for name, weights in PROB_BLEND:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * preds[source].to_numpy(dtype=float)
        blended /= total
        path = write_submission(name, blended, sample)
        print(describe(path))


if __name__ == "__main__":
    main()
