"""Airflow DAG used in Session 02."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


def _extract_costs() -> None:
    """Simulates extraction from ad platforms."""


def _extract_events() -> None:
    """Simulates extraction from web/app events."""


def _build_daily_metrics() -> None:
    """Simulates daily transformation for conversion and ROI."""


def _publish_report() -> None:
    """Simulates final publish to BI layer."""


default_args = {
    "owner": "mentoria",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="marketing_orchestration_dag",
    description="DAG didática para sessão 02",
    default_args=default_args,
    schedule="0 7 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["mentoria", "marketing", "session-02"],
) as dag:
    extract_costs = PythonOperator(task_id="extract_costs", python_callable=_extract_costs)
    extract_events = PythonOperator(task_id="extract_events", python_callable=_extract_events)
    build_daily_metrics = PythonOperator(
        task_id="build_daily_metrics", python_callable=_build_daily_metrics
    )
    publish_report = PythonOperator(task_id="publish_report", python_callable=_publish_report)

    [extract_costs, extract_events] >> build_daily_metrics >> publish_report
