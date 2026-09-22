Analisei o arquivo (`BASE DE PACING_v2.csv.xls`, 16.809 linhas). Antes do resultado, uma coisa estrutural importante que muda a leitura:

**O plano cobre menos da metade do que foi gasto.** Só 45 linhas são `Planejado` — 19 campanhas, 40 flights, todos entre 28/05 e 31/07/2024. No mesmo período o `Realizado` registra R$ 2.117.850 em 38 campanhas. O plano responde por R$ 1.047.334 disso, ou **49%**. Campanhas grandes como Material Didático (R$ 313k + R$ 332k em variações), Members Mark (R$ 182k) e Pampulha (R$ 41k) rodaram sem linha de planejado. Então "entregamos o que planejamos?" só tem resposta para metade da verba. O resto não tem contra o que comparar.

Também vale registrar como casei as bases: os nomes de campanha se repetem ao longo de 2023 (a base realizada vai de jan/2023 a ago/2024), então o match foi por Campanha + Veículo + data dentro da janela `Data de Inicio`–`Data de Termino` de cada flight. Comparar só por nome inflaria tudo em ~5x.

## O veredito, no escopo planejado

| Métrica | Planejado | Realizado | Entrega |
|---|---|---|---|
| Investimento | R$ 1.033.625 | R$ 1.047.334 | **101%** |
| Impressões | 137,1 M | 167,4 M | **122%** |
| Cliques | 626.766 | 297.275 | **47%** |

Os 47% de cliques são enganosos — vêm de uma linha só. O plano do **Freeshop** pedia 330.858 cliques sobre 33,1 M de impressões, ou seja CTR de 1,0%, quando o padrão realizado em toda a base é ~0,2%. É quase certamente erro de digitação no orçamento, não falha de entrega. Tirando o Freeshop da conta:

| Métrica (ex-Freeshop) | Planejado | Realizado | Entrega |
|---|---|---|---|
| Investimento | R$ 903.468 | R$ 880.377 | **97%** |
| Impressões | 99,6 M | 124,6 M | **125%** |
| Cliques | 273.164 | 256.668 | **94%** |

**Resumo: a verba foi entregue quase exatamente como orçada, a mídia veio mais barata que o previsto (CPM R$ 6,26 realizado vs. R$ 7,54 planejado), e por isso as impressões estouraram +25%. Cliques ficaram 6% abaixo — o CTR realizado (0,21%) ficou aquém do planejado (0,27%), e o volume extra de impressões compensou quase toda a diferença.** O CPC saiu em R$ 3,43 contra R$ 3,31 orçado.

O controle de pacing de verba foi o ponto mais forte: **31 dos 40 flights fecharam entre 99% e 100% do orçamento**, muitos com diferença de centavos.

## Onde não entregamos

**TikTok foi o furo do período.** É o único veículo que ficou abaixo em tudo:

| Veículo | Verba | Impressões | Cliques |
|---|---|---|---|
| Meta Ads | 107% | 135% | 48%¹ |
| Youtube Ads | 107% | 93% | 115% |
| **Tiktok Ads** | **48%** | **24%** | **13%** |

¹ contaminado pelo Freeshop.

Detalhando o TikTok:
- **Inauguração / TikTok (19–31/07, R$ 24.798 orçados): não rodou um único dia.** Zero de tudo.
- **Impulsionamentos / TikTok** entregou 49% da verba em junho (R$ 22,3k de R$ 46k) e 80% em julho, com só 19 e 20 dias veiculados de 30 e 31.
- **João Pessoa / TikTok** gastou 100% da verba mas entregou só 30% das impressões e 23% dos cliques — CPM muito acima do orçado.

Provável explicação para o flight de Inauguração: **Uberlândia rodou no TikTok de 17/07 a 09/08 com R$ 28.158, sem constar no plano.** O valor e a data batem com a verba de "Inauguração / TikTok". Ou seja, não foi verba perdida — foi realocada e reetiquetada. Vale confirmar com o time de mídia, porque na base isso aparece como 100% de não-entrega.

**Estouros relevantes:**
- Maceió / Meta em julho: R$ 60.343 contra R$ 30.888 orçados (**195%**, +R$ 29,5k).
- Freeshop / Meta: R$ 166.958 contra R$ 130.158 (**128%**, +R$ 36,8k).
- João Pessoa / YouTube: 150% da verba.

**Praças de inauguração superentregaram muito em impressões** — Maceió/Meta junho 519%, Fortaleza/Meta 352% nos dois meses, Uberlândia/Meta 254–290%, Feira de Santana/Meta 214–265%. Com a verba em 100%, isso significa que o CPM orçado para inaugurações estava conservador demais. Não é problema de entrega, é problema de orçamento — o planejamento dessas praças precisa recalibrar o CPM, senão o plano continua subestimando a entrega em 2–5x.

## Duas ressalvas na qualidade do dado

- Duas linhas de plano estão vazias: **João Pessoa / YouTube (Não Sócios)** e **João Pessoa - Não Pulável / YouTube** têm investimento nulo e zero impressões/cliques planejados, mas a segunda rodou R$ 5.949. São flights sem orçamento registrado.
- Vários flights de YouTube mostram 25–26 dias veiculados numa janela de 30. Pode ser pacing real ou lacuna de reporte — não dá pra distinguir pela base, já que o gasto fechou em 100%.

Se quiser, monto o comparativo flight a flight num CSV, ou aprofundo no TikTok / nas campanhas sem plano.
