from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


ID_COL = "id"
TARGET_COL = "PitNextLap"


def read_prediction_frame(path):
    df = pd.read_csv(path)
    if ID_COL not in df.columns:
        raise ValueError(f"{path} does not contain an id column")
    value_cols = [col for col in df.columns if col != ID_COL]
    if not value_cols:
        raise ValueError(f"{path} does not contain a prediction column")
    target_col = TARGET_COL if TARGET_COL in df.columns else value_cols[0]
    df = df[[ID_COL, target_col]].rename(columns={target_col: TARGET_COL})
    if df[ID_COL].duplicated().any():
        raise ValueError(f"{path} contains duplicate ids")
    values = pd.to_numeric(df[TARGET_COL], errors="raise").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{path} contains non-finite predictions")
    df[TARGET_COL] = np.clip(values, 0.0, 1.0)
    return df


def find_sample_ids():
    candidates = [
        Path("/kaggle/input/playground-series-s6e5/sample_submission.csv"),
        Path("/kaggle/input/predicting-f1-pit-stops/sample_submission.csv"),
    ]
    for path in candidates:
        if path.exists():
            return pd.read_csv(path)[ID_COL]
    return None


def find_source(predicate, label, mean_range, std_range):
    root = Path("/kaggle/input")
    candidates = sorted(root.rglob("*.csv")) if root.exists() else []
    for path in candidates:
        text = str(path).lower()
        if not predicate(text):
            continue
        try:
            df = read_prediction_frame(path)
        except Exception:
            continue
        pred = df[TARGET_COL]
        if len(df) == 188165 and mean_range[0] < pred.mean() < mean_range[1] and std_range[0] < pred.std() < std_range[1]:
            return path, df
    raise FileNotFoundError(f"could not identify {label}")


def rank_norm(values):
    arr = np.asarray(values, dtype=float)
    return rankdata(arr, method="average") / len(arr)


def rank_remap(anchor, blended_rank):
    order = np.argsort(blended_rank, kind="mergesort")
    sorted_anchor = np.sort(np.asarray(anchor, dtype=float))
    out = np.empty(len(anchor), dtype=float)
    out[order] = sorted_anchor
    return out


def align_to_sample(df, sample_ids):
    if sample_ids is None or df[ID_COL].equals(sample_ids):
        return df
    return df.set_index(ID_COL).loc[sample_ids].reset_index()


def main():
    sample_ids = find_sample_ids()
    dataregressor_path, dataregressor = find_source(
        lambda text: "knock" in text or "azzam" in text,
        "DataRegressor submission",
        (0.2055, 0.2066),
        (0.3070, 0.3082),
    )
    jayhawk_path, jayhawk = find_source(
        lambda text: "jayhawk" in text or "stacking" in text,
        "Jayhawk stacking submission",
        (0.1960, 0.1990),
        (0.3020, 0.3055),
    )

    dataregressor = align_to_sample(dataregressor, sample_ids)
    jayhawk = align_to_sample(jayhawk, sample_ids)

    blended_rank = 0.999 * rank_norm(dataregressor[TARGET_COL]) + 0.001 * rank_norm(jayhawk[TARGET_COL])
    submission = dataregressor.copy()
    submission[TARGET_COL] = rank_remap(dataregressor[TARGET_COL], blended_rank)
    submission.to_csv("submission.csv", index=False)

    print("Generated submission.csv")
    print(f"dataregressor source: {dataregressor_path}")
    print(f"jayhawk source: {jayhawk_path}")
    print(f"rows: {len(submission)}")
    print(f"mean: {submission[TARGET_COL].mean():.8f}")
    print(f"std: {submission[TARGET_COL].std():.8f}")
    print(f"min: {submission[TARGET_COL].min():.8f}")
    print(f"max: {submission[TARGET_COL].max():.8f}")


if __name__ == "__main__":
    main()
