#!/usr/bin/env python3
"""Print Kaggle competition status used at the start of each submission loop."""

from __future__ import annotations

import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo


COMPETITION = "playground-series-s6e5"
TZ = ZoneInfo("Europe/London")


def run_kaggle(args: list[str]) -> str:
    result = subprocess.run(
        ["kaggle", "competitions", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout.strip()


def main() -> None:
    now = datetime.now(TZ)
    print(f"Competition: {COMPETITION}")
    print(f"Local date: {now:%Y-%m-%d %H:%M:%S %Z}")
    print()

    print("Recent submissions:")
    print(run_kaggle(["submissions", "-c", COMPETITION]))
    print()

    print("Public leaderboard head:")
    print(run_kaggle(["leaderboard", "-c", COMPETITION, "--show"]))


if __name__ == "__main__":
    main()
