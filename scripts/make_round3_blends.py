#!/usr/bin/env python3
"""Create the 2026-05-07 high-score public blender submission queue."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
OUT = ROOT / "submissions_round3"


QUEUE = [
    ("u01_flexon_tb", ROOT / "public_outputs/flexon_blender_95410/outputs/blender/submissions/top_external/tb.csv"),
    ("u02_flexon_h01", ROOT / "public_outputs/flexon_blender_95410/outputs/blender/submissions/score_guided/h01.csv"),
    ("u03_flexon_h02", ROOT / "public_outputs/flexon_blender_95410/outputs/blender/submissions/score_guided/h02.csv"),
    ("u04_flexon_t95", ROOT / "public_outputs/flexon_blender_95410/outputs/blender/submissions/score_guided/t95.csv"),
    ("u05_flexon_t85", ROOT / "public_outputs/flexon_blender_95410/outputs/blender/submissions/score_guided/t85.csv"),
    ("u06_flexon_hm1", ROOT / "public_outputs/flexon_blender_95410/outputs/blender/submissions/hybrid/hm1.csv"),
    ("u07_flexon_hm2", ROOT / "public_outputs/flexon_blender_95410/outputs/blender/submissions/hybrid/hm2.csv"),
    ("u08_nina_hb4", ROOT / "public_outputs/nina_hb4/submission.csv"),
    ("u09_sohail_95407", ROOT / "public_outputs/sohail_blending_95407/submission.csv"),
    ("u10_mikhail_updated", ROOT / "public_outputs/mikhail_updated/submission.csv"),
]


def validate_source(path: Path, sample: pd.DataFrame) -> pd.DataFrame:
    df = pd.read_csv(path)
    if list(df.columns) != ["id", TARGET]:
        raise ValueError(f"{path} bad columns: {list(df.columns)}")
    if len(df) != len(sample) or not df["id"].equals(sample["id"]):
        raise ValueError(f"{path} is not sample aligned")
    pred = df[TARGET].astype(float)
    if not np.isfinite(pred).all():
        raise ValueError(f"{path} non-finite predictions")
    df[TARGET] = pred.clip(0, 1)
    return df


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    for name, source in QUEUE:
        df = validate_source(source, sample)
        path = OUT / f"{name}.csv"
        df.to_csv(path, index=False)
        pred = df[TARGET]
        print(f"{path},{pred.min():.8f},{pred.max():.8f},{pred.mean():.8f},{pred.std():.8f},{pred.nunique()}")


if __name__ == "__main__":
    main()
