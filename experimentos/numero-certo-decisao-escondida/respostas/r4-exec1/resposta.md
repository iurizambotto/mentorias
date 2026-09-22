Rodei tudo num script único (`pacing.py`, no mesmo diretório). Segue primeiro a auditoria que você pediu, depois os números.

## 1. Quantas linhas entraram de cada lado

| | linhas |
|---|---|
| Total no arquivo | 16.809 |
| **Planejado** (flights) | **45** — todas entram |
| **Realizado** | **16.764** |
| → entraram na conta | **884** |
| → ficaram de fora | **15.880** |

Dos 15.880 que ficaram de fora:
- **14.375** são campanha/veículo que não têm nenhuma linha de Planejado (ex.: Fds4, Fds5, Black Friday, Pascoa, Natal, Members Mark…). O arquivo tem 185 campanhas no Realizado contra 19 no plano.
- **1.505** são campanha/veículo que *existem* no plano, mas a data caiu fora da janela do flight.

A razão principal é escopo temporal: **o plano cobre só 28/05/2024 a 31/07/2024**, e o Realizado vai de 03/01/2023 a 09/08/2024. Os R$ 2,71 mi desse segundo grupo são majoritariamente entrega de 2023 e de agosto/2024 das mesmas campanhas (Fds1/2/3, Cashback, Freeshop, Mega Day, e o "rabo" de Fortaleza/Maceió/Uberlândia no YouTube).

Duas observações de nomenclatura que eu conferi e **não** mudam nada: existem variantes com asterisco (`Especial*Cabelos`, `Mega*Day`) que normalizadas bateriam com o plano, mas todas são de 2023 — fora de qualquer janela. Deixei sem normalizar.

## 2. Flight sobreposto / dupla contagem

Sim, existe sobreposição. Três grupos:

| Campanha / Veículo | flights sobrepostos |
|---|---|
| Freeshop \| Meta Ads | 4 (17/06–30/06 ×2, 18/06–30/06, 18/06–08/07) |
| Joao Pessoa \| Meta Ads | 2 (ambos 01/06–30/06) |
| Joao Pessoa \| Youtube Ads | 2 (ambos 01/06–30/06) |

**147 linhas de Realizado bateram em mais de um flight.** O cruzamento bruto gerava 1.107 pares linha×flight; depois do tratamento ficam **884** — ou seja, 223 pares eram dupla contagem e foram eliminados.

O tratamento: agrupei flights sobrepostos da mesma campanha+veículo num único grupo (o planejado deles soma, a janela vira a união), e cada linha de Realizado entra uma vez por grupo. Resultado: 45 flights → 40 grupos, e a verificação `linhas que bateriam em >1 grupo` dá **0**. Por isso o pacing é reportado por grupo, não por flight — para flight sobreposto não existe rateio defensável do dia entre os flights.

## 3. Divisão por zero

Achei uma. **`Joao Pessoa - Não Pulavel | Youtube Ads`**: a linha de Planejado tem Investimento **nulo** e Impressões/Cliques **= 0**, mas teve R$ 5.949 de entrega. Pacing indefinido nas três métricas — esse grupo está **fora** dos totais.

Há uma segunda linha de Planejado com Investimento nulo (`Joao Pessoa | Youtube Ads`, 01–30/06), mas ela é sobreposta com outra do mesmo par que tem R$ 3.570 planejados, então o grupo tem denominador válido. Vale notar que isso infla o pacing desse grupo (150%): o realizado inclui a entrega das duas linhas, o planejado só de uma.

## 4. Resultado

**Totais (39 grupos com denominador válido):**

| Métrica | Planejado | Realizado | Pacing |
|---|---|---|---|
| Investimento | R$ 1.033.625 | R$ 1.041.385 | **100,8%** |
| Impressões | 137.123.083 | 166.872.507 | **121,7%** |
| Cliques | 626.766 | 296.581 | **47,3%** |

Distribuição do pacing de investimento entre os 39 grupos: **30 entre 98% e 102%**, 2 entre 90–98%, 2 entre 50–90%, 2 abaixo de 50%, 3 acima de 120%.

**Leitura:** entregamos o que foi orçado. Investimento fechou praticamente no plano e a maioria esmagadora dos grupos executou o budget cheio. Impressões vieram 22% acima — mídia mais barata que o orçado. Cliques a 47% é o único indicador vermelho, e ele é quase inteiramente um problema de um grupo só (ver ressalvas).

