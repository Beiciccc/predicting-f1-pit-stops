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

## 2026-05-13

Seventh batch started with no same-day submissions in the Kaggle submission list. The public leaderboard still had stronger private/non-reproducible entries, but no fresh public artifact was verified above the `0.95419` plateau. The batch tested the remaining Raunak direct variants, recent public notebook outputs, and small rank blends around `s19`.

| Round | File | Public score |
|---:|---|---:|
| 1 | `y01_raunak_pow_tb_direct.csv` | `0.95419` |
| 2 | `y02_raunak_log_s18_direct.csv` | `0.95419` |
| 3 | `y03_arun_blend_direct.csv` | `0.95416` |
| 4 | `y04_simarbir_direct.csv` | `0.95259` |
| 5 | `y05_degnonguidi12_direct.csv` | `0.94302` |
| 6 | `y06_anthony_res_direct.csv` | `0.95419` |
| 7 | `y07_rank_s19_arun_80_20.csv` | `0.95419` |
| 8 | `y11_rank_s19_joseph_97_03.csv` | `0.95416` |
| 9 | `y12_rank_s19_nikita_97_03.csv` | `0.95417` |
| 10 | `y13_rank_s19_sarvesh_99_01.csv` | `0.95419` |

Conclusion: the project best remains `0.95419`. Raunak `pow_tb` and `log_s18` are safe plateau variants, and Anthony residual is effectively another `s19`-level anchor. Direct Simarbir and Degnonguidi12 should be excluded after large public-score drops. Arun, Joseph, and Nikita can also hurt even at small direct or rank-blend weights; only very tiny Sarvesh-style perturbations preserved the plateau.

## 2026-05-16

Eighth batch started with no same-day submissions in the Kaggle submission list. The public leaderboard had moved above `0.9548`, and public Code exposed a new reproducible `0.95437` blender family. Safar, Flexon, Nawfeel, and Raunak `s37` outputs were effectively duplicates, so the batch focused on the Raunak `s37` family and its micro-variants.

| Round | File | Public score |
|---:|---|---:|
| 1 | `z01_raunak_s37_direct.csv` | `0.95437` |
| 2 | `z02_raunak_ex35_direct.csv` | `0.95437` |
| 3 | `z03_raunak_c35_direct.csv` | `0.95437` |
| 4 | `z04_raunak_r35_direct.csv` | `0.95437` |
| 5 | `z05_raunak_l35_direct.csv` | `0.95437` |
| 6 | `z06_raunak_log35_direct.csv` | `0.95437` |
| 7 | `z07_raunak_lc_direct.csv` | `0.95437` |
| 8 | `z08_raunak_hb37_direct.csv` | `0.95436` |
| 9 | `z09_raunak_r31_direct.csv` | `0.95437` |
| 10 | `z10_rank_s37_hb37_sohail_97_02_01.csv` | `0.95437` |

Conclusion: the project best improved from `0.95419` to `0.95437`. The `s37` anchor and most small/selective variants tie at the new plateau. The larger HB-style `hb37` perturbation is slightly weaker at `0.95436`, so future work should favor conservative `s37` micro-variants and look for genuinely new public anchors rather than larger row-wise blends.

## 2026-05-17

Ninth batch started with no same-day submissions in the Kaggle submission list. Recent public Code and leaderboard checks exposed two useful new anchors: a Giovanny rank-style output around the `0.95446` level and a refreshed Mikhail output that was no longer identical to the older direct-output failures. The batch first tested the new public anchor, then remaining conservative `s37` micro-variants, then Mikhail/Giovanny rank blends.

