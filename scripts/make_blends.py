#!/usr/bin/env python3
"""Create validated submission candidates from local and public model outputs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions"


SOURCES = {
    "yekenot_realmlp": ROOT / "public_outputs" / "yekenot" / "submission.csv",
    "sohail_top10_rank": ROOT / "public_outputs" / "sohail" / "final_submission.csv",
    "anthony_blend": ROOT / "public_outputs" / "anthony" / "submission.csv",
    "nina_hb1": ROOT / "public_outputs" / "nina" / "submission.csv",
    "mikhail_ensemble": ROOT / "public_outputs" / "mikhailnaumov_f1_pit_stops_ensemble" / "submission.csv",
    "leon_nn": ROOT / "public_outputs" / "leonchani_02_nn_predicting_f1_pit_stops" / "submission.csv",
    "huzaifa_ensemble": ROOT / "public_outputs" / "huzaifa242_predicting_f1_pit_stops_ensemble" / "submission.csv",
    "ravi_public": ROOT / "public_outputs" / "ravi20076_playgrounds6e5_public_baseline_v1" / "submission.csv",
    "local_realmlp": ROOT / "submission.csv",
    "local_hgb": ROOT / "playground-series-s6e5" / "submission.csv",
}


PLANS: list[tuple[str, dict[str, float], str]] = [
    ("s01_sohail_direct", {"sohail_top10_rank": 1.0}, "rank"),
    ("s02_huzaifa_direct", {"huzaifa_ensemble": 1.0}, "rank"),
    ("s03_ravi_direct", {"ravi_public": 1.0}, "rank"),
    ("s04_mikhail_direct", {"mikhail_ensemble": 1.0}, "rank"),
    ("s05_nina_sohail_rank_5050", {"nina_hb1": 0.5, "sohail_top10_rank": 0.5}, "rank"),
    ("s06_public_strong_rank", {"nina_hb1": 0.28, "anthony_blend": 0.22, "mikhail_ensemble": 0.2, "sohail_top10_rank": 0.2, "yekenot_realmlp": 0.1}, "rank"),
    ("s07_diverse_rank_all", {"nina_hb1": 0.2, "anthony_blend": 0.16, "mikhail_ensemble": 0.16, "sohail_top10_rank": 0.16, "huzaifa_ensemble": 0.1, "ravi_public": 0.08, "yekenot_realmlp": 0.07, "local_hgb": 0.07}, "rank"),
    ("s08_hgb_sohail_nina_rank", {"sohail_top10_rank": 0.5, "nina_hb1": 0.3, "local_hgb": 0.2}, "rank"),
    ("s09_leon_small_diversifier", {"sohail_top10_rank": 0.35, "nina_hb1": 0.25, "mikhail_ensemble": 0.2, "leon_nn": 0.1, "local_hgb": 0.1}, "rank"),
    ("s10_realmlp_hgb_public_rank", {"sohail_top10_rank": 0.32, "nina_hb1": 0.22, "huzaifa_ensemble": 0.14, "local_realmlp": 0.14, "local_hgb": 0.1, "mikhail_ensemble": 0.08}, "rank"),
]


def load_source(path: Path, sample: pd.DataFrame) -> pd.Series:
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} has unexpected columns: {list(df.columns)}")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
        raise ValueError(f"{path} is not aligned with sample_submission")
    if not np.isfinite(df[TARGET]).all():
        raise ValueError(f"{path} contains non-finite predictions")
    return df[TARGET].astype(float)


def normalize(values: pd.Series, mode: str) -> np.ndarray:
    arr = values.to_numpy(dtype=float)
    if mode == "rank":
        return rankdata(arr, method="average") / len(arr)
    if mode == "raw":
        lo, hi = arr.min(), arr.max()
        return (arr - lo) / (hi - lo) if hi > lo else np.full_like(arr, 0.5)
    raise ValueError(mode)


def make_submission(name: str, weights: dict[str, float], mode: str, preds: dict[str, pd.Series], sample: pd.DataFrame) -> Path:
    total = sum(weights.values())
    blended = np.zeros(len(sample), dtype=float)
    for source, weight in weights.items():
        blended += weight * normalize(preds[source], mode)
    blended /= total
    final = rankdata(blended, method="average") / len(blended)
    sub = sample.copy()
    sub[TARGET] = final
    path = OUT / f"{name}.csv"
    sub.to_csv(path, index=False)
    return path


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    preds = {name: load_source(path, sample) for name, path in SOURCES.items() if path.exists()}
    missing = sorted(set(SOURCES) - set(preds))
    if missing:
        print("Missing sources:", ", ".join(missing))

    print("source,min,max,mean,std")
    for name, pred in preds.items():
        print(f"{name},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}")

    print("\ncreated")
    for name, weights, mode in PLANS:
        if not set(weights).issubset(preds):
            print(f"skip,{name},missing_source")
            continue
        path = make_submission(name, weights, mode, preds, sample)
        pred = pd.read_csv(path)[TARGET]
        print(f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f}")


if __name__ == "__main__":
    main()
