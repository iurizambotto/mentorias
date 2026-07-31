select
    cast(campanha_id as integer)             as campanha_id,
    trim(nome)                               as nome_campanha,
    lower(trim(canal))                       as canal,
    cast(data_inicio as date)                as data_inicio,
    cast(orcamento_diario as decimal(10, 2)) as orcamento_diario
from {{ source('bruto', 'campanhas') }}
