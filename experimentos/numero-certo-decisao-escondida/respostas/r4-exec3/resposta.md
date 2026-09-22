Analisei o arquivo `BASE DE PACING_v2.csv.xls` (é um CSV UTF-8 com BOM, apesar da extensão). O script completo está em `pacing.py` — roda com `python3 pacing.py` no diretório do arquivo.

## 1. Quantas linhas entraram e quantas ficaram de fora

| | linhas |
|---|---|
| Total no arquivo | 16.809 |
| **Planejado** (flights) | **45** — 44 com entrega casada, 1 sem nenhuma |
| **Realizado** | **16.764** — dos quais **884 entraram** no pacing (5,3%) |

As 15.880 linhas de Realizado que ficaram de fora, por motivo:

| motivo | linhas |
|---|---|
| campanha não existe no plano | 10.209 |
| campanha no plano, mas veículo fora do plano | 4.166 |
| campanha+veículo no plano, mas data fora da janela do flight | 1.505 |

O motivo estrutural: **o plano cobre só 2024-05-28 a 2024-07-31**, e o Realizado vai de 2023-01-03 a 2024-08-09. Dentro do período global do plano só existem 1.162 linhas de Realizado.

O flight sem nenhuma entrega é **Inauguracao / Tiktok Ads / 19–31 jul 2024, R$ 24.797,50 planejados**. Existe Realizado com campanha "Inauguracao", mas só no YouTube e em 2023 — não casa. Esse flight entra como 0% de pacing.

## 2. Dupla contagem por flight sobreposto

Sim, existe. **8 pares sobrepostos**, em 3 grupos:

- **Freeshop / Meta Ads** — 4 flights cruzados (17/06–30/06 ×2, 18/06–30/06, 18/06–08/07). Os dois últimos são idênticos em valor (R$ 5.000 / 1.250.000 imp) e só diferem na data de término — cheira a linha de plano duplicada com fim estendido.
- **Joao Pessoa / Meta Ads** — 2 flights com janela idêntica (01–30/06), diferindo só em Público.
- **Joao Pessoa / Youtube Ads** — idem.

Efeito: **147 linhas de Realizado casaram com mais de um flight**. Sem dedupe seriam 1.107 pareamentos para 884 linhas distintas — **223 contagens duplicadas**. O numerador foi deduplicado pelo índice da linha, então cada Realizado entra uma vez só.

Fiz também um teste de sensibilidade casando por Campanha+Veículo+**Público+Modalidade** (que é o que distingue os flights sobrepostos): dá exatamente as mesmas 884 linhas e os mesmos totais. Ou seja, o resultado não depende dessa escolha.

## 3. Divisão por zero

Dois flights têm denominador inválido:

| Campanha | Veículo | Janela | Invest. | Impr. | Cliques |
|---|---|---|---|---|---|
| Joao Pessoa | Youtube Ads | 01–30/06/24 | *nulo* | 0 | 0 |
| Joao Pessoa - Não Pulavel | Youtube Ads | 01–30/06/24 | *nulo* | 0 | 0 |

Foram tratados como `NaN` explícito, nunca 0 nem infinito. Detalhe que importa: **"Joao Pessoa - Não Pulavel" não tem nenhum flight válido**, mas tem R$ 5.949 de entrega casada. Se deixar ela na conta, o numerador ganha dinheiro sem denominador correspondente e o total infla. Tirei essa campanha do total consolidado. (O caso "Joao Pessoa" comum não é problema: o outro flight do mesmo veículo tem plano válido.)

Também verifiquei duplicatas de linha no Realizado: zero. A chave `campaign_name + Campanha + Veiculo + Data` é única nas 16.764 linhas. Aparecem várias linhas por Campanha×Veículo×dia, mas são praças/criativos diferentes, não repetição.

## 4. Os números

**Consolidado** (só campanhas do plano, entrega dentro da janela, sem a campanha sem denominador):

| métrica | planejado | realizado | pacing | delta |
|---|---|---|---|---|
| Investimento | R$ 1.033.625 | R$ 1.041.385 | **100,8%** | +R$ 7.760 |
| Impressões | 137.123.083 | 166.872.507 | **121,7%** | +29,7 M |
| Cliques | 626.766 | 296.581 | **47,3%** | −330.185 |

**A resposta curta: sim, entregamos o que foi planejado em verba e em mídia.** O dinheiro fechou praticamente no orçado e as impressões vieram 22% acima do previsto — comprou-se mídia mais barata que o plano assumia.

**Os cliques são o ponto fora da curva, e são um ponto falso.** Os 47% vêm quase inteiros de uma única linha: **Freeshop / Meta Ads planejava 330.858 cliques** (53% de todos os cliques planejados do arquivo) com R$ 99 mil e 33 M de impressões — ou seja, um CTR planejado de 1,0%, contra ~0,1% que a operação de fato entrega nesse veículo. Tirando Freeshop da conta, o pacing de cliques vai para **93,7%**, com impressões em 124,5% e investimento em 96,8%. Eu trataria aquela linha do plano como erro de orçamento, não como falha de entrega.

**Onde o dinheiro divergiu de verdade** (delta de investimento por campanha):

| campanha | planejado | realizado | pacing |
|---|---|---|---|
| Impulsionamentos | R$ 169.500 | R$ 139.302 | 82% |
| Inauguracao | R$ 24.798 | R$ 0 | 0% |
| Feira de Santana | R$ 53.933 | R$ 50.547 | 94% |
| Cashback Resgate | R$ 26.868 | R$ 25.004 | 93% |
| Maceio | R$ 86.368 | R$ 115.817 | 134% |
| Freeshop | R$ 130.158 | R$ 166.958 | 128% |

As outras 12 campanhas fecharam em 100% ± 0,1% — o plano foi cumprido à risca. Em Impulsionamentos a subentrega está concentrada no TikTok (57% da verba, 37% das impressões). Maceió e Freeshop estouraram o orçado; vale checar se foi realocação aprovada ou se saiu do controle.

## Ressalvas

- O casamento usa Campanha + Veículo normalizados (trim + casefold), por isso os nomes saem em minúsculas nas tabelas.
- Janela do flight é inclusiva nas duas pontas.
- Para Freeshop e Joao Pessoa, o pacing só é interpretável no agregado campanha×veículo: com flights sobrepostos não dá para atribuir a entrega a um flight específico sem uma regra de negócio que o arquivo não tem.
