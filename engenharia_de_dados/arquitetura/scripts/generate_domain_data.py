"""CLI to generate synthetic datasets from domain YAML config."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from zambotto_mentoria.config_loader import load_domain_config
from zambotto_mentoria.exporters import DatasetExporter, parse_formats
from zambotto_mentoria.generic_cdc import GenericCdcBuilder
from zambotto_mentoria.generic_generator import GenericDomainDataGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate synthetic datasets from YAML domain config")
    parser.add_argument("--config", required=True, help="Path to domain YAML config")
    parser.add_argument("--output", required=True, help="Output directory for generated files")
    parser.add_argument(
        "--formats",
        default="csv",
        help="Comma-separated formats: csv,jsonl,parquet,orc",
    )
    parser.add_argument(
        "--with-cdc",
        action="store_true",
        help="Generate CDC datasets for tables with CDC enabled",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and plan output files without writing",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logs for troubleshooting",
    )
    return parser.parse_args()


def main() -> None:
    """Generate datasets according to one domain YAML config."""
    args = parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        LOGGER.debug("Debug logging enabled")

    config_path = Path(args.config)
    output_dir = Path(args.output)

    domain_config = load_domain_config(config_path)
    generator = GenericDomainDataGenerator(domain_config)
    datasets = generator.generate()

    if args.with_cdc:
        cdc_builder = GenericCdcBuilder()
        cdc_datasets = cdc_builder.build_domain_events(domain_config, datasets)
        datasets = {**datasets, **cdc_datasets}

    exporter = DatasetExporter(formats=parse_formats(args.formats), dry_run=args.dry_run)
    written_paths = exporter.export(datasets=datasets, output_dir=output_dir)

    LOGGER.info(
        "Domain generation complete",
        extra={
            "domain": domain_config.domain,
            "tables": sorted(datasets.keys()),
            "output_dir": str(output_dir),
            "files_count": len(written_paths),
            "dry_run": args.dry_run,
        },
    )


if __name__ == "__main__":
    main()
