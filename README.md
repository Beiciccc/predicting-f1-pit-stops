# Predicting F1 Pit Stops

Kaggle Playground Series S6E5 project for binary classification of Formula 1 pit stop outcomes.

Competition page: https://www.kaggle.com/competitions/playground-series-s6e5

## Repository Contents

- `docs/experiment_log.md` records public leaderboard experiments and conclusions.
- `docs/data_manifest.md` summarizes the competition files and generated artifacts used locally.
- `docs/leaderboard_history.csv` keeps a compact public leaderboard score table.
- `scripts/` contains reproducible utilities for status checks, blending, validation, and submission preparation.
- `*.ipynb` notebooks contain exploratory analysis and modeling experiments with outputs stripped for a lightweight public record.

Large Kaggle data files, generated submission CSVs, model artifacts, OOF predictions, and local credentials are excluded from the repository.

## Current Result

Best public leaderboard score recorded so far: `0.95450`.

Best submission family: Raunak `max46_05` and closely related 0.95450 public-output variants.

## Main Findings

- Public notebook blends around the Flexon 0.95410 family are the strongest current baseline.
- The `t85` variant improved the project best public score from `0.95403` to `0.95411`.
- A small rank blend of `t85`, Sohail 0.95411, and DeepLearnerrr improved the best public score to `0.95412`.
- The newer `s19` blender family lifted the best public score to `0.95419`.
- Additional Raunak and Anthony plateau variants preserved `0.95419`, but did not improve it.
- The later `s37` blender family lifted the best public score to `0.95437`.
- A Giovanny public output lifted the best direct score to `0.95446`, and a Giovanny/Mikhail/`s37` rank blend improved the project best to `0.95447`.
- The newer `s49` public-output family lifted the project best to `0.95449`; nearby `lr46/r46/c37/cc` variants tied it, while larger `d37/hb49` and `s49` rank blends were weaker.
- The May 19 `max46_05` public-output variant lifted the project best to `0.95450`; DataRegressor's one-line output and a very small `max46_05`/DataRegressor rank blend also reached `0.95450`.
- Several high-scoring public notebook outputs transfer well only as small perturbation sources, not as direct anchors.
- Older direct Mikhail outputs scored poorly, while the refreshed May 17 output reached `0.95438`; it is useful as a secondary blend source rather than a primary anchor.

## Data Policy

The original competition data should be downloaded from Kaggle by each user under Kaggle's competition terms. This repository tracks only code, documentation, and compact experiment records.
