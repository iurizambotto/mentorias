"""Helpers for loading and validating domain YAML configs."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

from zambotto_mentoria.domain_config import DomainConfig

LOGGER = logging.getLogger(__name__)


def load_domain_config(config_path: Path) -> DomainConfig:
    """Load one domain config from YAML file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as stream:
        raw_config = yaml.safe_load(stream)

    if not isinstance(raw_config, dict):
        raise ValueError("Domain config must be a YAML object at root")

    config = DomainConfig.model_validate(raw_config)
    LOGGER.debug(
        "Domain config loaded",
        extra={
            "config_path": str(config_path),
            "domain": config.domain,
            "tables": [table.name for table in config.tables],
        },
    )
    return config
