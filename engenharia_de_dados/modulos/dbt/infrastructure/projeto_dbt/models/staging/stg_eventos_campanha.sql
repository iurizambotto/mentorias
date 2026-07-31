select
    cast(evento_id as integer)        as evento_id,
    cast(campanha_id as integer)      as campanha_id,
    cast(data_evento as date)         as data_evento,
    cast(impressoes as bigint)        as impressoes,
    cast(cliques as bigint)           as cliques,
    cast(custo as decimal(12, 2))     as custo
from {{ source('bruto', 'eventos_campanha') }}
