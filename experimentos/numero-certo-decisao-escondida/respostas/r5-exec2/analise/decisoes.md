# Decisões da análise de pacing

## O que é uma linha

O arquivo `BASE DE PACING_v2.csv.xls` é um CSV UTF-8 com BOM, não um `.xls`. A extensão não
corresponde ao conteúdo; a leitura é feita como CSV.

Ele empilha duas tabelas com grãos diferentes, separadas pela coluna `Base`:

| Tabela | Linhas | O que uma linha é | Colunas exclusivas |
|---|---|---|---|
| Planejado | 45 | Um flight: pedaço de campanha num veículo, com janela de veiculação | `Data de Inicio`, `Data de Termino`, `Soma de Dias_Veiculacao` |
| Realizado | 16.764 | A entrega de um único dia, de uma campanha, num veículo | `campaign_name` |

As colunas de janela existem também nas linhas de Realizado, sempre nulas, e as de Planejado têm
`campaign_name` sempre nulo. O perfil detectou os dois blocos de nulos casados, que é o que
denuncia a mistura de tabelas.

Consequência prática que quase passou: num `merge` ingênuo, as colunas de janela do lado
Realizado sobrevivem e as do plano são renomeadas com sufixo, de modo que a comparação de datas
cai sobre colunas nulas e devolve **zero** entregas atribuídas. A versão corrigida remove as
colunas nulas antes do join e afirma, com `assert`, que a janela não é nula depois dele.

## Regra de atribuição

Uma linha de Realizado pertence a um flight quando tem a **mesma campanha**, o **mesmo veículo**
e a `Data` dentro de `[Data de Inicio, Data de Termino]`, com as duas pontas incluídas.

## Grão do pacing: campanha × veículo, não flight

O plano tem flights sobrepostos. Onde há sobreposição, o Realizado é diário e não traz nada que
permita dizer a qual flight aquele dia pertence, porque os flights sobrepostos se distinguem por
`Publico`, `Modalidade` ou `Objetivo`, atributos que o Realizado não repete de forma compatível.
Então o pacing é calculado por campanha × veículo: o denominador soma os flights daquele par e o
numerador conta cada entrega **uma única vez**.

O pacing por flight isolado está em `flights_detalhe.csv` com a coluna `entrega_compartilhada`,
que marca os 8 flights cujo realizado é disputado. Esses 8 não podem ser somados entre si.

## Decisões que mudam um número

| Decisão | Alternativa | Resultado escolhido | Resultado da alternativa | Por quê |
|---|---|---|---|---|
| Cada entrega conta uma vez, mesmo quando vários flights a reivindicam | Somar a entrega uma vez por flight | Pacing de investimento **100,8%**, impressões **121,7%** | Investimento **151,3%**, impressões **219,7%** | 147 entregas casam com mais de um flight, uma delas com 4. Sem deduplicar, a mesma veiculação seria contada até 4 vezes e o painel mostraria entrega que não existiu |
| Entrega só conta dentro da janela do flight | Contar toda entrega da campanha e veículo, sem olhar data | Investimento **100,8%** | Investimento **361,7%** | O Realizado cobre jan/2023 a ago/2024 e o plano cobre mai a jul/2024. Sem o filtro, entrega de 2023 pagaria plano de 2024 |
| `Data de Termino` inclusiva | Término exclusivo | Investimento **100,8%** | Investimento **87,5%** | O último dia é dia de veiculação contratado. Excluí‑lo derrubaria o pacing em 13 pontos e criaria um déficit inexistente |
| Campanha casa por nome exato | Agrupar por prefixo, `Inauguracao Barra` contando como `Inauguracao` | Investimento **100,8%** | Investimento **100,8%** | Sem efeito: as 1.361 linhas que mudariam de campanha caem todas fora das janelas ou em outro veículo. Registrado porque a hipótese é plausível e precisava ser descartada com número, não com opinião |
| Par sem denominador válido sai do índice agregado e é reportado à parte | Tratar denominador nulo como zero e o pacing como 0% | 25 pares no índice, 1 reportado à parte | 26 pares, puxando o índice para baixo com uma divisão inválida | Dividir por zero não é entrega ruim, é ausência de plano. Misturar as duas coisas esconde as duas |

## Denominadores conferidos

| Situação | Quantidade | Tratamento |
|---|---|---|
| Flights sem investimento orçado (`NaN`) | 2 | Fora do denominador de investimento |
| Flights com impressões ou cliques orçados em zero | 2 | Fora do denominador dessas métricas |
| Pares campanha × veículo sem pacing calculável | 1 (`Joao Pessoa - Não Pulavel` em Youtube Ads) | Reportado à parte, nunca como 0% |
| Flights planejados sem nenhuma entrega na janela | 1 (`Inauguracao` em Tiktok Ads, R$ 24.797,50) | Pacing 0%, que aqui é entrega real de zero, não divisão inválida |

A função `pacing()` devolve `None` quando o denominador é zero ou nulo, e o livro de números
recusa valor não finito. Nenhuma divisão por zero chega a um entregável.

## Reconciliação

- Planejado 45 + Realizado 16.764 = 16.809 linhas do arquivo.
- Dentro do plano 884 + fora 15.880 = 16.764 linhas de Realizado.
- O fora se decompõe, sem interseção, em 10.209 linhas de campanha sem plano, 4.166 de veículo
  fora do plano da campanha e 1.505 de data fora da janela.
- Investimento dentro do plano + fora do plano = R$ 17.075.125,38, o total do Realizado.

Cada uma dessas igualdades é verificada por `assert` nos scripts, não conferida a olho.

## O que a análise não responde

- **Não há pacing por flight onde há sobreposição.** O dado não permite. Seria preciso uma chave
  de flight no Realizado, ou pelo menos `Publico` e `Modalidade` compatíveis entre os dois lados.
- **Não há juízo sobre as 166 campanhas sem plano.** R$ 12.098.469,92 rodaram fora deste plano.
  Podem ser outro plano, outra verba ou falta de registro; o arquivo não distingue.
- **O pacing de cliques não mede entrega de cliques.** O plano deriva cliques de uma premissa de
  CTR por flight, que varia de 0,05% a 1,00%. É premissa, não meta contratada.
