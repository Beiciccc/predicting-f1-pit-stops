# Predicting F1 Pit Stops

Kaggle Playground Series S6E5 project for binary classification of Formula 1 pit stop outcomes.

Competition page: https://www.kaggle.com/competitions/playground-series-s6e5

## Repository Contents

- `docs/experiment_log.md` records public leaderboard experiments and conclusions.
- `docs/data_manifest.md` summarizes the competition files and generated artifacts used locally.
- `docs/leaderboard_history.csv` keeps a compact public leaderboard score table.
- `scripts/` contains reproducible utilities for status checks, blending, validation, and submission preparation.
- `kaggle_code/` contains public Kaggle Code release sources for selected best-scoring submissions.
- `*.ipynb` notebooks contain exploratory analysis and modeling experiments with outputs stripped for a lightweight public record.

Large Kaggle data files, generated submission CSVs, model artifacts, OOF predictions, and local credentials are excluded from the repository.

## Current Result

Best public leaderboard score recorded so far: `0.95454`.

Best submission family: May 23 Anthony/DataRegressor public-output variants.

Latest public Kaggle Code release: https://www.kaggle.com/code/beicicc/f1-pit-stops-dataregressor-20260522-0-95453

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
- The May 20 `s52` public-output family lifted the project best to `0.95452`; the asymmetric `max52_46_02` variant improved it further to `0.95453`.
- The May 21 `s53`/tail family repeatedly tied `0.95453`; older SRP/isotonic variants fell back to `0.95452`.
- The May 22 DataRegressor refresh and conservative blends around `max52`, `s53`, and `tail53` all tied `0.95453`, confirming a tight plateau.
- The May 23 Anthony/DataRegressor refresh lifted the project best to `0.95454`; blending it back toward older anchors diluted the gain.
- The May 24 Raunak `s54_raw` and Rasulbek best-seven outputs tied `0.95454`; Raunak's targeted `s54` micro-variants fell back to `0.95453`.
- The May 25 Ray/Ruihao direct blend outputs fell back to `0.95451-0.95452`; only tiny support weights preserved `0.95454`.
- The May 26 public outputs did not expose the new `0.95465+` leaderboard artifacts; Yekenot/Ruihao rank perturbations mostly preserved `0.95454`, with larger mixed shifts falling to `0.95453`.
- The May 27 public outputs again lacked a reproducible top-10 artifact; Jayhawk, Djenk, Parth, Sarvesh, and Mikhail tiny rank perturbations all preserved `0.95454` without improving it.
- The May 28 public outputs were also unable to reproduce the top-10 region; tiny Sarvesh, Evgen, Alunji, Parth, Yeonseok, and Mikhail rank perturbations preserved `0.95454` only.
- The May 29 public outputs did not reach the `0.95460` target; Sarvesh EDA direct transfer fell to `0.95382`, while small Sarvesh/Shamanth/Evgen rank-remaps only preserved `0.95454`.
- The May 30 public outputs again missed the `0.95460` target; Varad and Ruihao direct transfers were weak, and the best Sarvesh triple rank-remap tied `0.95454`.
- Several high-scoring public notebook outputs transfer well only as small perturbation sources, not as direct anchors.
- Older direct Mikhail outputs scored poorly, while the refreshed May 17 output reached `0.95438`; it is useful as a secondary blend source rather than a primary anchor.

## Data Policy

The original competition data should be downloaded from Kaggle by each user under Kaggle's competition terms. This repository tracks only code, documentation, and compact experiment records.
