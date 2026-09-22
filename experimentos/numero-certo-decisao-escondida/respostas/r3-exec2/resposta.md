## Resposta curta

**Sim, o plano foi entregue em dinheiro — praticamente no centavo.** Pacing de investimento de **101,3%** no agregado, e **34 dos 42 flights** com verba planejada ficaram entre 90% e 110%. A entrega de mídia veio acima do plano em impressões (122%) e os cliques só parecem ruins por causa de uma meta mal calibrada num único flight.

## Como calculei

Regra que você descreveu: realizado dividido por planejado, contando só o realizado dentro da janela do flight e no mesmo veículo. Duas decisões que precisei tomar no caminho:

- **Havia flights sobrepostos na mesma Campanha+Veículo** (Freeshop/Meta e João Pessoa/Meta e Youtube), o que faria a mesma entrega ser contada duas vezes. Usei `Modalidade` + `Público` como desempate — e isso resolveu sem perder nenhuma linha: exatamente as mesmas 884 linhas de Realizado casam com e sem esses campos, só que agora cada uma cai num flight único.
- **Sobrou um caso que nem isso resolve:** Freeshop / Meta Ads / Trade / Sócios tem duas linhas de Planejado idênticas (R$ 5.000, 1,25M impressões cada), mesmo início 18/06, términos diferentes (30/06 e 08/07). Tratei como um plano só de R$ 10.000 na janela 18/06–08/07. Se for linha duplicada no orçamento e o certo for R$ 5.000, esse flight vai de 50% para 100% de pacing. **Vale confirmar com quem montou o plano.**

## O consolidado (45 flights, 28/05 a 31/07/2024)

| Métrica | Planejado | Realizado | Pacing |
|---|---|---|---|
| Investimento | R$ 1.033.625 | R$ 1.047.334 | **101,3%** |
| Impressões | 137,1 M | 167,4 M | **122,1%** |
| Cliques | 626.766 | 297.275 | **47,4%** |

O 47,4% de cliques é artefato de um flight só: **Freeshop / Meta / Não Sócios** foi planejado com 330.858 cliques sobre 33,1M de impressões — CTR de 1%, irreal para campanha de Alcance. Ele sozinho é 53% da meta de cliques do plano inteiro. As impressões desse flight entregaram 102%. **Tirando esse flight, o pacing de cliques vai para 91,8%** e o de impressões para 128,5%. Ou seja: o problema está na meta, não na entrega.

## Onde não entregou

| Campanha | Veículo | Janela | Plano | Realizado | Pacing |
|---|---|---|---|---|---|
| Inauguracao | Tiktok | 19–31/07 | R$ 24.798 | R$ 0 | **0%** |
| João Pessoa (Sócios) | Youtube | 01–30/06 | R$ 3.570 | R$ 1.371 | 38% |
| Impulsionamentos | Tiktok | 01–30/06 | R$ 46.000 | R$ 22.325 | 49% |
| Freeshop (Trade) | Meta | 18/06–08/07 | R$ 10.000 | R$ 5.000 | 50% |
| Feira de Santana | Meta | 01–30/06 | R$ 13.526 | R$ 10.145 | 75% |
| Impulsionamentos | Tiktok | 01–31/07 | R$ 16.333 | R$ 13.055 | 80% |

**O "zero" da Inauguracao/Tiktok quase certamente não é zero de verdade.** Não existe nenhuma entrega com o nome "Inauguracao" em 2024 (as únicas linhas com esse nome são Youtube, de 2023). Mas existe entrega **Uberlandia / Tiktok Ads / Inauguracao / Não Sócios de 17 a 31/07, R$ 22.004** — janela e valor quase colados no flight planejado, e sem plano próprio. Parece a mesma verba nomeada de forma diferente no realizado. Se for isso, o flight fica em ~89% e some o pior buraco do plano.

O único ponto de subentrega que se sustenta sozinho é o **Tiktok em Impulsionamentos**, que ficou abaixo nos dois meses (49% e 80%) e também nas impressões (27% e 79%).

## Onde estourou

- **Freeshop / Meta / Sócios: R$ 62.700 contra R$ 20.900 planejados — exatamente 3,00x.** Um múltiplo redondo assim geralmente é plano lançado por 1/3 do valor ou verba triplicada em veiculação. Uma única linha de campanha no realizado, sem nada anômalo nos dados. Precisa de confirmação: são R$ 41.800 acima do orçado.
- **Maceió / Meta / julho: 195%** (R$ 60.343 contra R$ 30.888), com impressões também em 190% — esse ao menos estourou entregando.

Esses dois somam ~R$ 71 mil acima do plano e são o que compensa as subentregas, mantendo o total em 101%.

## Duas ressalvas na base

- **Dois flights de João Pessoa/Youtube têm plano zerado** (investimento vazio e 0 impressões): o de Não Sócios e o "João Pessoa - Não Pulável". Ambos tiveram entrega real (R$ 3.967 e R$ 5.949). Ficaram sem pacing calculável — é divisão por zero, não performance ruim. São R$ 9.916 entregues sem plano registrado.
- **Pequenas sobras fora de janela:** Uberlândia teve entrega em 28–31/05 em Meta e Youtube (R$ 3.113 somados) que ficou de fora por cair antes do início do flight de junho, como manda a regra.

## O que ficou fora da conta

No período do plano rodaram **R$ 2,12 milhões** no total, mas só **R$ 1,05 milhão** pertence a este plano. Os outros **49% são de 20 campanhas sem nenhuma linha de Planejado** — Material Didático (R$ 313 mil), Members Mark (R$ 182 mil), Material Didático Influ (R$ 144 mil), Pampulha, Fds4, Fds5, Jabaquara e outras. Elas não entram no pacing, como você definiu, mas vale saber que **metade do investido no período não tinha plano associado neste arquivo**.

A base inteira vai de jan/2023 a ago/2024; tudo antes de 28/05/2024 é histórico fora do escopo do plano.

Deixei a tabela completa flight a flight em `/tmp/pacing_flight.csv`, com planejado, realizado e pacing das três métricas.
