"""Tests for CDC lifecycle guarantees."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from zambotto_mentoria.config_loader import load_domain_config
from zambotto_mentoria.generic_cdc import GenericCdcBuilder
from zambotto_mentoria.generic_generator import GenericDomainDataGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_generic_cdc_respects_lifecycle_contract_for_all_tables() -> None:
    config = load_domain_config(PROJECT_ROOT / "config" / "domains" / "marketing.yaml")
    datasets = GenericDomainDataGenerator(config).generate()
    cdc_datasets = GenericCdcBuilder().build_domain_events(config, datasets)

    expected_tables = {f"{policy.table}__cdc" for policy in config.cdc}
    assert expected_tables.issubset(set(cdc_datasets.keys()))

    for policy in config.cdc:
        cdc_name = f"{policy.table}__cdc"
        cdc_df = cdc_datasets[cdc_name]

        assert not cdc_df.empty
        assert cdc_df.columns.tolist()[-3:] == ["cdc_op", "cdc_event_ts", "cdc_source_table"]

        grouped = cdc_df.groupby(policy.primary_key, dropna=False, sort=False)
        for _, entity_df in grouped:
            operations = entity_df[policy.operation_field].tolist()

            assert operations[0] == "insert"
            assert operations.count("insert") == 1

            delete_seen = False
            insert_seen = False
            for operation in operations:
                if operation == "insert":
                    assert not insert_seen
                    assert not delete_seen
                    insert_seen = True
                elif operation == "update":
                    assert insert_seen
                    assert not delete_seen
                elif operation == "delete":
                    assert insert_seen
                    assert not delete_seen
                    delete_seen = True
                else:
                    raise AssertionError(f"Unexpected operation: {operation}")

            if "delete" in operations:
                assert operations[-1] == "delete"
                delete_index = operations.index("delete")
                assert all(op not in {"insert", "update"} for op in operations[delete_index + 1 :])

            timestamps = pd.to_datetime(entity_df[policy.event_timestamp_field]).tolist()
            assert timestamps == sorted(timestamps)


def test_generic_cdc_generates_updates_for_repeated_ids() -> None:
    config = load_domain_config(PROJECT_ROOT / "config" / "domains" / "marketing.yaml")
    datasets = GenericDomainDataGenerator(config).generate()
    cdc_datasets = GenericCdcBuilder().build_domain_events(config, datasets)

    events_cdc = cdc_datasets["events__cdc"]
    costs_cdc = cdc_datasets["costs__cdc"]

    assert "update" in set(events_cdc["cdc_op"].unique())
    assert "update" in set(costs_cdc["cdc_op"].unique())
