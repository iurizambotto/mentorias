"""Typed models for domain-driven synthetic generation configs."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

FieldType = Literal["string", "int", "float", "bool", "date", "datetime"]
GeneratorKind = Literal[
    "constant",
    "sequence",
    "choice",
    "weighted_choice",
    "random_int",
    "random_float",
    "random_bool",
    "date_offset",
    "datetime_from_field",
    "reference",
]


class ConditionRule(BaseModel):
    """Conditional rule used by CDC policies."""

    field: str
    equals: Any | None = None
    not_equals: Any | None = None
    in_values: list[Any] | None = None

    @model_validator(mode="after")
    def validate_condition(self) -> "ConditionRule":
        """Ensure one and only one condition operator is provided."""
        checks = [self.equals is not None, self.not_equals is not None, self.in_values is not None]
        if sum(checks) != 1:
            raise ValueError("ConditionRule requires exactly one of: equals, not_equals, in_values")
        if self.in_values is not None and not self.in_values:
            raise ValueError("in_values must not be empty")
        return self


class GeneratorSpec(BaseModel):
    """Generator behavior for one field."""

    kind: GeneratorKind
    value: Any | None = None
    values: list[Any] | None = None
    weights: list[float] | None = None
    min: float | int | None = None
    max: float | int | None = None
    precision: int | None = Field(default=2, ge=0)
    prefix: str = ""
    pad: int = Field(default=0, ge=0)
    from_reference: str | None = Field(default=None, alias="from")
    max_days: int | None = Field(default=None, ge=0)
    field: str | None = None
    table: str | None = None
    strategy: Literal["random", "aligned"] = "random"

    @model_validator(mode="after")
    def validate_by_kind(self) -> "GeneratorSpec":
        """Validate required parameters according to generator kind."""
        validators = {
            "constant": self._validate_constant,
            "choice": self._validate_choice,
            "weighted_choice": self._validate_weighted_choice,
            "random_int": self._validate_random_range,
            "random_float": self._validate_random_range,
            "date_offset": self._validate_date_offset,
            "datetime_from_field": self._validate_datetime_from_field,
            "reference": self._validate_reference,
        }
        validator = validators.get(self.kind)
        if validator is not None:
            validator()

        return self

    def _validate_constant(self) -> None:
        if self.value is None:
            raise ValueError("constant generator requires 'value'")

    def _validate_choice(self) -> None:
        if not self.values:
            raise ValueError("choice generator requires non-empty 'values'")

    def _validate_weighted_choice(self) -> None:
        if not self.values or not self.weights:
            raise ValueError("weighted_choice requires 'values' and 'weights'")
        if len(self.values) != len(self.weights):
            raise ValueError("weighted_choice requires same length for 'values' and 'weights'")

    def _validate_random_range(self) -> None:
        if self.min is None or self.max is None:
            raise ValueError(f"{self.kind} requires both 'min' and 'max'")
        if float(self.min) > float(self.max):
            raise ValueError("'min' must be lower than or equal to 'max'")

    def _validate_date_offset(self) -> None:
        if self.from_reference is None:
            raise ValueError("date_offset requires 'from'")
        if self.max_days is None:
            raise ValueError("date_offset requires 'max_days'")

    def _validate_datetime_from_field(self) -> None:
        if not self.field:
            raise ValueError("datetime_from_field requires 'field'")

    def _validate_reference(self) -> None:
        if not self.table or not self.field:
            raise ValueError("reference requires both 'table' and 'field'")


class FieldConfig(BaseModel):
    """Schema definition for one table field."""

    name: str
    field_type: FieldType = Field(alias="type")
    nullable: bool = False
    generator: GeneratorSpec


class CdcTablePolicy(BaseModel):
    """CDC policy for one source table."""

    table: str
    enabled: bool = True
    primary_key: str
    source_timestamp_field: str
    event_timestamp_field: str = "event_ts"
    operation_field: str = "op"
    sort_fields: list[str] = Field(default_factory=list)
    allow_update: bool = True
    allow_delete: bool = False
    delete_strategy: Literal["condition", "probability", "condition_or_probability"] = "condition"
    delete_probability: float | None = None
    update_when: ConditionRule | None = None
    delete_when: ConditionRule | None = None
    update_offset_seconds: int = 1
    delete_offset_seconds: int = 2
    allow_reinsert_after_delete: bool = False
    enforce_insert_first: bool = True
    enforce_terminal_delete: bool = True

    @model_validator(mode="after")
    def validate_offsets(self) -> "CdcTablePolicy":
        """Validate CDC lifecycle policy constraints."""
        if not self.sort_fields:
            self.sort_fields = [self.source_timestamp_field]

        if self.allow_delete and self.delete_offset_seconds < self.update_offset_seconds:
            raise ValueError("delete_offset_seconds must be >= update_offset_seconds")

        if self.delete_probability is not None and not (0.0 <= self.delete_probability <= 1.0):
            raise ValueError("delete_probability must be between 0 and 1")

        if self.delete_strategy in {"probability", "condition_or_probability"}:
            if self.delete_probability is None:
                raise ValueError(
                    "delete_strategy with probability requires delete_probability"
                )

        if self.delete_strategy == "condition" and self.delete_probability is not None:
            raise ValueError(
                "delete_probability must be null when delete_strategy is 'condition'"
            )

        if self.allow_reinsert_after_delete and self.enforce_terminal_delete:
            raise ValueError(
                "allow_reinsert_after_delete cannot be true when enforce_terminal_delete is true"
            )

        return self


class TableConfig(BaseModel):
    """Table declaration in the domain config."""

    name: str
    rows: int | None = Field(default=None, ge=1)
    rows_from_table: str | None = None
    primary_key: str | None = None
    fields: list[FieldConfig]

    @model_validator(mode="after")
    def validate_table(self) -> "TableConfig":
        """Validate table consistency rules."""
        if self.rows is not None and self.rows_from_table is not None:
            raise ValueError("table cannot define both 'rows' and 'rows_from_table'")

        field_names = [field.name for field in self.fields]
        if len(field_names) != len(set(field_names)):
            raise ValueError(f"table '{self.name}' has duplicated field names")

        return self


class DomainSettings(BaseModel):
    """Global settings shared by all table generators."""

    seed: int = 42
    start_date: date = date(2025, 1, 1)
    days: int = Field(default=30, ge=1)
    default_rows: int = Field(default=100, ge=1)


class DomainConfig(BaseModel):
    """Root config model for one domain."""

    version: int = 1
    domain: str
    settings: DomainSettings
    tables: list[TableConfig]
    cdc: list[CdcTablePolicy] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_domain(self) -> "DomainConfig":
        """Validate global domain constraints."""
        table_names, table_name_set, table_by_name = self._build_table_index()
        self._validate_unique_table_names(table_names)
        self._validate_table_references(table_name_set)
        self._validate_cdc_policies(table_name_set, table_by_name)

        return self

    def _build_table_index(self) -> tuple[list[str], set[str], dict[str, TableConfig]]:
        table_names = [table.name for table in self.tables]
        table_name_set = set(table_names)
        table_by_name = {table.name: table for table in self.tables}
        return table_names, table_name_set, table_by_name

    def _validate_unique_table_names(self, table_names: list[str]) -> None:
        if len(table_names) != len(set(table_names)):
            raise ValueError("Domain config contains duplicated table names")

    def _validate_table_references(self, table_name_set: set[str]) -> None:
        for table in self.tables:
            self._validate_rows_from_table_reference(table, table_name_set)
            self._validate_field_references(table, table_name_set)

    def _validate_rows_from_table_reference(self, table: TableConfig, table_name_set: set[str]) -> None:
        if table.rows_from_table and table.rows_from_table not in table_name_set:
            raise ValueError(
                f"table '{table.name}' references unknown rows_from_table '{table.rows_from_table}'"
            )

    def _validate_field_references(self, table: TableConfig, table_name_set: set[str]) -> None:
        for field in table.fields:
            spec = field.generator
            if spec.kind == "reference" and spec.table not in table_name_set:
                raise ValueError(
                    f"table '{table.name}' field '{field.name}' references unknown table '{spec.table}'"
                )

    def _validate_cdc_policies(
        self,
        table_name_set: set[str],
        table_by_name: dict[str, TableConfig],
    ) -> None:
        cdc_tables = [policy.table for policy in self.cdc]
        if len(cdc_tables) != len(set(cdc_tables)):
            raise ValueError("Domain config contains duplicated CDC policies for the same table")

        for policy in self.cdc:
            self._validate_one_cdc_policy(policy, table_name_set, table_by_name)

    def _validate_one_cdc_policy(
        self,
        policy: CdcTablePolicy,
        table_name_set: set[str],
        table_by_name: dict[str, TableConfig],
    ) -> None:
        if policy.table not in table_name_set:
            raise ValueError(f"CDC policy references unknown table '{policy.table}'")

        table = table_by_name[policy.table]
        field_names = {field.name for field in table.fields}
        if policy.primary_key not in field_names:
            raise ValueError(
                f"CDC policy for table '{policy.table}' uses unknown primary_key '{policy.primary_key}'"
            )
        if policy.source_timestamp_field not in field_names:
            raise ValueError(
                "CDC policy for table "
                f"'{policy.table}' uses unknown source_timestamp_field "
                f"'{policy.source_timestamp_field}'"
            )

        missing_sort_fields = [field for field in policy.sort_fields if field not in field_names]
        if missing_sort_fields:
            raise ValueError(
                f"CDC policy for table '{policy.table}' has unknown sort_fields: {missing_sort_fields}"
            )