| Round | File | Public score |
|---:|---|---:|
| 1 | `aa01_giovanny_95446_direct.csv` | `0.95446` |
| 2 | `aa02_nina_hb10_direct.csv` | `0.95436` |
| 3 | `aa03_raunak_log31_direct.csv` | `0.95437` |
| 4 | `aa04_raunak_cc_direct.csv` | `0.95437` |
| 5 | `aa05_raunak_l31_direct.csv` | `0.95437` |
| 6 | `aa06_mikhail_latest_direct.csv` | `0.95438` |
| 7 | `aa07_rank_mikhail_giovanny_s37_70_20_10.csv` | `0.95444` |
| 8 | `aa08_rank_mikhail_giovanny_nina_85_10_05.csv` | `0.95441` |
| 9 | `aa09_rank_giovanny_mikhail_s37_70_20_10.csv` | `0.95447` |
| 10 | `aa10_rank_mikhail_karlton_giovanny_90_05_05.csv` | `0.95439` |

Conclusion: the project best improved from `0.95437` to `0.95447`. Giovanny is the strongest reproducible public anchor so far. The refreshed Mikhail direct output scored only `0.95438`, but it helped as a secondary rank source when Giovanny remained dominant. Nina `hb10` and the remaining `s37` micro-variants did not improve the plateau. Future work should keep Giovanny as the primary anchor and use only small, score-verified rank perturbations from Mikhail or other fresh public outputs.

## 2026-05-18

Tenth batch started with no same-day submissions in the Kaggle submission list. Recent public Code exposed a new `0.95449` family from Raunak/Flexon/Safar/Abdullah-style outputs. The downloaded `s49` files were exact numerical duplicates across several public notebooks, while Raunak also exposed nearby `lr46/r46/d37/hb49/c37/cc` variants.

| Round | File | Public score |
|---:|---|---:|
| 1 | `ab01_raunak_s49_direct.csv` | `0.95449` |
| 2 | `ab02_raunak_lr46_02_direct.csv` | `0.95449` |
| 3 | `ab03_raunak_r46_02_direct.csv` | `0.95449` |
| 4 | `ab04_raunak_r46_05_direct.csv` | `0.95449` |
| 5 | `ab05_raunak_d37_10_direct.csv` | `0.95448` |
| 6 | `ab06_raunak_hb49_direct.csv` | `0.95446` |
| 7 | `ab07_raunak_c37_direct.csv` | `0.95449` |
| 8 | `ab08_raunak_cc_direct.csv` | `0.95449` |
| 9 | `ab09_rank_s49_giovanny_mikhail_80_15_05.csv` | `0.95448` |
| 10 | `ab10_rank_s49_giovanny_mikhail_70_20_10.csv` | `0.95448` |

Conclusion: the project best improved from `0.95447` to `0.95449`. The `s49/lr46/r46/c37/cc` family ties at the new plateau. The larger `d37_10` and `hb49` perturbations are weaker, and adding Giovanny/Mikhail rank support also dropped to `0.95448`. Future public-score work should treat `s49` as the primary anchor, avoid larger hblend/d37 perturbations, and look for genuinely new public outputs above `0.95449`.

## 2026-05-19

Eleventh batch started with no same-day submissions in the Kaggle submission list. The newest public Code exposed a Raunak `0.95450` blender, Nina `hb11`, a refreshed Mikhail notebook output, and a DataRegressor one-line output. The refreshed Mikhail output was numerically unchanged from the prior public file, while Raunak `submission.csv` matched the new `max46_05` candidate.

| Round | File | Public score |
|---:|---|---:|
| 1 | `ac01_raunak_max46_05_direct.csv` | `0.95450` |
| 2 | `ac02_dataregressor_knock_direct.csv` | `0.95450` |
| 3 | `ac03_nina_hb11_direct.csv` | `0.95448` |
| 4 | `ac04_raunak_max31_05_direct.csv` | `0.95449` |
| 5 | `ac05_raunak_ex37_direct.csv` | `0.95449` |
| 6 | `ac06_raunak_r37_05_direct.csv` | `0.95449` |
| 7 | `ac07_raunak_d31_05_direct.csv` | `0.95448` |
| 8 | `ac08_raunak_d37_05_direct.csv` | `0.95449` |
| 9 | `ac09_raunak_min31_05_direct.csv` | `0.95447` |
| 10 | `ac10_rank_max46_dataregressor_98_02.csv` | `0.95450` |

