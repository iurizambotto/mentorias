"""CLI integration test for domain data generation script."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generate_domain_data_cli_with_cdc(tmp_path: Path) -> None:
    output_dir = tmp_path / "generated"
    command = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "generate_domain_data.py"),
        "--config",
        str(PROJECT_ROOT / "config" / "domains" / "marketing.yaml"),
        "--output",
        str(output_dir),
        "--formats",
        "csv,jsonl",
        "--with-cdc",
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")

    result = subprocess.run(command, capture_output=True, text=True, env=env, check=False)

    assert result.returncode == 0, result.stderr
    assert (output_dir / "events.csv").exists()
    assert (output_dir / "events.jsonl").exists()
    assert (output_dir / "crm__cdc.csv").exists()
    assert (output_dir / "crm__cdc.jsonl").exists()
