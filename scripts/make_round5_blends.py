#!/usr/bin/env python3
"""Create the 2026-05-11 submission queue."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round5"


SOURCES = {
    "flex_s19": ROOT / "public_outputs/flexon_blender_95419/outputs/max/s19.csv",
    "flex_d02": ROOT / "public_outputs/flexon_blender_95419/outputs/max/d02.csv",
    "flex_rtb02": ROOT / "public_outputs/flexon_blender_95419/outputs/max/rtb02.csv",
    "flex_cs02": ROOT / "public_outputs/flexon_blender_95419/outputs/max/cs02.csv",
    "raunak_log_s11": ROOT / "public_outputs/raunak_diversity_correction/outputs/max/log_s11.csv",
    "raunak_geo_s11": ROOT / "public_outputs/raunak_diversity_correction/outputs/max/geo_s11.csv",
    "nina_hb5": ROOT / "public_outputs/nina_hb5_95419/submission.csv",
    "abd_s18": ROOT / "public_outputs/abdullah_blender_95418/outputs/max/s18.csv",
    "masaya_mlp32": ROOT / "public_outputs/masaya_stacking_vibe_latest/submission_gpu_2layer_stack_base_l1_l2_logreg_l1_mlp_32x16_0.954471.csv",
    "gkanamoto": ROOT / "public_outputs/gkanamoto_s6e5_ensemble/submission.csv",
}


DIRECT_QUEUE = [
    ("w01_flex_s19_direct", "flex_s19"),
    ("w02_flex_d02_direct", "flex_d02"),
    ("w03_flex_rtb02_direct", "flex_rtb02"),
    ("w04_flex_cs02_direct", "flex_cs02"),
    ("w05_raunak_log_s11_direct", "raunak_log_s11"),
    ("w06_raunak_geo_s11_direct", "raunak_geo_s11"),
    ("w07_nina_hb5_direct", "nina_hb5"),
    ("w08_abd_s18_direct", "abd_s18"),
    ("w09_masaya_mlp32_direct", "masaya_mlp32"),
]


BLEND_QUEUE = [
    ("w10_rank_s19_masaya_gkanamoto", {"flex_s19": 0.82, "masaya_mlp32": 0.13, "gkanamoto": 0.05}),
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


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}

    anchor = preds["flex_s19"].to_numpy()
    print("source,min,max,mean,std,corr_s19")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        pred = pd.read_csv(path)[TARGET]
        print(f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}")

    for name, weights in BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * rank_norm(preds[source])
        blended /= total
        final = rankdata(blended, method="average") / len(blended)
        path = write_submission(name, final, sample)
        pred = pd.read_csv(path)[TARGET]
        print(f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}")


if __name__ == "__main__":
    main()
