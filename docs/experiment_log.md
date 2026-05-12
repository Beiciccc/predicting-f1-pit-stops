# Experiment Log

## 2026-05-05

Baseline and public-output blend experiments established a project best public leaderboard score of `0.95403`.

Key submissions:

| Submission | Public score | Notes |
|---|---:|---|
| `s01_sohail_direct` | `0.95402` | Strong public notebook output. |
| `s05_nina_sohail_rank_5050` | `0.95402` | Rank blend of two public outputs. |
| `s06_public_strong_rank` | `0.95403` | Best result from the first recorded batch. |

Conclusion: rank blending among strong public outputs was more stable than direct averaging.

## 2026-05-06

Second batch tested Mojjeed, Pilkwang, Roman, HGB, Leon, and Sohail blend variants. No submission improved the existing `0.95403` best.

Best result from this batch: `0.95368`.

Conclusion: Mojjeed, Pilkwang, and Roman variants did not transfer well enough to serve as primary anchors.

## 2026-05-07

Third batch focused on newer public notebook outputs, especially the Flexon 0.95410 blender family.

| Round | File | Public score |
|---:|---|---:|
| 1 | `u01_flexon_tb.csv` | `0.95410` |
| 2 | `u02_flexon_h01.csv` | `0.95410` |
| 3 | `u03_flexon_h02.csv` | `0.95410` |
| 4 | `u04_flexon_t95.csv` | `0.95410` |
| 5 | `u05_flexon_t85.csv` | `0.95411` |
| 6 | `u06_flexon_hm1.csv` | `0.95408` |
| 7 | `u07_flexon_hm2.csv` | `0.95409` |
| 8 | `u08_nina_hb4.csv` | `0.95409` |
| 9 | `u09_sohail_95407.csv` | `0.95407` |
| 10 | `u10_mikhail_updated.csv` | `0.95347` |

Conclusion: Flexon `t85` is the current project anchor. Future experiments should explore small rank-blend perturbations around `t85`, `tb`, `h01`, and `h02`, using Nina hb4 and Sohail 0.95407 as secondary sources.

## 2026-05-08

Fourth batch started with no same-day submissions in the Kaggle submission list. Recent public Code updates included Sohail 0.95411, DeepLearnerrr 0.95411, Abhishek 0.95410, Flexon pair-search variants, and a refreshed Mikhail run.

| Round | File | Public score |
|---:|---|---:|
| 1 | `v01_sohail_95411_direct.csv` | `0.95411` |
| 2 | `v02_deep_95411_direct.csv` | `0.95404` |
| 3 | `v03_abhishek_95410_direct.csv` | `0.94810` |
| 4 | `v04_mikhail_0508_direct.csv` | `0.95347` |
| 5 | `v05_flex_t925_direct.csv` | `0.95410` |
| 6 | `v06_flex_t975_direct.csv` | `0.95409` |
| 7 | `v07_flex_a40_direct.csv` | `0.95409` |
| 8 | `v08_flex_a60_direct.csv` | `0.95409` |
| 9 | `v09_rank_t85_sohail_deep.csv` | `0.95412` |
| 10 | `v10_rank_t85_tb_sohail_t925.csv` | `0.95411` |

Conclusion: the only improvement came from a small rank blend of Flexon `t85`, Sohail 0.95411, and DeepLearnerrr. Abhishek and Mikhail direct outputs should be excluded from future blends unless a new public score is verified by direct submission. Flexon pair-search variants did not improve over `t85`.

## 2026-05-11

Fifth batch started with no same-day submissions in the local timezone. The newest public Code and leaderboard scan showed a stronger 0.95419 blender family plus Masaya stacking artifacts. Kaggle records these submissions as 2026-05-10 23:xx UTC, which is 2026-05-11 00:xx BST.

| Round | File | Public score |
|---:|---|---:|
| 1 | `w01_flex_s19_direct.csv` | `0.95419` |
| 2 | `w02_flex_d02_direct.csv` | `0.95419` |
| 3 | `w03_flex_rtb02_direct.csv` | `0.95419` |
| 4 | `w04_flex_cs02_direct.csv` | `0.95419` |
| 5 | `w05_raunak_log_s11_direct.csv` | `0.95419` |
| 6 | `w06_raunak_geo_s11_direct.csv` | `0.95419` |
| 7 | `w07_nina_hb5_direct.csv` | `0.95419` |
| 8 | `w08_abd_s18_direct.csv` | `0.95418` |
| 9 | `w09_masaya_mlp32_direct.csv` | `0.95405` |
| 10 | `w10_rank_s19_masaya_gkanamoto.csv` | `0.95419` |

Conclusion: the `s19` family is the new public anchor at `0.95419`, but its micro-corrections mostly sit on the same plateau. Abdullah `s18` is slightly weaker at `0.95418`. Masaya's highest-CV stacking file did not transfer directly (`0.95405`), so it should not be used as a direct anchor.

## 2026-05-12

Sixth batch started with no same-day submissions in the Kaggle submission list. The newest leaderboard scan showed several private competitors above `0.95419`, but no reproducible public output above the known plateau. Recent public Code suggested a refreshed Mikhail ensemble and several unsubmitted Flexon/Raunak micro-variants, so this batch tested conservative plateau variants first, then used the refreshed Mikhail output as a direct probe.

| Round | File | Public score |
|---:|---|---:|
| 1 | `x01_flex_ex02_direct.csv` | `0.95419` |
| 2 | `x02_flex_cdn02_direct.csv` | `0.95419` |
| 3 | `x03_flex_cup02_direct.csv` | `0.95419` |
| 4 | `x04_flex_d01_direct.csv` | `0.95419` |
| 5 | `x05_rank_s19_nina_geo_72_16_12.csv` | `0.95419` |
| 6 | `x06_rank_s19_log_geo_nina_70_10_10_10.csv` | `0.95419` |
| 7 | `x07_mikhail_0512_direct.csv` | `0.95347` |
| 8 | `x08_flex_rs11_direct.csv` | `0.95419` |
| 9 | `x09_flex_t02_direct.csv` | `0.95419` |
| 10 | `x10_raunak_log_tb_direct.csv` | `0.95419` |

Conclusion: the public plateau remains `0.95419`. Flexon pro variants and conservative rank blends around `s19`, Nina `hb5`, and Raunak `log_s11/geo_s11/log_tb` are stable but did not improve the score. The refreshed Mikhail direct output again scored `0.95347`, so the Mikhail family should remain excluded as a direct anchor unless a new public artifact is proven by submission.