Conclusion: the project best improved from `0.95449` to `0.95450`. The strongest candidates are Raunak `max46_05`, DataRegressor direct, and a very small `max46_05`/DataRegressor rank blend. Nina `hb11` did not transfer to `0.95450`, and the `max31/min31/d31` style perturbations were weaker. Future work should use `max46_05` as the primary public anchor and search for genuinely new public outputs above `0.95450`, not larger perturbations of the same family.

## 2026-05-20

Twelfth batch started with no same-day submissions in the Kaggle submission list. Recent public Code exposed a new `0.95452` family. Safar and Nawfeel direct outputs matched the Raunak `s52_raw` file exactly, while Kalyan `0.95450` matched the already-tested May 19 `max46_05` anchor. The batch therefore focused on non-duplicate `s52` variants and very small transformations around the new `s52` anchor.

| Round | File | Public score |
|---:|---|---:|
| 1 | `ad01_s52_raw_direct.csv` | `0.95452` |
| 2 | `ad02_lr52_46_01_direct.csv` | `0.95452` |
| 3 | `ad03_lr52_46_02_direct.csv` | `0.95452` |
| 4 | `ad04_d52_49_05_direct.csv` | `0.95452` |
| 5 | `ad05_max52_46_02_direct.csv` | `0.95453` |
| 6 | `ad06_pow52_49_10_direct.csv` | `0.95452` |
| 7 | `ad07_harm52_46_02_direct.csv` | `0.95452` |
| 8 | `ad08_geo52_46_02_direct.csv` | `0.95452` |
| 9 | `ad09_srp52_46_001_direct.csv` | `0.95452` |
| 10 | `ad10_gate52_49_top5_direct.csv` | `0.95452` |

Conclusion: the project best improved from `0.95450` to `0.95453`. The raw `s52` family is a reliable new public anchor at `0.95452`, and the asymmetric `max52_46_02` variant is the strongest tested file at `0.95453`. Other very small logit-rank, probability, harmonic, geometric, and gated variants preserved `0.95452` but did not beat the asymmetric max adjustment. Future work should treat `max52_46_02` as the primary anchor and search for additional independent public sources or extremely conservative perturbations around this file.

Public Code release: https://www.kaggle.com/code/beicicc/f1-pit-stops-max52-46-02-0-95453

## 2026-05-21

Thirteenth batch started with no same-day submissions in the Kaggle submission list. Recent public Code exposed a new `0.95453` tail-injection family. The batch first tested the new `s53` direct and tail variants, then extremely small blends around the prior `max52_46_02` best, and finally two unsubmitted advanced `s52` micro-variants.

| Round | File | Public score |
|---:|---|---:|
| 1 | `ae01_tail53_top_05_direct.csv` | `0.95453` |
| 2 | `ae02_s53_raw_direct.csv` | `0.95453` |
| 3 | `ae03_dataregressor_20260521_direct.csv` | `0.95453` |
| 4 | `ae04_tail53_dual_03_direct.csv` | `0.95453` |
| 5 | `ae05_tail53_bottom_05_direct.csv` | `0.95453` |
| 6 | `ae06_prob_max52_s53_99_01.csv` | `0.95453` |
| 7 | `ae07_prob_max52_datareg_99_01.csv` | `0.95453` |
| 8 | `ae08_rank_max52_s53_99_01.csv` | `0.95453` |
| 9 | `ae09_srp52_46_005_direct.csv` | `0.95452` |
| 10 | `ae10_iso52_46_02_direct.csv` | `0.95452` |

Conclusion: the project best remains `0.95453`. The new `s53` family, DataRegressor refresh, tail injections, and tiny `max52_46_02` blends all tie the current best without lifting it. The older `srp52_46_005` and `iso52_46_02` variants are weaker at `0.95452`. Future work should look for a genuinely new independent public source above `0.95453` or much more targeted tail/rank corrections, because the present plateau is very tight.

