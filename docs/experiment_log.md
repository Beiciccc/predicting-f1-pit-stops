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
