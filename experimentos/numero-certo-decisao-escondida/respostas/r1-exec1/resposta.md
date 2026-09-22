Análise feita sobre `BASE DE PACING_v2.csv.xls` (16.809 linhas; é um CSV, apesar da extensão `.xls`).

## Antes do veredito: o plano cobre só 6% do investimento

A coluna `Base` separa plano de realizado, mas de forma muito assimétrica:

| | Linhas | Campanhas | Período | Investimento |
|---|---|---|---|---|
| Planejado | 45 | 19 | mai–jul/2024 | R$ 1,03 mi |
| Realizado | 16.764 | 185 | jan/2023–ago/2024 | R$ 17,08 mi |

Então "entregamos o que foi planejado?" só tem resposta para **19 campanhas e ~R$ 1,03 mi**. Os outros R$ 16 mi (166 campanhas) não têm linha de plano no arquivo — não é que ficaram fora da meta, é que não há meta registrada contra a qual comparar.

## Dentro do escopo planejado: sim, entregou

Comparando por campanha × veículo × público, dentro da janela de voo de cada linha:

| Métrica | Planejado | Realizado | Pacing |
|---|---|---|---|
| Investimento | R$ 1.033.625 | R$ 1.047.334 | **101,3%** |
| Impressões | 137,1 mi | 167,4 mi | **122,1%** |
| Cliques | 626.766 | 297.275 | **47,4%** ⚠️ |

Investimento praticamente cravado no plano (mai+jun a 102%, jul a 100%), e a entrega de mídia veio **22% acima** porque o CPM saiu mais barato que o previsto: **R$ 6,26 vs R$ 7,54 planejado** (17% abaixo). Verifiquei que isso não é artefato de mistura de objetivos — todo o realizado dentro da janela está em objetivos que existem no plano.

**O 47% de cliques é enganoso.** Uma única linha (Freeshop / Meta / Não Sócios) concentra 53% de toda a meta de cliques do plano, assumindo CTR de 1,0%. Sem ela, os cliques ficam em **91,8%**. O plano usa premissas de CTR muito inconsistentes entre linhas — de 0,05% (Fortaleza, Maceió) a 1,0% (Freeshop, João Pessoa Sócios) — o que torna a meta de cliques agregada pouco confiável como termômetro.

## Onde realmente furou

1. **`Inauguracao` (TikTok, 19–31/jul): R$ 24.798 planejados, zero entregue.** Não há nenhum registro dessa campanha em 2024 — o realizado com esse nome só existe em abr e jun/**2023**, e em YouTube. No TikTok naquela janela só rodaram `Impulsionamentos` e `Uberlandia`. Ou foi cancelada, ou foi veiculada sob outro nome.
2. **TikTok é o canal que não entregou: 48% do investimento** (R$ 47,3 mil de R$ 99,1 mil) e **24% das impressões**. Meta Ads ficou em 107% e YouTube em 107%.
3. **`Impulsionamentos`: 82% do investimento, 73% das impressões** — a maior subentrega em valor absoluto (~R$ 30 mil não gastos).
4. **Estouros de verba:** Maceió 134%, Freeshop 128%, João Pessoa 104%.
5. **`Joao Pessoa - Não Pulavel`: R$ 5.949 gastos sem nenhuma meta preenchida** (linha de plano com investimento e impressões em branco). Mesmo caso em João Pessoa/YouTube/Não Sócios.

## Dois pontos que podem mudar a leitura

- **R$ 1,15 mi foram gastos em 2024 nessas mesmas campanhas fora das janelas planejadas** — `Fds1` (R$ 204 mil), `Cashback` (R$ 173 mil) e `Impulsionamentos` (R$ 144 mil) rodam recorrentemente de janeiro a agosto. Ou seja: são campanhas contínuas e o plano no arquivo cobre só um ciclo delas. Se a expectativa era que o plano cobrisse o ano, a lacuna de planejamento é bem maior que a de entrega.
- O realizado termina em **09/08/2024** (mês parcial), então agosto não serve para comparação.

**Resumo:** no recorte que tem plano, a entrega foi fiel — verba 101%, mídia 122% por CPM melhor que o previsto, cliques ~92% descontada uma meta fora de curva. Os problemas reais são pontuais e todos identificáveis: a campanha `Inauguracao` no TikTok que não saiu, o TikTok como canal (48%) e `Impulsionamentos` (82%). O achado mais relevante, porém, não é de performance e sim de processo: 94% do investimento do arquivo não tem plano para comparar.

Se quiser, posso montar o pacing dia a dia das campanhas que estouraram verba (Maceió, Freeshop) para ver se o problema foi curva de entrega ou meta subdimensionada.