Public Code release: https://www.kaggle.com/code/beicicc/f1-pit-stops-tail53-top-05-0-95453

## 2026-05-22

Fourteenth batch started with no same-day submissions in the Kaggle submission list. Recent public Code did not expose a clearly stronger direct source; the only useful new signal was the May 22 DataRegressor one-line output. The batch therefore tested that direct output and conservative probability/rank perturbations around the existing `max52_46_02`, `s53`, and `tail53` anchors.

| Round | File | Public score |
|---:|---|---:|
| 1 | `af01_dataregressor_20260522_direct.csv` | `0.95453` |
| 2 | `af02_prob_max52_datareg22_995_005.csv` | `0.95453` |
| 3 | `af03_prob_max52_datareg22_99_01.csv` | `0.95453` |
| 4 | `af04_prob_s53_datareg22_995_005.csv` | `0.95453` |
| 5 | `af05_prob_tail53_datareg22_995_005.csv` | `0.95453` |
| 6 | `af06_rank_max52_datareg22_995_005.csv` | `0.95453` |
| 7 | `af07_rank_max52_datareg22_99_01.csv` | `0.95453` |
| 8 | `af08_rank_s53_datareg22_995_005.csv` | `0.95453` |
| 9 | `af09_prob_max52_s53_50_50.csv` | `0.95453` |
| 10 | `af10_prob_max52_tail53_50_50.csv` | `0.95453` |

Conclusion: the project best remains `0.95453`. The May 22 DataRegressor direct output, tiny DataRegressor perturbations, rank remaps, and midpoint blends between existing best anchors all tie the current plateau without improving it. Future work should wait for a genuinely new public output above the current family or focus on targeted tail/rank corrections with independent validation, because broad micro-blending around these anchors is saturated.

Public Code release: https://www.kaggle.com/code/beicicc/f1-pit-stops-dataregressor-20260522-0-95453

## 2026-05-25

Seventeenth batch started with no same-day submissions in the Kaggle submission list. Fresh public Code exposed Ray/Ruihao blend variants and several new model outputs, while the public leaderboard showed stronger private-team scores without a reproducible public artifact. The batch first tested the closest Ray/Ruihao direct blend files, then switched to very small perturbations around the May 23/24 `0.95454` anchor family after the direct files underperformed.

| Round | File | Public score |
|---:|---|---:|
| 1 | `ai01_ruihao_hb12_style_direct.csv` | `0.95452` |
| 2 | `ai02_ruihao_h_rank_direct.csv` | `0.95451` |
| 3 | `ai03_ruihao_best2_direct.csv` | `0.95452` |
| 4 | `ai04_prob_dr23_hb12_995_005.csv` | `0.95454` |
| 5 | `ai05_rank_dr23_hb12_995_005.csv` | `0.95454` |
| 6 | `ai06_prob_s54raw_hb12_995_005.csv` | `0.95454` |
| 7 | `ai07_prob_rasulbek_hb12_995_005.csv` | `0.95454` |
| 8 | `ai08_prob_s54rank_hb12_995_005.csv` | `0.95454` |
| 9 | `ai09_prob_dr23_hrank_999_001.csv` | `0.95454` |
| 10 | `ai10_prob_dr23_tyrelife_9995_0005.csv` | `0.95454` |

Conclusion: the project best remains `0.95454`. Ray/Ruihao direct blends are too aggressive despite very high correlation to the current anchor and should not be used directly. Small `0.5%` or smaller perturbations preserve the plateau but did not improve it. Future work should avoid direct transfer from these May 25 outputs and only test them as tiny support unless a new public artifact demonstrates a clear leaderboard lift.

Public Code release: https://www.kaggle.com/code/beicicc/f1-pit-stops-dataregressor-20260522-0-95453

## 2026-05-24

