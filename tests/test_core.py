"""Offline unit tests for the pure-logic modules."""

from __future__ import annotations

import json

import pytest

from tokenmix_bulk.config import RunConfig
from tokenmix_bulk.identity import (
    random_email,
    random_key_name,
    random_password,
    random_username,
)
from tokenmix_bulk.results import AccountResult, ResultStore


def test_random_password_policy():
    for _ in range(50):
        pw = random_password(16)
        assert len(pw) == 16
        assert any(c.islower() for c in pw)
        assert any(c.isupper() for c in pw)
        assert any(c.isdigit() for c in pw)


def test_random_password_rejects_short():
    with pytest.raises(ValueError):
        random_password(4)


def test_random_username_and_email():
    username = random_username()
    assert "." in username
    email = random_email("example.com", "swift.falcon")
    assert email.startswith("swift.falcon.")
    assert email.endswith("@example.com")


def test_random_key_name_prefix():
    name = random_key_name("ci")
    assert name.startswith("ci-")
    assert len(name.split("-")) == 4


def test_config_roundtrip(tmp_path):
    config = RunConfig(count=3, concurrency=2, headless=True)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config.to_dict()), encoding="utf-8")
    loaded = RunConfig.from_file(path)
    assert loaded.count == 3
    assert loaded.concurrency == 2
    assert loaded.headless is True


def test_config_keeps_unknown_keys():
    config = RunConfig.from_dict({"count": 1, "mystery": "value"})
    assert config.extra["mystery"] == "value"


def test_result_store_exports(tmp_path):
    store = ResultStore(tmp_path / "a.json", tmp_path / "a.csv")
    ok = AccountResult(index=1, email="a@b.c", password="x", username="u")
    ok.api_key = "sk-tm-test"
    ok.finish("success")
    bad = AccountResult(index=2, email="d@e.f", password="y", username="v")
    bad.finish("failed", error="boom")
    store.add(ok)
    store.add(bad)

    payload = json.loads((tmp_path / "a.json").read_text(encoding="utf-8"))
    assert payload["succeeded"] == 1
    assert payload["failed"] == 1
    csv_text = (tmp_path / "a.csv").read_text(encoding="utf-8")
    assert "sk-tm-test" in csv_text
    assert "boom" in csv_text
