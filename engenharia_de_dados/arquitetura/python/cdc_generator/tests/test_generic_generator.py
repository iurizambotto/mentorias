"""Tests for generic domain data generator."""

from __future__ import annotations

from pathlib import Path

from zambotto_mentoria.config_loader import load_domain_config
from zambotto_mentoria.generic_generator import GenericDomainDataGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generic_generator_creates_all_marketing_tables() -> None:
    config = load_domain_config(PROJECT_ROOT / "config" / "domains" / "marketing.yaml")

    datasets = GenericDomainDataGenerator(config).generate()

    assert set(datasets.keys()) == {"users", "campaigns", "events", "costs", "crm"}
    assert len(datasets["users"]) == 80
    assert len(datasets["crm"]) == 80
    assert datasets["crm"]["user_id"].nunique() == 80
    assert not datasets["events"].empty
    assert not datasets["costs"].empty
