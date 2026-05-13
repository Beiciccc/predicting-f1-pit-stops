#!/usr/bin/env python3
"""Create the 2026-05-13 submission candidates."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round7"


SOURCES = {
    "s19": ROOT / "public_outputs/flexon_blender_95419/outputs/max/s19.csv",
    "raunak_pow_tb": ROOT / "public_outputs/raunak_diversity_correction/outputs/pro/pow_tb.csv",
    "raunak_log_s18": ROOT / "public_outputs/raunak_diversity_correction/outputs/pro/log_s18.csv",
    "anthony_res": ROOT / "public_outputs/anthony_residual_20260512/submission.csv",
    "arun_blend": ROOT / "public_outputs/arun_fe_ensemble_20260512/submission_blended.csv",
    "simarbir": ROOT / "public_outputs/simarbir_realmlp_20260512/submission.csv",
    "degnonguidi12": ROOT / "public_outputs/degnonguidi_20260513/submission12.csv",
    "joseph_stack": ROOT / "public_outputs/joseph_context_stack_20260512/submission.csv",
    "nikita_cat": ROOT / "public_outputs/nikita_catboost_20260511/submission.csv",
    "sarvesh_blend": ROOT / "public_outputs/sarvesh_triple_blend_20260512/submission.csv",
    "simon_stack": ROOT / "public_outputs/simon_stacking_20260512/submission_stacking.csv",
    "gkanamoto": ROOT / "public_outputs/gkanamoto_s6e5_ensemble/submission.csv",
}


DIRECT = [
    ("y01_raunak_pow_tb_direct", "raunak_pow_tb"),
    ("y02_raunak_log_s18_direct", "raunak_log_s18"),
    ("y03_arun_blend_direct", "arun_blend"),
    ("y04_simarbir_direct", "simarbir"),
    ("y05_degnonguidi12_direct", "degnonguidi12"),
    ("y06_anthony_res_direct", "anthony_res"),
]


RANK_BLEND = [
    ("y07_rank_s19_arun_80_20", {"s19": 0.80, "arun_blend": 0.20}),
    ("y08_rank_s19_simarbir_95_05", {"s19": 0.95, "simarbir": 0.05}),
    ("y09_rank_s19_deg12_97_03", {"s19": 0.97, "degnonguidi12": 0.03}),
    ("y10_rank_s19_sim_deg_arun_90_05_03_02", {"s19": 0.90, "simarbir": 0.05, "degnonguidi12": 0.03, "arun_blend": 0.02}),
    ("y11_rank_s19_joseph_97_03", {"s19": 0.97, "joseph_stack": 0.03}),
    ("y12_rank_s19_nikita_97_03", {"s19": 0.97, "nikita_cat": 0.03}),
    ("y13_rank_s19_sarvesh_99_01", {"s19": 0.99, "sarvesh_blend": 0.01}),
    ("y14_rank_s19_simon_gka_96_02_02", {"s19": 0.96, "simon_stack": 0.02, "gkanamoto": 0.02}),
    ("y15_rank_s19_arun_nikita_sarvesh_94_03_02_01", {"s19": 0.94, "arun_blend": 0.03, "nikita_cat": 0.02, "sarvesh_blend": 0.01}),
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


if __name__ == "__main__":
    main()
