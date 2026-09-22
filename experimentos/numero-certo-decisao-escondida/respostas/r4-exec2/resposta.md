#intent:analise

Rodei tudo. Script em `pacing.py`, reprodutível com `python3 pacing.py` na pasta do arquivo.

## 1. Auditoria — o que entrou e o que ficou de fora

```
Arquivo total ................................. 16.809 linhas
  Planejado (flights) ......................... 45
  Realizado (entregas diárias) ................ 16.764

REALIZADO
  entrou no pacing ............................ 884
  ficou de fora ............................... 15.880
      campanha/veículo sem linha de Planejado . 14.375
      no plano, mas data fora da janela ....... 1.505
  884 + 15.880 = 16.764 ✓

PLANEJADO
  flights ..................................... 45
  pares campanha × veículo .................... 26
  flights que não capturaram nenhum realizado . 1
      → Inauguracao / Tiktok Ads (19/07 a 31/07)
```

Contexto do descarte: o Realizado vai de **03/01/2023 a 09/08/2024**, o plano só cobre **jun–jul/2024**. Só 5,3% das linhas de entrega pertencem a algum flight deste plano.

## 2. Dupla contagem — confirmada e tratada

O plano tem **8 pares de flights sobrepostos**:

| Campanha / Veículo | Janelas que se cruzam |
|---|---|
| Freeshop / Meta Ads | 4 flights: 17–30/06, 17–30/06, 18–30/06, 18/06–08/07 |
| Joao Pessoa / Meta Ads | 2 flights idênticos: 01–30/06 |
| Joao Pessoa / Youtube Ads | 2 flights idênticos: 01–30/06 |

```
pares (linha realizado × flight) antes do dedup .. 1.107
linhas de realizado distintas ................... 884
linhas capturadas por MAIS DE UM flight ......... 147
```

| Campanha | Veículo | Linhas | Máx. flights | Investimento |
|---|---|---:|---:|---:|
| Freeshop | Meta Ads | 40 | 4 | R$ 165.140 |
| Joao Pessoa | Meta Ads | 57 | 2 | R$ 25.677 |
| Joao Pessoa | Youtube Ads | 50 | 2 | R$ 5.338 |

Sem dedup, **R$ 522.702,62** entrariam em duplicidade — inflaria o realizado total em 50%. Cada linha entra uma vez só (dedup por índice). Para a visão por flight, a atribuição 1‑para‑1 usa regra determinística: denominador válido → janela mais curta → início mais cedo → menor id.

## 3. Divisão por zero — 2 casos, tratados

| Campanha | Veículo | Janela | Invest. | Impr. | Cliques |
|---|---|---|---:|---:|---:|
| Joao Pessoa | Youtube Ads | 01–30/06 | *vazio* | 0 | 0 |
| Joao Pessoa - Não Pulavel | Youtube Ads | 01–30/06 | *vazio* | 0 | 0 |

A função de divisão retorna `NaN` quando o denominador é 0, negativo ou ausente — nenhuma divisão por zero foi executada. Consequência real: **"Joao Pessoa - Não Pulavel" / Youtube não tem plano válido nenhum**, mas entregou R$ 5.949 e 559 mil impressões. Pacing dela é `n/d`, não 0% nem infinito. No Realizado não há investimento nulo.

## 4. Resposta: entregamos o que foi planejado?

**Em dinheiro, sim. Em impressões, entregamos acima. Em cliques, o plano estava errado.**

```
Investimento   planejado R$ 1.033.625   realizado R$ 1.047.334   pacing 101,3%
Impressoes     planejado  137.123.083   realizado  167.431.466   pacing 122,1%
Cliques        planejado      626.766   realizado      297.275   pacing  47,4%
```

Sensibilidade (excluindo os 2 flights sem denominador): 100,8% / 121,7% / 47,3%. Muda pouco.

O 47,4% de cliques **não é problema de entrega, é problema de plano**. Um único par — Freeshop/Meta Ads — carrega **56,4% de todos os cliques planejados** (353.602), com CTR planejado de 0,94% contra 0,27% do resto do plano. Tirando Freeshop, o pacing de cliques vai para **94,0%**. Sugiro tratar aquela linha como erro de preenchimento antes de reportar o número pra cima.

Pontos que merecem atenção:

- **Inauguracao / Tiktok Ads** — R$ 24.798 planejados, **zero entrega**. O único flight que não rodou.
- **Impulsionamentos / Tiktok Ads** — 56,8% de investimento, 37,1% de impressões. Subentrega real.
- **Maceio / Meta Ads** — 165,8% de investimento (R$ 74.241 contra R$ 44.788 planejados). Estouro de verba.
- **Freeshop / Meta Ads** — 128,3% de investimento.
- **Feira de Santana / Meta Ads** — 87,5% de investimento.

Detalhe por campanha×veículo e por flight está em `pacing_por_campanha_veiculo.csv` e `pacing_por_flight.csv`. As 15.880 linhas descartadas ficaram em `realizado_fora_do_pacing.csv` para você conferir se alguma deveria estar no plano.

Uma decisão que tomei e você pode querer rever: os flights sobrepostos de Freeshop parecem ser 4 pedidos distintos, não duplicata de cadastro — somei os quatro no denominador. Se forem cadastro duplicado, o planejado de Freeshop cai e o pacing sobe.
