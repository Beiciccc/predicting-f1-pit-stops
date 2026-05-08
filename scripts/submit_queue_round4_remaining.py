#!/usr/bin/env python3
"""Submit the remaining 2026-05-08 recovery queue."""

from __future__ import annotations

from submit_queue_round4 import QUEUE, main


QUEUE[:] = [
    ("submissions_round4/v06_flex_t975_direct.csv", "r4_loop06_v06_flex_t975_direct"),
    ("submissions_round4/v07_flex_a40_direct.csv", "r4_loop07_v07_flex_a40_direct"),
    ("submissions_round4/v08_flex_a60_direct.csv", "r4_loop08_v08_flex_a60_direct"),
    ("submissions_round4/v09_rank_t85_sohail_deep.csv", "r4_loop09_v09_rank_t85_sohail_deep"),
    ("submissions_round4/v10_rank_t85_tb_sohail_t925.csv", "r4_loop10_v10_rank_t85_tb_sohail_t925"),
]


if __name__ == "__main__":
    raise SystemExit(main())
