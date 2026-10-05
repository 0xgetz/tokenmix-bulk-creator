#!/usr/bin/env python3
"""Programmatic example: create two accounts and print their API keys.

Run after installing the project:

    pip install -e .
    playwright install chromium
    python examples/create_accounts.py
"""

from __future__ import annotations

from tokenmix_bulk.config import RunConfig
from tokenmix_bulk.orchestrator import BulkCreator


def main() -> None:
    config = RunConfig(
        count=2,
        concurrency=1,
        key_name_prefix="demo",
        output="output/example_accounts.json",
        csv_output="output/example_accounts.csv",
        headless=False,
    )

    creator = BulkCreator(config)
    results = creator.run()

    print("\n=== results ===")
    for result in results:
        if result.status == "success":
            print(f"[{result.index}] {result.email} -> {result.api_key}")
        else:
            print(f"[{result.index}] {result.email} -> FAILED: {result.error}")


if __name__ == "__main__":
    main()
