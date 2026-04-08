"""Generic CDC event builder with per-ID lifecycle guarantees."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from random import Random
from typing import Any, Mapping, cast

import pandas as pd

from zambotto_mentoria.domain_config import CdcTablePolicy, ConditionRule, DomainConfig

LOGGER = logging.getLogger(__name__)


class GenericCdcBuilder:
    """Build CDC events honoring lifecycle rules for each primary key."""

    def build_domain_events(
        self,
        config: DomainConfig,
        datasets: Mapping[str, pd.DataFrame],
    ) -> dict[str, pd.DataFrame]:
        """Build CDC datasets for all enabled table policies."""
        cdc_datasets: dict[str, pd.DataFrame] = {}
        randomizer = Random(config.settings.seed)

        LOGGER.debug(
            "Starting CDC generation",
            extra={
                "domain": config.domain,
                "configured_policies": [policy.table for policy in config.cdc],
                "available_tables": sorted(datasets.keys()),
            },
        )

        for policy in config.cdc:
            if not policy.enabled:
                LOGGER.debug("Skipping disabled CDC policy", extra={"table": policy.table})
                continue

            source_df = datasets.get(policy.table)
            if source_df is None:
                raise ValueError(f"dataset for CDC table '{policy.table}' was not generated")

            cdc_name = f"{policy.table}__cdc"
            cdc_datasets[cdc_name] = self.build_table_events(policy=policy, source_df=source_df, rng=randomizer)

        return cdc_datasets

    def build_table_events(
        self,
        policy: CdcTablePolicy,
        source_df: pd.DataFrame,
        rng: Random,
    ) -> pd.DataFrame:
        """Build CDC events for one table policy."""
        self._validate_required_columns(policy, source_df)

        working_df = source_df.copy()
        sort_columns = [policy.primary_key, *policy.sort_fields]
        working_df = working_df.sort_values(sort_columns).reset_index(drop=True)

        all_events: list[dict[str, Any]] = []
        sample_sequences: list[dict[str, Any]] = []

        grouped = working_df.groupby(policy.primary_key, sort=False, dropna=False)
        for entity_id, group_df in grouped:
            entity_events = self._build_events_for_entity(policy=policy, entity_id=entity_id, group_df=group_df, rng=rng)
            self._validate_entity_lifecycle(policy=policy, entity_id=entity_id, entity_events=entity_events)
            all_events.extend(entity_events)

            if len(sample_sequences) < 5:
                sample_sequences.append(
                    {
                        "id": str(entity_id),
                        "operations": [event[policy.operation_field] for event in entity_events],
                    }
                )

        result = pd.DataFrame(all_events)
        if result.empty:
            LOGGER.debug("CDC output is empty", extra={"table": policy.table})
            return result

        final_sort_columns = [policy.primary_key, policy.event_timestamp_field, policy.operation_field]
        result = result.sort_values(final_sort_columns).reset_index(drop=True)
        result = self._ensure_cdc_fields_at_tail(policy=policy, dataframe=result)

        op_counts = self._get_column_series(result, policy.operation_field).value_counts().to_dict()
        ids_count = self._count_unique_ids(result, policy.primary_key)
        LOGGER.debug(
            "CDC events generated",
            extra={
                "table": policy.table,
                "rows": len(result),
                "ids": ids_count,
                "op_counts": op_counts,
                "sample_sequences": sample_sequences,
            },
        )
        return result

    def _build_events_for_entity(
        self,
        policy: CdcTablePolicy,
        entity_id: Any,
        group_df: pd.DataFrame,
        rng: Random,
    ) -> list[dict[str, Any]]:
        rows = group_df.to_dict(orient="records")
        if not rows:
            return []

        first_row = rows[0]
        first_ts = self._coerce_timestamp(first_row[policy.source_timestamp_field], policy)
        events = [
            self._build_event_payload(
                payload=first_row,
                policy=policy,
                operation="insert",
                event_ts=first_ts,
            )
        ]

        last_ts = first_ts
        if policy.allow_update:
            for row in rows[1:]:
                if not self._matches_condition(payload=row, rule=policy.update_when):
                    continue

                source_ts = self._coerce_timestamp(row[policy.source_timestamp_field], policy)
                candidate_ts = source_ts + timedelta(seconds=policy.update_offset_seconds)
                update_ts = self._next_timestamp(candidate_ts, last_ts)

                events.append(
                    self._build_event_payload(
                        payload=row,
                        policy=policy,
                        operation="update",
                        event_ts=update_ts,
                    )
                )
                last_ts = update_ts

        should_delete = policy.allow_delete and self._should_delete(policy=policy, payload=rows[-1], rng=rng)
        if should_delete:
            delete_base_ts = self._coerce_timestamp(rows[-1][policy.source_timestamp_field], policy)
            delete_candidate_ts = delete_base_ts + timedelta(seconds=policy.delete_offset_seconds)
            delete_ts = self._next_timestamp(delete_candidate_ts, last_ts)

            events.append(
                self._build_event_payload(
                    payload=rows[-1],
                    policy=policy,
                    operation="delete",
                    event_ts=delete_ts,
                )
            )

        return events

    def _validate_entity_lifecycle(
        self,
        policy: CdcTablePolicy,
        entity_id: Any,
        entity_events: list[dict[str, Any]],
    ) -> None:
        if not entity_events:
            raise ValueError(f"Entity '{entity_id}' in table '{policy.table}' has no CDC events")

        op_field = policy.operation_field
        operations = [event[op_field] for event in entity_events]

        if policy.enforce_insert_first and operations[0] != "insert":
            raise ValueError(
                f"Invalid CDC sequence for table '{policy.table}', id '{entity_id}': first op must be insert"
            )

        if operations.count("insert") != 1:
            raise ValueError(
                f"Invalid CDC sequence for table '{policy.table}', id '{entity_id}': expected one insert"
            )

        delete_seen = False
        for index, operation in enumerate(operations):
            if delete_seen:
                if not policy.allow_reinsert_after_delete:
                    raise ValueError(
                        "Invalid CDC sequence for table "
                        f"'{policy.table}', id '{entity_id}': operation '{operation}' appears after delete"
                    )

            if operation == "insert" and index != 0:
                raise ValueError(
                    f"Invalid CDC sequence for table '{policy.table}', id '{entity_id}': insert must be first"
                )

            if operation == "delete":
                if delete_seen:
                    raise ValueError(
                        f"Invalid CDC sequence for table '{policy.table}', id '{entity_id}': duplicated delete"
                    )
                delete_seen = True

        if policy.enforce_terminal_delete and delete_seen and operations[-1] != "delete":
            raise ValueError(
                f"Invalid CDC sequence for table '{policy.table}', id '{entity_id}': delete must be terminal"
            )

    def _should_delete(self, policy: CdcTablePolicy, payload: Mapping[str, Any], rng: Random) -> bool:
        condition_match = self._matches_condition(payload=payload, rule=policy.delete_when)

        if policy.delete_strategy == "condition":
            return condition_match

        probability = policy.delete_probability if policy.delete_probability is not None else 0.0
        probability_match = rng.random() < probability

        if policy.delete_strategy == "probability":
            return probability_match

        if policy.delete_strategy == "condition_or_probability":
            return condition_match or probability_match

        raise ValueError(f"Unsupported delete_strategy: {policy.delete_strategy}")

    def _matches_condition(self, payload: Mapping[str, Any], rule: ConditionRule | None) -> bool:
        if rule is None:
            return True

        value = payload.get(rule.field)
        if rule.equals is not None:
            return value == rule.equals
        if rule.not_equals is not None:
            return value != rule.not_equals
        if rule.in_values is not None:
            return value in rule.in_values
        return False

    def _validate_required_columns(self, policy: CdcTablePolicy, source_df: pd.DataFrame) -> None:
        required = {policy.primary_key, policy.source_timestamp_field, *policy.sort_fields}
        missing = required - set(source_df.columns)
        if missing:
            missing_list = sorted(missing)
            raise ValueError(f"table '{policy.table}' missing columns for CDC: {missing_list}")

    def _build_event_payload(
        self,
        payload: Mapping[str, Any],
        policy: CdcTablePolicy,
        operation: str,
        event_ts: datetime,
    ) -> dict[str, Any]:
        event = dict(payload)
        event[policy.operation_field] = operation
        event[policy.event_timestamp_field] = event_ts
        event["cdc_source_table"] = policy.table
        return event

    def _ensure_cdc_fields_at_tail(self, policy: CdcTablePolicy, dataframe: pd.DataFrame) -> pd.DataFrame:
        cdc_tail = [policy.operation_field, policy.event_timestamp_field, "cdc_source_table"]
        base_columns = [column for column in dataframe.columns if column not in cdc_tail]
        ordered_columns = base_columns + cdc_tail
        return cast(pd.DataFrame, dataframe.reindex(columns=ordered_columns))

    def _get_column_series(self, dataframe: pd.DataFrame, column_name: str) -> pd.Series:
        column_data = dataframe.loc[:, column_name]
        if isinstance(column_data, pd.DataFrame):
            return column_data.iloc[:, 0]
        return column_data

    def _count_unique_ids(self, dataframe: pd.DataFrame, column_name: str) -> int:
        series = self._get_column_series(dataframe, column_name).astype("string")
        return int(series.nunique())

    def _coerce_timestamp(self, value: Any, policy: CdcTablePolicy) -> datetime:
        if value is None:
            raise ValueError(
                f"source timestamp field '{policy.source_timestamp_field}' is null for table '{policy.table}'"
            )
        timestamp = pd.Timestamp(value).to_pydatetime()
        if not isinstance(timestamp, datetime):
            raise ValueError(
                f"source timestamp field '{policy.source_timestamp_field}' has invalid type for table '{policy.table}'"
            )
        return timestamp

    def _next_timestamp(self, candidate: datetime, last_timestamp: datetime) -> datetime:
        if candidate > last_timestamp:
            return candidate
        return last_timestamp + timedelta(seconds=1)
