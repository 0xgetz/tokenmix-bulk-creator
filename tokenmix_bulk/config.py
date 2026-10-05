"""Run configuration: defaults, dataclass and YAML/JSON loading."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://api.tokenmix.ai"
DEFAULT_SITE_URL = "https://tokenmix.ai"
DEFAULT_MAIL_BASE_URL = "https://api.mail.tm"


@dataclass
class RunConfig:
    """Everything the orchestrator needs to perform a bulk run."""

    count: int = 1
    concurrency: int = 1
    password: str | None = None
    key_name_prefix: str | None = None
    referral_code: str | None = None
    mail_domain: str | None = None
    base_url: str = DEFAULT_BASE_URL
    site_url: str = DEFAULT_SITE_URL
    mail_base_url: str = DEFAULT_MAIL_BASE_URL
    output: str = "accounts.json"
    csv_output: str | None = "accounts.csv"
    headless: bool = False
    browser: str = "chromium"
    timeout: float = 180.0
    page_timeout: float = 60.0
    code_timeout: float = 150.0
    retries: int = 2
    stop_on_error: bool = False
    verbose: bool = False
    proxy: str | None = None
    user_agent: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunConfig":
        known = {f for f in cls.__dataclass_fields__}  # type: ignore[attr-defined]
        payload = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        config = cls(**payload)
        config.extra = extra
        return config

    @classmethod
    def from_file(cls, path: str | Path) -> "RunConfig":
        text = Path(path).read_text(encoding="utf-8")
        if str(path).endswith((".yaml", ".yml")):
            try:
                import yaml  # type: ignore
            except ImportError as exc:  # pragma: no cover - optional dependency
                raise RuntimeError(
                    "PyYAML is required to read YAML config files "
                    "(pip install pyyaml) or use JSON instead"
                ) from exc
            return cls.from_dict(yaml.safe_load(text) or {})
        return cls.from_dict(json.loads(text))
