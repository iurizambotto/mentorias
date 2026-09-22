# Decisões da análise de pacing

## O que é uma linha

O arquivo empilha duas tabelas com grão diferente, separadas pela coluna `Base`. O perfil
mostrou isso: `Data de Inicio`, `Data de Termino` e `Soma de Dias_Veiculacao` são nulas
exatamente nas 16.764 linhas de `Realizado`, e `campaign_name` é nula exatamente nas 45 linhas
de `Planejado`.

| Lado | Linhas | Grão de uma linha |
|---|---|---|
| Planejado | 45 | um flight: campanha + veículo + janela (`Data de Inicio` a `Data de Termino`) |
| Realizado | 16.764 | entrega de um dia de um `campaign_name` (anúncio) dentro de uma campanha e veículo |

O grão de `Realizado` é mais fino do que "um dia de uma campanha num veículo": há 9.249 linhas
duplicadas na chave `Campanha + Veiculo + Data`. A chave única é `campaign_name + Veiculo + Data`
(zero duplicatas). Isso não muda a conta de pacing, porque somamos as linhas de qualquer jeito,
mas muda a leitura de "quantas entregas houve".

`Data` no lado Planejado é cópia de `Data de Inicio` e não foi usada.

## Decisões que mudam um número

| Decisão | Alternativa | Resultado escolhido | Resultado da alternativa | Por quê |
|---|---|---|---|---|
| Linha de Realizado que cai em vários flights sobrepostos conta **uma vez** (união das janelas por campanha+veículo) | Join direto contra cada flight, deixando a linha contar uma vez por flight | Pacing de investimento **100,75%** | **151,32%** | Instrução explícita da área. O join ingênuo criaria 223 linhas que não existem e inflaria o realizado em R$ 522.702,62 |
| Realizado só entra se a `Data` cair **dentro da janela** do flight | Somar toda a entrega da campanha naquele veículo, sem filtro de data | **100,75%** | **361,72%** | Entrega fora da janela não pertence àquele plano. O arquivo tem entrega desde 2023-01-03, e o plano começa em 2024-05-28 |
| Match exige **mesmo veículo** | Match só por campanha, somando todos os veículos | **100,75%** | **103,46%** | Um flight é comprado num veículo específico. Ignorar o veículo traz R$ 1.216.657 de entrega que nenhum flight comprou |
| Par `Joao Pessoa - Não Pulavel / Youtube Ads` fica **fora** do agregado, e é reportado à parte | Tratar o plano nulo como zero e manter no agregado | Realizado no agregado **R$ 1.041.385,17** | **R$ 1.047.334,48**, com pacing infinito | O plano desse par tem investimento nulo e 0 impressões. Dividir por ele produz infinito; somar só o numerador inflaria o agregado sem denominador que o sustente |
| Campanhas com nome parecido (`Fds1`, `Fds1 Out`, `Fds1 Set`; `Natal`, `Natal Japao`, …) são tratadas como **campanhas distintas** | Agrupar por prefixo, como o perfil sugeriu | 185 campanhas distintas, 19 com plano | Agrupamento por prefixo juntaria `Freeshop` com 5 campanhas diferentes e transformaria gasto fora do plano em gasto dentro do plano | O perfil detecta variantes por prefixo por heurística. Aqui são ações comerciais diferentes, com janelas e verbas próprias. Nenhuma foi fundida |
| `Objetivo` e `Publico` com o texto `N/a` (18 e 241 linhas) permanecem como categoria própria | Converter em nulo | Sem efeito em pacing | Sem efeito em pacing | São classificações, não métricas. Não entram em nenhum denominador |

## Checagens obrigatórias

| Checagem | Resultado |
|---|---|
| Linhas antes e depois do join | Realizado 16.764 → join ingênuo 1.107 → deduplicado **884**. O join ingênuo aumentou a contagem em 223 linhas; a dedup corrigiu |
| Dupla contagem | **147 linhas** de Realizado casaram com mais de um flight, uma delas com **4 flights**. Medido com e sem dedup: R$ 1.570.037,10 contra R$ 1.047.334,48 |
| Mesmo universo | Não. O plano cobre 2024-05-28 a 2024-07-31 e 19 campanhas; o realizado cobre 2023-01-03 a 2024-08-09 e 185 campanhas. **6,10%** do investimento realizado está dentro do plano |
| Reconciliação | Soma por campanha e soma por veículo batem com o total, diferença R$ 0,00 |
| Denominadores | **2 flights** com investimento planejado nulo e 0 impressões/cliques. Um deles é o único flight do seu par e foi isolado. Nenhuma divisão por zero passou para um número publicado: `registrar()` recusa não finito |

## Sobreposição de flights, detalhe

| Campanha | Veículo | Flights | Pares que se cruzam |
|---|---|---|---|
| Freeshop | Meta Ads | 4 | 6 |
| Joao Pessoa | Meta Ads | 2 | 1 |
| Joao Pessoa | Youtube Ads | 2 | 1 |

Em Freeshop/Meta Ads, dois flights têm a janela idêntica (2024-06-17 a 2024-06-30) e outros dois
começam em 18/06, um terminando em 30/06 e outro em 08/07. Qualquer dia entre 18/06 e 30/06 cai
nos quatro.

## O que esta análise não responde

- **Se o plano estava certo.** Pacing compara entrega com o que foi orçado, não com o que era
  razoável orçar. Um flight com 0 impressões planejadas é um erro de plano que o pacing não julga.
- **Por que 93,9% do investimento ficou fora do plano.** O arquivo não diz se essas campanhas
  tinham plano em outra planilha ou se rodaram sem plano.
- **Atribuição de um dia de entrega a um flight específico** dentro de um grupo sobreposto. A
  união de janelas resolve o total do par corretamente, mas não divide a entrega entre os flights
  que se cruzam. Para o total, isso não muda nada; para pacing por flight individual em Freeshop
  e Joao Pessoa, não há resposta possível com os dados atuais.
