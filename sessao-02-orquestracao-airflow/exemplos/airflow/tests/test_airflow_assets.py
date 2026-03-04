"""Asset-level checks for Session 02 Airflow files."""

from __future__ import annotations

from pathlib import Path


def test_compose_has_core_services() -> None:
    compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    content = compose_path.read_text(encoding="utf-8")

    assert "airflow-webserver" in content
    assert "airflow-scheduler" in content
    assert "postgres" in content


def test_dag_has_expected_tasks() -> None:
    dag_path = Path(__file__).parent.parent / "dags" / "marketing_orchestration_dag.py"
    content = dag_path.read_text(encoding="utf-8")

    assert "marketing_orchestration_dag" in content
    assert "extract_costs" in content
    assert "extract_events" in content
    assert "build_daily_metrics" in content
    assert "publish_report" in content
