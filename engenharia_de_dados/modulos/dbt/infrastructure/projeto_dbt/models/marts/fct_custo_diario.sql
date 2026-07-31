{{ config(materialized="incremental", unique_key=["campanha_id", "data_evento"]) }}

select
    campanha_id,
    data_evento,
    sum(custo) as custo
from {{ ref('stg_eventos_campanha') }}

{% if is_incremental() %}
    -- Only on runs after the first one, and never under --full-refresh.
    where data_evento > (
        select coalesce(max(data_evento), date '1900-01-01') from {{ this }}
    )
{% endif %}

group by campanha_id, data_evento
