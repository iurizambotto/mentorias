"""Build tested assets for Session 03."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from zambotto_mentoria.config_loader import load_domain_config
from zambotto_mentoria.exporters import DatasetExporter
from zambotto_mentoria.generic_cdc import GenericCdcBuilder
from zambotto_mentoria.generic_generator import GenericDomainDataGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOGGER = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_CONFIG_PATH = PROJECT_ROOT / "config" / "domains" / "marketing.yaml"
OUTPUT_DIR = (
    PROJECT_ROOT
    / "docs"
    / "sessions"
    / "sessao-03-cdc-airflow-tabelas"
    / "exemplos"
    / "output"
)


def main() -> None:
    args = parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        LOGGER.debug("Debug logging enabled")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    domain_config = load_domain_config(DOMAIN_CONFIG_PATH)
    datasets = GenericDomainDataGenerator(domain_config).generate()

    if "events" not in datasets:
        raise ValueError("Session 03 requires an 'events' table in the domain YAML")

    event_exporter = DatasetExporter(formats=["csv", "jsonl", "parquet", "orc"])
    event_exporter.export(datasets={"events": datasets["events"]}, output_dir=OUTPUT_DIR)

    cdc_tables = GenericCdcBuilder().build_domain_events(domain_config, datasets)
    crm_cdc = cdc_tables.get("crm__cdc")
    if crm_cdc is None:
        raise ValueError("Session 03 requires CDC enabled for the 'crm' table")

    DatasetExporter(formats=["csv"]).export(
        datasets={"crm_cdc_events": crm_cdc},
        output_dir=OUTPUT_DIR,
    )

    LOGGER.info(
        "Session 03 assets generated",
        extra={
            "domain": domain_config.domain,
            "output_dir": str(OUTPUT_DIR),
            "events_rows": len(datasets["events"]),
            "cdc_rows": len(crm_cdc),
        },
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI args for troubleshooting options."""
    parser = argparse.ArgumentParser(description="Build session 03 example assets")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logs for troubleshooting",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
