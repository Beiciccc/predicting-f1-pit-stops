#!/usr/bin/env python3
"""Create the 2026-05-17 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round9"


SOURCES = {
    "raunak_s37": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/s37.csv",
    "raunak_log31": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/max/log31.csv",
    "raunak_cc": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/cc.csv",
    "raunak_hc37": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/hc37.csv",
    "raunak_hbold": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/hbold.csv",
    "raunak_l31": ROOT / "public_outputs/raunak_blender_95437_20260516/outputs/pro/l31.csv",
    "giovanny_95446": ROOT / "public_outputs/giovanny_95446_20260517/submission.csv",
    "nina_hb10": ROOT / "public_outputs/nina_hb10_20260516/submission.csv",
    "masaya_mlp32": ROOT
    / "public_outputs/masaya_stacking_vibe_latest/submission_gpu_2layer_stack_base_l1_l2_logreg_l1_mlp_32x16_0.954471.csv",
}


DIRECT_QUEUE = [
    ("aa01_giovanny_95446_direct", "giovanny_95446"),
    ("aa02_nina_hb10_direct", "nina_hb10"),
    ("aa03_raunak_log31_direct", "raunak_log31"),
    ("aa04_raunak_cc_direct", "raunak_cc"),
    ("aa05_raunak_l31_direct", "raunak_l31"),
    ("aa06_raunak_hc37_direct", "raunak_hc37"),
    ("aa07_raunak_hbold_direct", "raunak_hbold"),
]


RANK_BLEND_QUEUE = [
    ("aa08_rank_giovanny_s37_95_05", {"giovanny_95446": 0.95, "raunak_s37": 0.05}),
    (
        "aa09_rank_giovanny_nina_s37_88_08_04",
        {"giovanny_95446": 0.88, "nina_hb10": 0.08, "raunak_s37": 0.04},
    ),
    (
        "aa10_rank_giovanny_s37_masaya_90_08_02",
        {"giovanny_95446": 0.90, "raunak_s37": 0.08, "masaya_mlp32": 0.02},
    ),
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


def write_submission(name: str, pred: np.ndarray | pd.Series, sample: pd.DataFrame) -> Path:
    sub = sample.copy()
    sub[TARGET] = np.asarray(pred, dtype=float).clip(0, 1)
    path = OUT / f"{name}.csv"
    sub.to_csv(path, index=False)
    return path


def describe(path: Path, anchor: np.ndarray) -> str:
    pred = pd.read_csv(path)[TARGET].astype(float).to_numpy()
    corr = np.corrcoef(anchor, pred)[0, 1]
    return (
        f"{path},{pred.min():.8f},{pred.max():.8f},"
        f"{pred.mean():.8f},{pred.std():.8f},{corr:.10f}"
    )


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}

    anchor = preds["raunak_s37"].to_numpy()
    print("source,min,max,mean,std,corr_s37")
    for name, pred in preds.items():
        arr = pred.to_numpy()
        corr = np.corrcoef(anchor, arr)[0, 1]
        print(f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},{corr:.10f}")

    print("\ncreated,min,max,mean,std,corr_s37")
    for name, source in DIRECT_QUEUE:
        path = write_submission(name, preds[source], sample)
        print(describe(path, anchor))

    for name, weights in RANK_BLEND_QUEUE:
        total = sum(weights.values())
        blended = np.zeros(len(sample), dtype=float)
        for source, weight in weights.items():
            blended += weight * rank_norm(preds[source])
        blended /= total
        final = rankdata(blended, method="average") / len(blended)
        path = write_submission(name, final, sample)
        print(describe(path, anchor))


if __name__ == "__main__":
    main()
