-- A singular test is a query that must return zero rows.
-- A negative cost means the ingestion inverted a sign, and that has happened.
select
    campanha_id,
    data_evento,
    custo
from {{ ref('fct_desempenho_campanha') }}
where custo < 0