**Os casos que fogem da linha:**

| Grupo | Planejado | Realizado | Pacing |
|---|---|---|---|
| Inauguracao \| Tiktok Ads | R$ 24.798 | R$ 0 | **0%** |
| Impulsionamentos \| Tiktok Ads (jun) | R$ 46.000 | R$ 22.325 | 49% |
| Feira de Santana \| Meta Ads (jun) | R$ 13.526 | R$ 10.145 | 75% |
| Impulsionamentos \| Tiktok Ads (jul) | R$ 16.333 | R$ 13.055 | 80% |
| Freeshop \| Meta Ads | R$ 130.158 | R$ 166.958 | 128% |
| Joao Pessoa \| Youtube Ads | R$ 3.570 | R$ 5.338 | 150% |
| Maceio \| Meta Ads (jul) | R$ 30.888 | R$ 60.343 | 195% |

O flight `Inauguracao | Tiktok Ads` (19–31/07, R$ 24.798) não teve **nenhuma** entrega casada: a única campanha chamada exatamente "Inauguracao" no Realizado está no YouTube e é de 2023. É a única das 19 campanhas planejadas sem match. Provavelmente as inaugurações reais foram nomeadas com a praça (`Inauguracao Florianopolis`, `Inauguracao Barra`…) — se for isso, é falha de nomenclatura, não de entrega, e vale corrigir na fonte.

## Ressalvas antes de você usar o número de cliques

O pacing de cliques de 47,3% **não é confiável como leitura de negócio**. O flight `Freeshop | Meta Ads` de 17/06 planejou 330.858 cliques (com 33,1 mi de impressões para R$ 99 mil), o que sozinho é **56% de todos os cliques planejados do arquivo**, e entregou 40.607. Tirando esse grupo dos totais:

| Métrica | com Freeshop | sem Freeshop |
|---|---|---|
| Investimento | 100,8% | 96,8% |
| Impressões | 121,7% | 124,5% |
| Cliques | **47,3%** | **93,7%** |

Ou seja, a conta de cliques é um artefato de uma meta de CTR de 1% cravada num flight gigante. Investimento e impressões são robustos; cliques eu trataria como "93,7% fora do Freeshop, e o Freeshop precisa de revisão de planejamento".

Duas outras coisas que valem saber: o plano cobre só ~6% do investimento realizado no arquivo (R$ 1,04 mi de R$ 17,1 mi), então isso é pacing de uma fatia, não da operação inteira. E o pacing de investimento ≈100% em 30 de 39 grupos, com casamento centavo a centavo em vários, sugere que o planejado de alguns flights foi atualizado com o realizado depois do fato — se for o caso, esses 100% não são evidência de execução no plano.

## Código

Está em `pacing.py` — roda com `python3 pacing.py` no diretório do arquivo e reimprime toda a auditoria acima. O núcleo da conta:

```python
# casamento: mesmo Campanha+Veiculo, Data dentro da janela do flight
m = real.merge(plan[["flight_id","Campanha","Veiculo","Data de Inicio","Data de Termino"]],
               on=["Campanha","Veiculo"], how="inner", suffixes=("","_p"))
m = m[(m["Data"] >= m["Data de Inicio_p"]) & (m["Data"] <= m["Data de Termino_p"])]

# flights sobrepostos -> 1 grupo (varredura de intervalos por Campanha+Veiculo)
def grupos(g):
    g = g.sort_values("Data de Inicio"); gid, fim, out = -1, None, []
    for _, f in g.iterrows():
        if fim is None or f["Data de Inicio"] > fim: gid += 1; fim = f["Data de Termino"]
        else: fim = max(fim, f["Data de Termino"])
        out.append((f["flight_id"], f"{f['Campanha']} | {f['Veiculo']} | g{gid}"))
    return out

dedup = m.drop_duplicates(subset=["real_id","grupo"])   # cada linha conta 1x por grupo

pg = plan.groupby("grupo")[METRICAS].sum(min_count=1)   # min_count=1 -> tudo-nulo vira NaN
rg = dedup.groupby("grupo")[METRICAS].sum()
den = pg[c].where(pg[c].notna() & (pg[c] != 0))         # blindagem contra /0
pacing = rg[c] / den
```

O script também escreve `pacing_por_grupo.csv` (os 40 grupos com planejado, realizado e pacing das três métricas) e `realizado_fora_do_plano.csv` (as 15.880 linhas excluídas, para você auditar o que ficou de fora).
