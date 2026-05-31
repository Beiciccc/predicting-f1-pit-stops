#!/usr/bin/env python3
"""Create the 2026-05-31 final-day submission candidates."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata


TARGET = "PitNextLap"
ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "playground-series-s6e5" / "sample_submission.csv"
TRAIN = ROOT / "playground-series-s6e5" / "train.csv"
TEST = ROOT / "playground-series-s6e5" / "test.csv"
OUT = ROOT / "submissions_round23"


SOURCES = {
    "dr23": ROOT / "submissions_round15/ag02_dataregressor_20260523_direct.csv",
    "an09": ROOT / "submissions_round22/an09_rank_dr23_sarvesh_triple30_98_02.csv",
    "s54": ROOT / "submissions_round16/ah01_s54_raw_direct.csv",
    "kk31": ROOT / "public_outputs/kkhandekar_lgbm_catb_xgb_20260531/submission.csv",
    "emanuell31": ROOT / "public_outputs/emanuellcs_catboost_20260531/submission.csv",
    "teamaker31": ROOT / "public_outputs/teamaker_optuna_xgb_lgbm_20260531/submission.csv",
    "evgen30": ROOT / "public_outputs/evgen_tabm_blend_20260530/submission.csv",
    "parth30": ROOT / "public_outputs/parth_cat_xgb_blend_20260530/submission.csv",
    "koushik30": ROOT / "public_outputs/koushik_prediction_20260530/submission.csv",
    "jeff_rank30": ROOT / "public_outputs/jeffbutt_ensemble_20260530/submission_own_rank_blend.csv",
    "masaya_l2_l1_c005": ROOT
    / "public_outputs/masaya_stacking_vibe_latest"
    / "submission_gpu_2layer_stack_base_l1_l2_logreg_l2_cuml_logreg_l1_C0p05_0.954462.csv",
}


RANK_BLEND_QUEUE = [
    ("ao01_rank_dr23_kk31_999_001", "dr23", {"dr23": 0.999, "kk31": 0.001}),
    ("ao02_rank_dr23_kk31_995_005", "dr23", {"dr23": 0.995, "kk31": 0.005}),
    ("ao03_rank_dr23_emanuell31_999_001", "dr23", {"dr23": 0.999, "emanuell31": 0.001}),
    ("ao04_rank_dr23_evgen30_999_001", "dr23", {"dr23": 0.999, "evgen30": 0.001}),
    ("ao05_rank_dr23_masaya_l2_999_001", "dr23", {"dr23": 0.999, "masaya_l2_l1_c005": 0.001}),
    ("ao06_rank_dr23_parth30_999_001", "dr23", {"dr23": 0.999, "parth30": 0.001}),
    ("ao07_rank_s54_kk31_999_001", "s54", {"s54": 0.999, "kk31": 0.001}),
    ("ao08_rank_dr23_consensus31_996_002_001_001", "dr23", {"dr23": 0.996, "kk31": 0.002, "emanuell31": 0.001, "evgen30": 0.001}),
    ("ao09_rank_dr23_teyrsp_999_001", "dr23", {"dr23": 0.999, "te_year_race_stint_tyre_pos": 0.001}),
    ("ao10_rank_dr23_jeffrank30_999_001", "dr23", {"dr23": 0.999, "jeff_rank30": 0.001}),
]


PROB_BLEND_QUEUE = [
    ("ao11_prob_dr23_an09_s54_equal", {"dr23": 1.0, "an09": 1.0, "s54": 1.0}),
    ("ao12_rank_dr23_kk_emanuell_masaya_997_001_001_001", "dr23", {"dr23": 0.997, "kk31": 0.001, "emanuell31": 0.001, "masaya_l2_l1_c005": 0.001}),
]


def load_source(path: Path, sample: pd.DataFrame) -> pd.Series:
    df = pd.read_csv(path)
    if "id" not in df.columns:
        raise ValueError(f"{path} does not contain id")
    pred_col = TARGET if TARGET in df.columns else [col for col in df.columns if col != "id"][0]
    df = df[["id", pred_col]].rename(columns={pred_col: TARGET})
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


def make_group_te_source(sample: pd.DataFrame) -> pd.Series:
    train = pd.read_csv(TRAIN)
    test = pd.read_csv(TEST)
    keys = ["Year", "Race", "Stint", "TyreLife", "Position"]
    global_mean = train[TARGET].mean()
    smooth = 3.0
    train_key = train[keys].astype(str).agg("\x1f".join, axis=1)
    test_key = test[keys].astype(str).agg("\x1f".join, axis=1)
    grouped = pd.DataFrame({"key": train_key, TARGET: train[TARGET]}).groupby("key")[TARGET].agg(["sum", "count"])
    means = (grouped["sum"] + global_mean * smooth) / (grouped["count"] + smooth)
    pred = test_key.map(means).fillna(global_mean).to_numpy(dtype=float)
    out = pd.Series(pred, index=test["id"], name=TARGET).loc[sample["id"]]
    return out.reset_index(drop=True)


def rank_norm(values: pd.Series | np.ndarray) -> np.ndarray:
    return rankdata(np.asarray(values, dtype=float), method="average") / len(values)


def rank_remap(anchor: pd.Series, weights: dict[str, float], preds: dict[str, pd.Series]) -> np.ndarray:
    total = sum(weights.values())
    blended = np.zeros(len(anchor), dtype=float)
    for source, weight in weights.items():
        blended += weight * rank_norm(preds[source])
    blended /= total
    order = np.argsort(blended, kind="mergesort")
    sorted_anchor = np.sort(anchor.to_numpy(dtype=float))
    out = np.empty(len(anchor), dtype=float)
    out[order] = sorted_anchor
    return out


def write_submission(name: str, pred: np.ndarray | pd.Series, sample: pd.DataFrame) -> Path:
    sub = sample.copy()
    sub[TARGET] = np.asarray(pred, dtype=float).clip(0, 1)
    path = OUT / f"{name}.csv"
    sub.to_csv(path, index=False)
    return path


def fingerprint(values: np.ndarray) -> str:
    return hashlib.md5(np.round(values, 12).tobytes()).hexdigest()


def previous_submission_hashes() -> dict[str, list[str]]:
    hashes: dict[str, list[str]] = {}
    for path in sorted(ROOT.glob("submissions*/**/*.csv")):
        if OUT in path.parents:
            continue
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if TARGET not in df.columns:
            continue
        arr = df[TARGET].astype(float).to_numpy()
        hashes.setdefault(fingerprint(arr), []).append(str(path.relative_to(ROOT)))
    return hashes


def source_summary(name: str, arr: np.ndarray, preds: dict[str, pd.Series]) -> str:
    return (
        f"{name},{arr.min():.8f},{arr.max():.8f},{arr.mean():.8f},{arr.std():.8f},"
        f"{np.corrcoef(preds['dr23'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(rank_norm(preds['dr23']), rank_norm(arr))[0, 1]:.10f},"
        f"{np.corrcoef(preds['an09'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['s54'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['kk31'], arr)[0, 1]:.10f},"
        f"{np.corrcoef(preds['emanuell31'], arr)[0, 1]:.10f}"
    )


def describe(path: Path, preds: dict[str, pd.Series], seen_hashes: dict[str, list[str]]) -> str:
    arr = pd.read_csv(path)[TARGET].astype(float).to_numpy()
    duplicate = "|".join(seen_hashes.get(fingerprint(arr), []))
    return f"{path},{source_summary(path.stem, arr, preds).split(',', 1)[1]},{duplicate}"


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("ao*.csv"):
        old.unlink()
    preds = {name: load_source(path, sample) for name, path in SOURCES.items()}
    preds["te_year_race_stint_tyre_pos"] = make_group_te_source(sample)
    seen_hashes = previous_submission_hashes()

    header = "source,min,max,mean,std,corr_dr23,rankcorr_dr23,corr_an09,corr_s54,corr_kk31,corr_emanuell31"
    print(header)
    for name, pred in preds.items():
        print(source_summary(name, pred.to_numpy(), preds))

    print(f"\ncreated,{header.split(',', 1)[1]},duplicate_previous")
    for name, anchor_source, weights in RANK_BLEND_QUEUE:
        final = rank_remap(preds[anchor_source], weights, preds)
        path = write_submission(name, final, sample)
        print(describe(path, preds, seen_hashes))

    for item in PROB_BLEND_QUEUE:
        if len(item) == 2:
            name, weights = item
            total = sum(weights.values())
            blended = np.zeros(len(sample), dtype=float)
            for source, weight in weights.items():
                blended += weight * preds[source].to_numpy(dtype=float)
            blended /= total
            path = write_submission(name, blended, sample)
        else:
            name, anchor_source, weights = item
            final = rank_remap(preds[anchor_source], weights, preds)
            path = write_submission(name, final, sample)
        print(describe(path, preds, seen_hashes))


if __name__ == "__main__":
    main()
