"""Result models and export helpers (JSON / CSV / NDJSON)."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class AccountResult:
    """Outcome of provisioning a single account."""

    index: int
    email: str
    password: str
    username: str
    status: str = "pending"
    api_key: str | None = None
    api_key_name: str | None = None
    key_id: str | None = None
    balance: str | None = None
    error: str | None = None
    attempts: int = 0
    started_at: str = field(default_factory=_utc_now)
    finished_at: str | None = None

    def finish(self, status: str, *, error: str | None = None) -> None:
        self.status = status
        self.error = error
        self.finished_at = _utc_now()

    def to_dict(self) -> dict:
        return asdict(self)


class ResultStore:
    """Incrementally persists account results so a crash loses nothing."""

    def __init__(self, json_path: str | Path, csv_path: str | Path | None = None) -> None:
        self.json_path = Path(json_path)
        self.csv_path = Path(csv_path) if csv_path else None
        self.results: list[AccountResult] = []

    def add(self, result: AccountResult) -> None:
        self.results.append(result)
        self.flush()

    def update(self, result: AccountResult) -> None:
        self.flush()

    def flush(self) -> None:
        self.json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": _utc_now(),
            "total": len(self.results),
            "succeeded": sum(1 for r in self.results if r.status == "success"),
            "failed": sum(1 for r in self.results if r.status != "success"),
            "accounts": [r.to_dict() for r in self.results],
        }
        self.json_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        if self.csv_path is not None:
            self._write_csv(self.results)

    def _write_csv(self, results: Iterable[AccountResult]) -> None:
        rows = list(results)
        if not rows:
            return
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)  # type: ignore[union-attr]
        columns = [
            "index", "status", "email", "password", "api_key",
            "api_key_name", "balance", "error",
        ]
        with self.csv_path.open("w", newline="", encoding="utf-8") as handle:  # type: ignore[union-attr]
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            for result in rows:
                writer.writerow(result.to_dict())

    def summary(self) -> dict:
        succeeded = sum(1 for r in self.results if r.status == "success")
        return {
            "total": len(self.results),
            "succeeded": succeeded,
            "failed": len(self.results) - succeeded,
            "output": str(self.json_path),
            "csv": str(self.csv_path) if self.csv_path else None,
        }
