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


def rank_max_blend(anchor, support, support_weight):
    r_anchor = normalized_rank(anchor)
    r_support = normalized_rank(support)
    blended_rank = np.maximum(r_anchor, r_support * support_weight)
    order = np.argsort(blended_rank, kind="mergesort")
    out = np.empty_like(anchor, dtype=float)
    out[order] = np.sort(anchor)
    return clip_pred(out)


def load_submission(path, sample_ids):
    df = pd.read_csv(path)
    if ID_COL not in df.columns:
        raise ValueError(f"{path} does not contain an id column")
    value_cols = [col for col in df.columns if col != ID_COL]
    target_col = TARGET_COL if TARGET_COL in df.columns else value_cols[0]
    df = df[[ID_COL, target_col]].rename(columns={target_col: TARGET_COL})
    if df[ID_COL].duplicated().any():
        raise ValueError(f"{path} contains duplicate ids")
    if not df[ID_COL].equals(sample_ids):
        df = df.set_index(ID_COL).loc[sample_ids].reset_index()
    pred = pd.to_numeric(df[TARGET_COL], errors="raise").to_numpy(dtype=float)
    if not np.isfinite(pred).all():
        raise ValueError(f"{path} contains non-finite predictions")
    return clip_pred(pred)


def find_competition_sample():
    candidates = [
        Path("/kaggle/input/playground-series-s6e5/sample_submission.csv"),
        Path("playground-series-s6e5/sample_submission.csv"),
    ]
    for path in candidates:
        if path.exists():
            return pd.read_csv(path)
    raise FileNotFoundError("sample_submission.csv was not found")


def find_blend_dataset():
    candidates = [
        Path("/kaggle/input/f1-submissions/blend_dataset"),
        Path("/kaggle/input/blend-dataset"),
        Path("/kaggle/input") / "blend_dataset",
        Path("public_outputs/raunak_blender_95452_20260520/outputs/diagnostics"),
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


def find_s52_file(sample_ids):
    candidates = []
    for root in [Path("/kaggle/input/pss6ep5448"), Path("/kaggle/input")]:
        if root.exists():
            candidates.extend(sorted(root.rglob("*.csv")))
    local = Path("public_outputs/raunak_blender_95452_20260520/outputs/max/s52_raw.csv")
    if local.exists():
        candidates.append(local)

    valid = []
    for path in candidates:
        path_text = str(path).lower()
        if "train" in path_text or "test" in path_text or "sample_submission" in path_text:
            continue
        try:
            pred = load_submission(path, sample_ids)
        except Exception:
            continue
        if len(pred) == len(sample_ids) and 0.2055 < pred.mean() < 0.2066 and 0.3070 < pred.std() < 0.3080:
            score_hint = 0
            if "092611" in path.name or "pss6ep5448" in path_text or "s52" in path.name.lower():
                score_hint = 1
            valid.append((score_hint, path, pred))
    if not valid:
        raise FileNotFoundError("could not identify the 0.95452 source file")
    valid.sort(key=lambda item: (item[0], str(item[1])), reverse=True)
    return valid[0][1], valid[0][2]


def load_rank_source(blend_dataset, sample_ids):
    rank_dir = blend_dataset / "public" / "rank_diverse"
    if not rank_dir.exists():
        raise FileNotFoundError("public/rank_diverse folder was not found")
    candidates = sorted(rank_dir.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError("no rank-diverse source files were found")
    path = candidates[-1]
    return path, load_submission(path, sample_ids)


def main():
    sample = find_competition_sample()
    sample_ids = sample[ID_COL]

    blend_dataset = find_blend_dataset()
    s52_path, s52_pred = find_s52_file(sample_ids)
    s46_path, s46_pred = load_rank_source(blend_dataset, sample_ids)

    final_pred = rank_max_blend(s52_pred, s46_pred, 0.98)
    submission = sample[[ID_COL]].copy()
    submission[TARGET_COL] = final_pred
    submission.to_csv("submission.csv", index=False)

    print("Generated submission.csv")
    print(f"s52 source: {s52_path}")
    print(f"rank source: {s46_path}")
    print(f"rows: {len(submission)}")
    print(f"mean: {submission[TARGET_COL].mean():.8f}")
    print(f"std: {submission[TARGET_COL].std():.8f}")
    print(f"min: {submission[TARGET_COL].min():.8f}")
    print(f"max: {submission[TARGET_COL].max():.8f}")


if __name__ == "__main__":
    main()
