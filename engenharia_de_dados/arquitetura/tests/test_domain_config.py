"""Tests for domain YAML config loading and validation."""

from __future__ import annotations

from pathlib import Path

from zambotto_mentoria.config_loader import load_domain_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_load_marketing_domain_config() -> None:
    config_path = PROJECT_ROOT / "config" / "domains" / "marketing.yaml"
    config = load_domain_config(config_path)

    table_names = [table.name for table in config.tables]
    assert config.domain == "marketing"
    assert {"users", "campaigns", "events", "costs", "crm"}.issubset(set(table_names))
    assert config.settings.days == 14
