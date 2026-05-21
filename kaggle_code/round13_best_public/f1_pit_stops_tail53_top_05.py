from pathlib import Path

import numpy as np
import pandas as pd


ID_COL = "id"
TARGET_COL = "PitNextLap"
CLIP_LOW = 1e-7
CLIP_HIGH = 1 - 1e-7


def clip_pred(values):
    return np.clip(np.asarray(values, dtype=float), CLIP_LOW, CLIP_HIGH)


def normalized_rank(values):
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.linspace(0.0, 1.0, len(values))
    return ranks


def logit_transform(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1.0 - p))


def sigmoid_transform(x):
    return 1.0 / (1.0 + np.exp(-x))


def logit_rank_blend(anchor, support, support_weight):
    anchor_rank = normalized_rank(anchor)
    support_rank = normalized_rank(support)
    blended_logit = (1.0 - support_weight) * logit_transform(anchor_rank)
    blended_logit += support_weight * logit_transform(support_rank)
    blended_rank = sigmoid_transform(blended_logit)

    order = np.argsort(blended_rank, kind="mergesort")
    out = np.empty_like(anchor, dtype=float)
    out[order] = np.sort(anchor)
    return clip_pred(out)


def tail_gated_blend(anchor, support, weight_high=0.05, upper_thresh=0.92):
    blended_high = logit_rank_blend(anchor, support, weight_high)
    out = anchor.copy()
    high_mask = anchor >= upper_thresh
    out[high_mask] = blended_high[high_mask]
    return clip_pred(out)


def read_prediction_frame(path):
    df = pd.read_csv(path)
    if ID_COL not in df.columns:
        raise ValueError(f"{path} does not contain an id column")
    value_cols = [col for col in df.columns if col != ID_COL]
    target_col = TARGET_COL if TARGET_COL in df.columns else value_cols[0]
    df = df[[ID_COL, target_col]].rename(columns={target_col: TARGET_COL})
    if df[ID_COL].duplicated().any():
        raise ValueError(f"{path} contains duplicate ids")
    df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors="raise")
    if not np.isfinite(df[TARGET_COL].to_numpy(dtype=float)).all():
        raise ValueError(f"{path} contains non-finite predictions")
    return df


def load_submission(path, sample_ids):
    df = read_prediction_frame(path)
    if not df[ID_COL].equals(sample_ids):
        df = df.set_index(ID_COL).loc[sample_ids].reset_index()
    return clip_pred(df[TARGET_COL].to_numpy(dtype=float))


def find_blend_dataset():
    candidates = [
        Path("/kaggle/input/f1-submissions/blend_dataset"),
        Path("/kaggle/input/blend-dataset"),
        Path("/kaggle/input") / "blend_dataset",
    ]
    for path in candidates:
        if (path / "public").exists() and (path / "ours").exists():
            return path
    root = Path("/kaggle/input")
    if root.exists():
        for path in sorted(root.rglob("*")):
            if path.is_dir() and (path / "public").exists() and (path / "ours").exists():
                return path
    raise FileNotFoundError("structured blend dataset was not found")


def find_s53_file():
    candidates = [
        Path("/kaggle/input/notebooks/anthonytherrien/predicting-f1-pit-stops-nn-residual-network/submission.csv"),
        Path("/kaggle/input/predicting-f1-pit-stops-nn-residual-network/submission.csv"),
        Path("public_outputs/anthony_nn_residual_20260521/submission.csv"),
        Path("public_outputs/raunak_blender_95453_20260521/outputs/max/s53_raw.csv"),
    ]
    for root in [Path("/kaggle/input"), Path(".")]:
        if root.exists():
            for path in sorted(root.rglob("submission.csv")):
                if "anthony" in str(path).lower() or "95453" in str(path).lower():
                    candidates.append(path)

    checked = set()
    for path in candidates:
        if path in checked or not path.exists():
            continue
        checked.add(path)
        try:
            df = read_prediction_frame(path)
        except Exception:
            continue
        pred = clip_pred(df[TARGET_COL].to_numpy(dtype=float))
        if len(pred) == 188165 and 0.2055 < pred.mean() < 0.2066 and 0.3070 < pred.std() < 0.3080:
            return path, df[ID_COL], pred
    raise FileNotFoundError("could not identify the 0.95453 source file")


def load_rank_source(blend_dataset, sample_ids):
    rank_dir = blend_dataset / "public" / "rank_diverse"
    candidates = sorted(rank_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError("no rank-diverse source files were found")
    path = candidates[-1]
    return path, load_submission(path, sample_ids)


def main():
    blend_dataset = find_blend_dataset()
    s53_path, sample_ids, s53_pred = find_s53_file()
    s46_path, s46_pred = load_rank_source(blend_dataset, sample_ids)

    final_pred = tail_gated_blend(s53_pred, s46_pred, weight_high=0.05, upper_thresh=0.92)
    submission = pd.DataFrame({ID_COL: sample_ids})
    submission[TARGET_COL] = final_pred
    submission.to_csv("submission.csv", index=False)

    print("Generated submission.csv")
    print(f"s53 source: {s53_path}")
    print(f"rank source: {s46_path}")
    print(f"rows: {len(submission)}")
    print(f"mean: {submission[TARGET_COL].mean():.8f}")
    print(f"std: {submission[TARGET_COL].std():.8f}")
    print(f"min: {submission[TARGET_COL].min():.8f}")
    print(f"max: {submission[TARGET_COL].max():.8f}")


if __name__ == "__main__":
    main()
