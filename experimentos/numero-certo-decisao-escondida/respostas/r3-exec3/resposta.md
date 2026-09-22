## Resposta curta

**A verba foi entregue (100,8% do orçado), as impressões vieram acima do plano (121,7%), e os cliques ficaram bem abaixo (47,3%) — mas esse 47% é quase todo um erro de premissa no plano, não falha de entrega.** Corrigindo isso, cliques ficam em 93,7%.

Dito isso, tem uma ressalva importante sobre o dado antes dos números: **o pacing de verba dessa base é quase tautológico.** Em 30 das 39 janelas de plano, o realizado fecha com diferença menor que R$ 5 do planejado. Ou seja, a coluna de investimento do Realizado parece ser a verba contratada rateada por dia, não uma medição independente. Então eu usaria verba só para achar as exceções, e mídia (impressões/cliques) como o sinal real de performance.

## O que entrou na conta

| | Planejado | Realizado | Pacing |
|---|---|---|---|
| Investimento | R$ 1.033.625 | R$ 1.041.385 | **100,8%** |
| Impressões | 137,1 mi | 166,9 mi | **121,7%** |
| Cliques | 626.766 | 296.581 | **47,3%** |

Escopo: 45 flights planejados, de 28/05 a 31/07/2024, 19 campanhas. A base tem realizado de jan/2023 a 09/08/2024 (R$ 17,1 mi total) — só R$ 1,04 mi (6%) casa com esse plano.

Eficiência: CPM realizado R$ 6,24 contra R$ 7,54 planejado (mídia saiu mais barata, o que explica as impressões acima). CTR realizado 0,178% contra 0,457% planejado.

## Os cliques: o 47% é ruído

Uma única linha de plano responde por quase todo o gap: **Freeshop / Meta Ads**, que orçou 330.858 cliques sobre 33 mi de impressões — CTR implícito de **1,00%**, quando a média do próprio plano é 0,27% e a realidade da conta foi 0,09%. Essa linha sozinha é 53% de toda a meta de cliques do plano.

Sem Freeshop: cliques em **93,7%**, impressões em 124,5%. É esse o número que eu levaria pra frente. A meta de cliques do Freeshop precisa ser revisada, não a entrega.

## O que realmente não entregou

Só 6 das 39 janelas ficaram abaixo de 95% na verba, e são elas que importam:

| Campanha | Veículo | Janela | Planejado | Realizado | Pacing |
|---|---|---|---|---|---|
| Inauguracao | Tiktok | 19–31/07 | R$ 24.798 | R$ 0 | **0%** |
| Impulsionamentos | Tiktok | 01–30/06 | R$ 46.000 | R$ 22.325 | **48,5%** |
| Feira de Santana | Meta | 01–30/06 | R$ 13.526 | R$ 10.145 | 75,0% |
| Impulsionamentos | Tiktok | 01–31/07 | R$ 16.333 | R$ 13.055 | 79,9% |
| Cashback Resgate | Meta | 10–30/06 | R$ 19.848 | R$ 17.984 | 90,6% |
| Impulsionamentos | Meta | 01–31/07 | R$ 32.667 | R$ 29.422 | 90,1% |

**TikTok é o problema concentrado:** R$ 99.050 planejados, R$ 47.290 entregues — 48% de verba e **24% de impressões**. Meta (107% verba) e YouTube (102%) entregaram.

Sobre a Inauguracao no TikTok: não existe **nenhuma** linha de realizado de Inauguracao em 2024 — a campanha só aparece no YouTube em 2023. E o TikTok tem entrega normal naquela janela (outras campanhas rodaram), então não é falta de dado. Uma hipótese que vale checar: **Uberlandia entregou R$ 22.004 no TikTok dentro do período sem ter linha de plano nesse veículo** — valor próximo dos R$ 24.798 que faltaram. Parece remanejamento de verba entre campanhas no mesmo veículo.

## Estouros

| Campanha | Veículo | Planejado | Realizado | Pacing |
|---|---|---|---|---|
| Maceio | Meta | R$ 30.888 | R$ 60.343 | **195,4%** |
| Joao Pessoa | Youtube | R$ 3.570 | R$ 5.338 | 149,5% |
| Freeshop | Meta | R$ 130.158 | R$ 166.958 | 128,3% |

Maceio/Meta em julho é o caso mais claro: dobrou a verba, entregou 190% das impressões, tudo em objetivo Alcance nos 31 dias.

## Ressalvas metodológicas (vale ler)

**1. Flights sobrepostos — tratei com merge.** Alguns pares campanha+veículo têm flights com janelas que se cruzam: Freeshop/Meta tem 4 flights sobrepostos (17/06–08/07), e Joao Pessoa tem 2 flights de Meta e 2 de YouTube com janelas *idênticas*. Se eu casasse cada flight com o realizado separadamente, o mesmo dia de entrega seria contado 2 a 4 vezes e o Freeshop apareceria com pacing de ~500%. Uni as janelas sobrepostas somando os planos: **45 flights → 40 janelas de plano.** Se a área trata esses flights sobrepostos como coisas distintas (ex.: linhas separadas de compra dentro da mesma campanha), me diga qual critério usa para atribuir a entrega diária, porque isso muda Freeshop e Joao Pessoa.

**2. Duas linhas de plano sem verba.** `Joao Pessoa / Youtube` e `Joao Pessoa - Não Pulavel / Youtube` têm investimento vazio e 0 impressões/cliques planejados. A segunda é a **única** linha de plano da campanha "Joao Pessoa - Não Pulavel", então ela fica sem pacing — apesar de ter entregue R$ 5.949 e 559 mil impressões. Ou o orçamento dela está em outra linha, ou faltou preencher.

**3. Muita verba rodou fora do plano.** Dentro do próprio período 28/05–31/07, **R$ 1.031.072 foram gastos em 20 campanhas sem nenhuma linha de Planejado** — praticamente o mesmo tamanho do plano todo. As maiores: família Material Didatico (~R$ 645 mil), Members Mark (R$ 181 mil), Pampulha (R$ 41 mil). Também apareceram **Fds4 e Fds5** rodando, quando o plano só vai até Fds3. Isso está fora do pacing conforme a regra, mas é o achado que eu levaria pra reunião: metade do dinheiro do período não tinha plano registrado nessa base.

**4. Entrega fora de janela é irrelevante aqui.** Campanhas planejadas que entregaram fora da sua janela/veículo somam R$ 3,93 mi na base inteira, mas só R$ 39 mil dentro do período do plano. Não move o resultado.

**5. Nomes de 2023 usam `*` como separador** (`Mega*Day`, `Dia*Das*Maes` — 57 campanhas, R$ 1,9 mi). Verifiquei: são todas de jan a jul/2023, nenhuma toca o período do plano. Não precisou normalizar.

O script da análise está em `/tmp/pacing.py` se quiser rodar com outro critério de matching.
