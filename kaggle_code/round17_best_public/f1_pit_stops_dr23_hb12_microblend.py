from pathlib import Path

import numpy as np
import pandas as pd


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


def find_source(predicate, label):
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
        if len(df) == 188165 and 0.19 < pred.mean() < 0.21 and 0.29 < pred.std() < 0.32:
            return path, df
    raise FileNotFoundError(f"could not identify {label}")


def find_hb12_source():
    root = Path("/kaggle/input")
    preferred = []
    if root.exists():
        preferred.extend(sorted(root.rglob("hb12_style.csv")))
        preferred.extend(path for path in sorted(root.rglob("*.csv")) if "hb12" in str(path).lower())

    checked = set()
    for path in preferred:
        if path in checked:
            continue
        checked.add(path)
        try:
            df = read_prediction_frame(path)
        except Exception:
            continue
        pred = df[TARGET_COL]
        if len(df) == 188165 and 0.2050 < pred.mean() < 0.2060 and 0.3070 < pred.std() < 0.3080:
            return path, df
    raise FileNotFoundError("could not identify Ruihao hb12-style submission")


def main():
    sample_ids = find_sample_ids()
    dataregressor_path, dataregressor = find_source(
        lambda text: "knock" in text or "azzam" in text,
        "DataRegressor submission",
    )
    hb12_path, hb12 = find_hb12_source()

    if sample_ids is not None:
        if not dataregressor[ID_COL].equals(sample_ids):
            dataregressor = dataregressor.set_index(ID_COL).loc[sample_ids].reset_index()
        if not hb12[ID_COL].equals(sample_ids):
            hb12 = hb12.set_index(ID_COL).loc[sample_ids].reset_index()

    submission = dataregressor.copy()
    submission[TARGET_COL] = np.clip(
        0.995 * dataregressor[TARGET_COL].to_numpy(dtype=float)
        + 0.005 * hb12[TARGET_COL].to_numpy(dtype=float),
        0.0,
        1.0,
    )
    submission.to_csv("submission.csv", index=False)

    print("Generated submission.csv")
    print(f"dataregressor source: {dataregressor_path}")
    print(f"hb12 source: {hb12_path}")
    print(f"rows: {len(submission)}")
    print(f"mean: {submission[TARGET_COL].mean():.8f}")
    print(f"std: {submission[TARGET_COL].std():.8f}")
    print(f"min: {submission[TARGET_COL].min():.8f}")
    print(f"max: {submission[TARGET_COL].max():.8f}")


if __name__ == "__main__":
    main()
