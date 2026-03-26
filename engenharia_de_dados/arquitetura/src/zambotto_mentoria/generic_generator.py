"""Generic synthetic generator driven by domain YAML configs."""

from __future__ import annotations

import logging
from datetime import date, datetime, time, timedelta
from random import Random
from typing import Any

import pandas as pd

from zambotto_mentoria.domain_config import DomainConfig, FieldConfig, GeneratorSpec, TableConfig

LOGGER = logging.getLogger(__name__)


class GenericDomainDataGenerator:
    """Generate domain datasets based on typed config models."""

    def __init__(self, config: DomainConfig) -> None:
        self.config = config
        self._random = Random(config.settings.seed)
        self._datasets: dict[str, pd.DataFrame] = {}
        self._value_dispatch = {
            "constant": self._generate_constant_value,
            "sequence": self._generate_sequence_value,
            "choice": self._generate_choice_value,
            "weighted_choice": self._generate_weighted_choice_value,
            "random_int": self._generate_random_int_value,
            "random_float": self._generate_random_float_value,
            "random_bool": self._generate_random_bool_value,
            "date_offset": self._generate_date_offset_value,
            "datetime_from_field": self._generate_datetime_from_field_value,
            "reference": self._generate_reference_value,
        }
        self._cast_dispatch = {
            "string": self._cast_string,
            "int": self._cast_int,
            "float": self._cast_float,
            "bool": self._cast_bool,
            "date": self._cast_date,
            "datetime": self._cast_datetime,
        }

    def generate(self) -> dict[str, pd.DataFrame]:
        """Generate all domain tables following declaration order."""
        for table in self.config.tables:
            row_count = self._resolve_row_count(table)
            rows = [self._generate_row(table, row_index) for row_index in range(row_count)]
            dataframe = pd.DataFrame(rows)
            typed_dataframe = self._apply_field_types(dataframe, table)
            self._datasets[table.name] = typed_dataframe

            LOGGER.debug(
                "Generated table",
                extra={
                    "domain": self.config.domain,
                    "table": table.name,
                    "rows": len(typed_dataframe),
                    "columns": list(typed_dataframe.columns),
                },
            )

        return self._datasets

    def _resolve_row_count(self, table: TableConfig) -> int:
        if table.rows is not None:
            return table.rows
        if table.rows_from_table is not None:
            if table.rows_from_table not in self._datasets:
                raise ValueError(
                    f"table '{table.name}' rows_from_table '{table.rows_from_table}' must be generated first"
                )
            return len(self._datasets[table.rows_from_table])
        return self.config.settings.default_rows

    def _generate_row(self, table: TableConfig, row_index: int) -> dict[str, Any]:
        row: dict[str, Any] = {}
        for field in table.fields:
            row[field.name] = self._generate_value(field, row_index, row)
        return row

    def _generate_value(
        self,
        field: FieldConfig,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        spec = field.generator
        handler = self._value_dispatch.get(spec.kind)
        if handler is None:
            raise ValueError(f"Unsupported generator kind: {spec.kind}")
        return handler(field=field, spec=spec, row_index=row_index, current_row=current_row)

    def _generate_constant_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, row_index, current_row
        return spec.value

    def _generate_sequence_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del current_row
        index_value = row_index + 1
        if field.field_type == "string":
            if spec.pad > 0:
                return f"{spec.prefix}{index_value:0{spec.pad}d}"
            return f"{spec.prefix}{index_value}"
        return index_value

    def _generate_choice_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, row_index, current_row
        return self._random.choice(spec.values or [])

    def _generate_weighted_choice_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, row_index, current_row
        values = spec.values or []
        weights = spec.weights or []
        return self._random.choices(values, weights=weights, k=1)[0]

    def _generate_random_int_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, row_index, current_row
        return self._random.randint(int(spec.min), int(spec.max))

    def _generate_random_float_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, row_index, current_row
        precision = spec.precision if spec.precision is not None else 2
        return round(self._random.uniform(float(spec.min), float(spec.max)), precision)

    def _generate_random_bool_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, spec, row_index, current_row
        return self._random.choice([True, False])

    def _generate_date_offset_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, row_index
        base_date = self._resolve_date_reference(spec, current_row)
        offset = self._random.randint(0, int(spec.max_days))
        return base_date + timedelta(days=offset)

    def _generate_datetime_from_field_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, row_index
        return self._resolve_datetime_from_field(spec, current_row)

    def _generate_reference_value(
        self,
        field: FieldConfig,
        spec: GeneratorSpec,
        row_index: int,
        current_row: dict[str, Any],
    ) -> Any:
        del field, current_row
        return self._resolve_reference_value(spec, row_index)

    def _resolve_date_reference(self, spec: GeneratorSpec, current_row: dict[str, Any]) -> date:
        reference = spec.from_reference
        if reference == "settings.start_date":
            return self.config.settings.start_date

        if reference and reference.startswith("field."):
            field_name = reference.split(".", maxsplit=1)[1]
            value = current_row.get(field_name)
            if isinstance(value, datetime):
                return value.date()
            if isinstance(value, date):
                return value
            raise ValueError(f"field reference '{reference}' must resolve to date or datetime")

        raise ValueError(f"Unsupported date reference: {reference}")

    def _resolve_datetime_from_field(self, spec: GeneratorSpec, current_row: dict[str, Any]) -> datetime:
        raw_value = current_row.get(spec.field or "")
        if isinstance(raw_value, datetime):
            return raw_value
        if isinstance(raw_value, date):
            return datetime.combine(raw_value, time.min)
        if raw_value is None:
            raise ValueError(f"datetime_from_field source is missing: {spec.field}")
        timestamp = pd.Timestamp(raw_value)
        return timestamp.to_pydatetime()

    def _resolve_reference_value(self, spec: GeneratorSpec, row_index: int) -> Any:
        table_name = spec.table or ""
        field_name = spec.field or ""

        if table_name not in self._datasets:
            raise ValueError(f"reference table '{table_name}' must be generated first")

        dataset = self._datasets[table_name]
        if field_name not in dataset.columns:
            raise ValueError(f"reference field '{field_name}' not found in table '{table_name}'")

        values = dataset[field_name].tolist()
        if not values:
            raise ValueError(f"reference table '{table_name}' has no rows")

        if spec.strategy == "aligned":
            return values[row_index % len(values)]
        return self._random.choice(values)

    def _apply_field_types(self, dataframe: pd.DataFrame, table: TableConfig) -> pd.DataFrame:
        typed = dataframe.copy()
        for field in table.fields:
            if field.name not in typed.columns:
                typed[field.name] = pd.Series(dtype="object")

            series = typed[field.name]
            typed[field.name] = self._cast_series(series, field)

        ordered_columns = [field.name for field in table.fields]
        return typed[ordered_columns]

    def _cast_series(self, series: pd.Series, field: FieldConfig) -> pd.Series:
        caster = self._cast_dispatch.get(field.field_type)
        if caster is None:
            raise ValueError(f"Unsupported field type: {field.field_type}")
        return caster(series=series, field=field)

    def _cast_string(self, series: pd.Series, field: FieldConfig) -> pd.Series:
        del field
        return series.astype("string")

    def _cast_int(self, series: pd.Series, field: FieldConfig) -> pd.Series:
        numeric = pd.to_numeric(series, errors="coerce")
        if field.nullable:
            return numeric.astype("Int64")
        return numeric.fillna(0).astype("int64")

    def _cast_float(self, series: pd.Series, field: FieldConfig) -> pd.Series:
        numeric = pd.to_numeric(series, errors="coerce")
        if field.nullable:
            return numeric.astype("Float64")
        return numeric.fillna(0.0).astype("float64")

    def _cast_bool(self, series: pd.Series, field: FieldConfig) -> pd.Series:
        if field.nullable:
            return series.astype("boolean")
        return series.fillna(False).astype(bool)

    def _cast_date(self, series: pd.Series, field: FieldConfig) -> pd.Series:
        date_series = pd.to_datetime(series, errors="coerce").dt.date
        if not field.nullable and date_series.isna().any():
            raise ValueError(f"non-nullable date field '{field.name}' has null values")
        return date_series

    def _cast_datetime(self, series: pd.Series, field: FieldConfig) -> pd.Series:
        datetime_series = pd.to_datetime(series, errors="coerce")
        if not field.nullable and datetime_series.isna().any():
            raise ValueError(f"non-nullable datetime field '{field.name}' has null values")
        return datetime_series
