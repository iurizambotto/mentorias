"""Export helpers for generated datasets."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd

LOGGER = logging.getLogger(__name__)

SUPPORTED_FORMATS = {"csv", "jsonl", "parquet", "orc"}


class DatasetExporter:
    """Persist generated datasets to one or many formats."""

    def __init__(self, formats: Iterable[str], dry_run: bool = False) -> None:
        normalized_formats = [fmt.strip().lower() for fmt in formats if fmt.strip()]
        invalid_formats = sorted(set(normalized_formats) - SUPPORTED_FORMATS)
        if invalid_formats:
            raise ValueError(f"Unsupported export formats: {invalid_formats}")
        if not normalized_formats:
            raise ValueError("At least one export format must be provided")

        self.formats = normalized_formats
        self.dry_run = dry_run

    def export(self, datasets: Mapping[str, pd.DataFrame], output_dir: Path) -> list[Path]:
        """Write datasets and return generated file paths."""
        output_dir.mkdir(parents=True, exist_ok=True)
        written_paths: list[Path] = []

        for table_name, dataframe in datasets.items():
            for export_format in self.formats:
                destination = output_dir / f"{table_name}.{export_format}"
                if not self.dry_run:
                    self._write_one(dataframe, destination, export_format)

                written_paths.append(destination)
                LOGGER.info(
                    "Dataset export planned",
                    extra={
                        "table": table_name,
                        "format": export_format,
                        "path": str(destination),
                        "dry_run": self.dry_run,
                        "rows": len(dataframe),
                    },
                )

        return written_paths

    def _write_one(self, dataframe: pd.DataFrame, destination: Path, export_format: str) -> None:
        if export_format == "csv":
            dataframe.to_csv(destination, index=False)
            return

        if export_format == "jsonl":
            dataframe.to_json(destination, orient="records", lines=True, date_format="iso")
            return

        if export_format == "parquet":
            dataframe.to_parquet(destination, index=False)
            return

        if export_format == "orc":
            dataframe.to_orc(destination, index=False)
            return

        raise ValueError(f"Unsupported export format: {export_format}")


def parse_formats(raw_formats: str | None) -> list[str]:
    """Parse comma-separated export formats string."""
    if raw_formats is None:
        return ["csv"]
    return [fmt.strip().lower() for fmt in raw_formats.split(",") if fmt.strip()]