Sixteenth batch started with no same-day submissions in the Kaggle submission list. New public Code exposed Raunak's `s54` 0.95454 blender family and a near-identical Rasulbek best-seven blend. The batch tested the new direct `s54` files first, then conservative combinations with the May 23 DataRegressor/Anthony/Yekenot anchors.

| Round | File | Public score |
|---:|---|---:|
| 1 | `ah01_s54_raw_direct.csv` | `0.95454` |
| 2 | `ah02_s54_asym_core_direct.csv` | `0.95453` |
| 3 | `ah03_s54_ultra_narrow_direct.csv` | `0.95453` |
| 4 | `ah04_s54_micro_booster_direct.csv` | `0.95453` |
| 5 | `ah05_rasulbek_best7_direct.csv` | `0.95454` |
| 6 | `ah06_prob_dr23_s54raw_50_50.csv` | `0.95454` |
| 7 | `ah07_prob_ag08_s54raw_995_005.csv` | `0.95454` |
| 8 | `ah08_prob_dr23_rasulbek_50_50.csv` | `0.95454` |
| 9 | `ah09_rank_dr23_s54raw_50_50.csv` | `0.95454` |
| 10 | `ah10_rank_ag09_s54raw_995_005.csv` | `0.95454` |

Conclusion: the project best remains `0.95454`. Raunak `s54_raw`, Rasulbek `best7`, and several conservative combinations with the May 23 anchors all tie the current best. Raunak's `asym_core`, `ultra_narrow`, and `micro_booster` variants dropped to `0.95453`, so the raw `s54` file is the strongest usable variant from that family. Future work should keep the May 23/24 `0.95454` family as the primary anchor and avoid targeted micro-variants unless a new public source demonstrates a clear improvement.

Public Code release: https://www.kaggle.com/code/beicicc/f1-pit-stops-dataregressor-20260522-0-95453

## 2026-05-23

Fifteenth batch started with no same-day submissions in the Kaggle submission list. New public Code runs exposed a stronger Anthony residual-network output and a matching late DataRegressor one-line output. The batch prioritized those direct files, then tested whether conservative blends with the prior `max52_46_02`, `s53`, `tail53`, Yekenot PyTabKit, or a high-correlation Mirza Optuna variant could lift the new anchor.

| Round | File | Public score |
|---:|---|---:|
| 1 | `ag01_anthony_20260523_direct.csv` | `0.95454` |
| 2 | `ag02_dataregressor_20260523_direct.csv` | `0.95454` |
| 3 | `ag03_prob_max52_anth23_995_005.csv` | `0.95453` |
| 4 | `ag04_prob_s53_anth23_995_005.csv` | `0.95453` |
| 5 | `ag05_prob_tail53_anth23_995_005.csv` | `0.95453` |
| 6 | `ag06_rank_max52_anth23_995_005.csv` | `0.95453` |
| 7 | `ag07_rank_s53_anth23_995_005.csv` | `0.95453` |
| 8 | `ag08_prob_anth23_yekenot_pytab_995_005.csv` | `0.95454` |
| 9 | `ag09_rank_anth23_yekenot_pytab_995_005.csv` | `0.95454` |
| 10 | `ag10_mirza_sub8_optuna_direct.csv` | `0.95452` |

Conclusion: the project best improved from `0.95453` to `0.95454`. The Anthony and DataRegressor May 23 direct outputs are effectively the same new anchor and both scored `0.95454`. Mixing the new anchor back toward the prior `max52`, `s53`, or `tail53` files diluted the gain to `0.95453`, while tiny Yekenot PyTabKit support preserved `0.95454`. The Mirza Optuna variant was weaker at `0.95452`. Future work should treat the May 23 Anthony/DataRegressor output as the primary anchor and only test additions that preserve its distribution or provide genuinely new independent signal.

Public Code release: https://www.kaggle.com/code/beicicc/f1-pit-stops-dataregressor-20260522-0-95453
