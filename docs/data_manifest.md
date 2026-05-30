# Data Manifest

## Competition Files

The original competition files are downloaded from Kaggle and kept outside Git.

Expected local competition files:

| File | Purpose |
|---|---|
| `train.csv` | Training rows and target labels. |
| `test.csv` | Test rows for leaderboard submissions. |
| `sample_submission.csv` | Submission format reference. |

## Local Generated Artifacts

Generated artifacts are intentionally excluded from Git because they are large, reproducible, or competition-output files.

| Path pattern | Contents |
|---|---|
| `submissions/` | Generated submission CSVs. |
| `submissions_round*/` | Batch-specific generated submission CSVs. |
| `kaggle_code/` | Public Kaggle Code release sources for selected best-scoring submissions. |
| `public_outputs/` | Downloaded public notebook outputs used for blending experiments. |
| `outputs/` | Local model and notebook outputs. |
| `models/` | Trained model artifacts. |
| `runs/`, `wandb/` | Experiment tracker outputs. |

Current local public-output families include Flexon/Raunak plateau variants, Nina `hb5`/`hb10`/`hb11`, Masaya stacking artifacts, Giovanny 0.95446 output, refreshed Mikhail output, TabPFN output, CatBoost/XGBoost blend outputs, the Raunak/Flexon/Safar/Abdullah `s49` family, the May 19 Raunak/DataRegressor 0.95450 variants, the May 20 `s52`/advanced public-output variants, the May 21 `s53`/tail public-output variants, the May 22 DataRegressor/RealMLP/CatBoost-XGBoost public outputs, the May 23 Anthony/DataRegressor/Yekenot/Mirza/LightGBM/XGBoost public outputs, the May 24 Raunak/Rasulbek/RealMLP/LGBM ensemble public outputs, the May 25 Ray/Ruihao blend/model outputs, the May 26 Mikhail/Ray/Yekenot/Leonardo/LightGBM public outputs, the May 27 Anthony/Jayhawk/Djenk/Parth/Sarvesh/Zhenrui/Evgen/Maed/VH public outputs, the May 28 Anthony/Mikhail/Yeonseok/Alunji/Djenk/Evgen/Sarvesh/Parth/Koushik/Abbas/VH public outputs, the May 29 Sarvesh/Shamanth/Evgen/Parth/Sakuno/Fullmetal public outputs, and the May 30 Varad/Ruihao/Sarvesh/Jeff/Koushik/Yeonseok/Rakshit public outputs checked through 2026-05-30. These source files are kept local and are represented publicly only through score summaries and generation scripts.

## Public Records

Only compact summaries are tracked publicly:

| File | Contents |
|---|---|
| `docs/experiment_log.md` | Human-readable experiment notes and conclusions. |
| `docs/leaderboard_history.csv` | Compact public leaderboard score history. |
| `docs/round9_live_results.csv` | Compact record of the 2026-05-17 submission batch. |
| `docs/round10_live_results.csv` | Compact record of the 2026-05-18 submission batch. |
| `docs/round11_live_results.csv` | Compact record of the 2026-05-19 submission batch. |
| `docs/round12_live_results.csv` | Compact record of the 2026-05-20 submission batch. |
| `docs/round13_live_results.csv` | Compact record of the 2026-05-21 submission batch. |
| `docs/round14_live_results.csv` | Compact record of the 2026-05-22 submission batch. |
| `docs/round15_live_results.csv` | Compact record of the 2026-05-23 submission batch. |
| `docs/round16_live_results.csv` | Compact record of the 2026-05-24 submission batch. |
| `docs/round17_live_results.csv` | Compact record of the 2026-05-25 submission batch. |
| `docs/round18_live_results.csv` | Compact record of the 2026-05-26 submission batch. |
| `docs/round19_live_results.csv` | Compact record of the 2026-05-27 submission batch. |
| `docs/round20_live_results.csv` | Compact record of the 2026-05-28 submission batch. |
| `docs/round21_live_results.csv` | Compact record of the 2026-05-29 submission batch. |
| `docs/round22_live_results.csv` | Compact record of the 2026-05-30 submission batch. |
