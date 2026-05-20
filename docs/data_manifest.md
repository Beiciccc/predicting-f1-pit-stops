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
| `public_outputs/` | Downloaded public notebook outputs used for blending experiments. |
| `outputs/` | Local model and notebook outputs. |
| `models/` | Trained model artifacts. |
| `runs/`, `wandb/` | Experiment tracker outputs. |

Current local public-output families include Flexon/Raunak plateau variants, Nina `hb5`/`hb10`/`hb11`, Masaya stacking artifacts, Giovanny 0.95446 output, refreshed Mikhail output, TabPFN output, CatBoost/XGBoost blend outputs, the Raunak/Flexon/Safar/Abdullah `s49` family, the May 19 Raunak/DataRegressor 0.95450 variants, and the May 20 `s52`/advanced public-output variants checked through 2026-05-20. These source files are kept local and are represented publicly only through score summaries and generation scripts.

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
