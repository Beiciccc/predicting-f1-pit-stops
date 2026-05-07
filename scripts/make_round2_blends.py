#!/usr/bin/env python3
"""Create the 2026-05-06 submission queue from newly downloaded artifacts."""

from __future__ import annotations

from pathlib import Path
from shutil import copyfile

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round2"


SOURCES = {
    "sohail": ROOT / "public_outputs" / "sohail" / "final_submission.csv",
    "yekenot": ROOT / "public_outputs" / "yekenot" / "submission.csv",
    "moj": ROOT / "public_outputs" / "mojjeed_multiseed" / "submission.csv",
    "pilk_stack": ROOT / "public_outputs" / "pilkwang_high_score_stacking" / "submission_stack_rank_blend.csv",
    "pilk_lgb": ROOT / "public_outputs" / "pilkwang_high_score_stacking" / "sub_lgb_domain_w07_full_fullrows_10fold.csv",
    "pilk_xgb": ROOT / "public_outputs" / "pilkwang_high_score_stacking" / "sub_xgb_core_w1_full_fullrows_10fold.csv",
    "pilk_cat": ROOT / "public_outputs" / "pilkwang_high_score_stacking" / "sub_cat_core_w1_full_fullrows_10fold.csv",
    "pilk_xgbte": ROOT / "public_outputs" / "pilkwang_high_score_stacking" / "sub_xgb_public_te_w1_full_fullrows_10fold.csv",
    "roman_v8": ROOT / "public_outputs" / "roman_driver_race_year" / "submission_v8_solo.csv",
    "leon": ROOT / "public_outputs" / "leonchani_02_nn_predicting_f1_pit_stops" / "submission.csv",
    "mikhail": ROOT / "public_outputs" / "mikhailnaumov_f1_pit_stops_ensemble" / "submission.csv",
    "local_hgb": ROOT / "playground-series-s6e5" / "submission.csv",
}


PLANS: list[tuple[str, dict[str, float] | str]] = [
    ("t01_mojjeed_direct", "moj"),
    ("t02_pilkwang_stack_direct", "pilk_stack"),
    ("t03_oof_rank_moj40_pilk30_yek30", {"moj": 0.40, "pilk_stack": 0.30, "yekenot": 0.30}),
    ("t04_oof_rank_moj50_pilk30_yek20", {"moj": 0.50, "pilk_stack": 0.30, "yekenot": 0.20}),
    ("t05_oof_rank_moj35_pilk35_yek30", {"moj": 0.35, "pilk_stack": 0.35, "yekenot": 0.30}),
    ("t06_pilkwang_learner_rank", {"pilk_lgb": 0.35, "pilk_xgb": 0.30, "pilk_cat": 0.20, "pilk_xgbte": 0.15}),
    ("t07_roman_v8_solo_direct", "roman_v8"),
    ("t08_rank_moj50_romanv8_25_sohail25", {"moj": 0.50, "roman_v8": 0.25, "sohail": 0.25}),
    ("t09_rank_sohail35_moj30_pilk25_leon10", {"sohail": 0.35, "moj": 0.30, "pilk_stack": 0.25, "leon": 0.10}),
    ("t10_rank_moj40_pilk25_mikhail15_hgb10_leon10", {"moj": 0.40, "pilk_stack": 0.25, "mikhail": 0.15, "local_hgb": 0.10, "leon": 0.10}),
]


def load(path: Path, sample: pd.DataFrame) -> pd.Series:
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} has unexpected columns: {list(df.columns)}")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
        raise ValueError(f"{path} is not aligned with sample_submission")
    pred = df[TARGET].astype(float)
    if not np.isfinite(pred).all():
        raise ValueError(f"{path} has non-finite predictions")
    return pred.clip(0, 1)


def rank01(values: pd.Series) -> np.ndarray:
    return rankdata(values.to_numpy(dtype=float), method="average") / len(values)


def write_blend(name: str, weights: dict[str, float], preds: dict[str, pd.Series], sample: pd.DataFrame) -> Path:
    total = sum(weights.values())
    blend = np.zeros(len(sample), dtype=float)
    for source, weight in weights.items():
        blend += weight * rank01(preds[source])
    blend /= total
    out = sample.copy()
    out[TARGET] = rankdata(blend, method="average") / len(blend)
    path = OUT / f"{name}.csv"
    out.to_csv(path, index=False)
    return path


def write_direct(name: str, source: str, preds: dict[str, pd.Series], sample: pd.DataFrame) -> Path:
    out = sample.copy()
    out[TARGET] = preds[source]
    path = OUT / f"{name}.csv"
    out.to_csv(path, index=False)
    return path


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load(path, sample) for name, path in SOURCES.items()}

    for name, plan in PLANS:
        if isinstance(plan, str):
            path = write_direct(name, plan, preds, sample)
        else:
            path = write_blend(name, plan, preds, sample)
        pred = pd.read_csv(path)[TARGET]
        print(f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f},{pred.nunique()}")


if __name__ == "__main__":
    main()
