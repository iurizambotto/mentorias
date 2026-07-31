select
    cast(conversao_id as integer)   as conversao_id,
    cast(campanha_id as integer)    as campanha_id,
    cast(data_conversao as date)    as data_conversao,
    cast(valor as decimal(12, 2))   as valor_conversao
from {{ source('bruto', 'conversoes') }}
