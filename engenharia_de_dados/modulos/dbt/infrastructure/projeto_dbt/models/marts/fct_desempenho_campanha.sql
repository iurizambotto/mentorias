with eventos as (
    select * from {{ ref('stg_eventos_campanha') }}
),

campanhas as (
    select * from {{ ref('stg_campanhas') }}
),

canais as (
    select * from {{ ref('de_para_canal') }}
),

conversoes_por_dia as (
    select
        campanha_id,
        data_conversao,
        count(*)             as conversoes,
        sum(valor_conversao) as receita
    from {{ ref('stg_conversoes') }}
    group by campanha_id, data_conversao
)

select
    eventos.campanha_id,
    eventos.data_evento,
    campanhas.nome_campanha,
    campanhas.canal,
    canais.grupo_de_canal,
    eventos.impressoes,
    eventos.cliques,
    cast(eventos.custo as decimal(12, 2))                        as custo,
    cast(coalesce(conversoes_por_dia.conversoes, 0) as bigint)   as conversoes,
    cast(coalesce(conversoes_por_dia.receita, 0) as decimal(12, 2)) as receita,
    cast(
        {{ razao_segura('eventos.custo', 'conversoes_por_dia.conversoes') }}
        as decimal(12, 2)
    )                                                            as custo_por_conversao
from eventos
inner join campanhas
    on eventos.campanha_id = campanhas.campanha_id
left join canais
    on campanhas.canal = canais.canal
left join conversoes_por_dia
    on eventos.campanha_id = conversoes_por_dia.campanha_id
    and eventos.data_evento = conversoes_por_dia.data_conversao
