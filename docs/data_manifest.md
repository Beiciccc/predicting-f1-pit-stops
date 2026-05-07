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

## Public Records

Only compact summaries are tracked publicly:

| File | Contents |
|---|---|
| `docs/experiment_log.md` | Human-readable experiment notes and conclusions. |
| `docs/leaderboard_history.csv` | Compact public leaderboard score history. |
