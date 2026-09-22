# Decisões da análise de pacing

## Grão: o arquivo empilha duas tabelas

O arquivo tem extensão `.xls` mas é CSV UTF-8 com BOM, separador vírgula, quebra CRLF.
A coluna `Base` separa duas tabelas com grão diferente, e o perfil confirma isso pelo padrão
de nulos: `campaign_name` é nulo exatamente nas 45 linhas de Planejado, e
`Data de Inicio` / `Data de Termino` / `Soma de Dias_Veiculacao` são nulas exatamente nas
16.764 linhas de Realizado.

| Tabela | Linhas | O que uma linha é |
|---|---|---|
| Planejado | 45 | Um flight: campanha × veículo × janela de veiculação |
| Realizado | 16.764 | A entrega de um dia: campanha × veículo × data |

Em Planejado, a coluna `Data` repete `Data de Inicio` e não tem significado próprio.

## A regra de casamento

Uma linha de Realizado pertence a um flight quando tem a **mesma campanha**, o **mesmo
veículo**, e `Data` dentro de `[Data de Inicio, Data de Termino]`, limites incluídos.
Entrega fora da janela não pertence ao plano, e campanha sem linha de Planejado fica fora
da conta.

## O bloco de plano, e por que ele existe

O plano tem flights sobrepostos: mesma campanha, mesmo veículo, janelas que se cruzam.
São 8 flights em 3 grupos.

| Campanha | Veículo | Janela unida | Flights |
|---|---|---|---|
| Freeshop | Meta Ads | 2024-06-17 a 2024-07-08 | 4 |
| Joao Pessoa | Meta Ads | 2024-06-01 a 2024-06-30 | 2 |
| Joao Pessoa | Youtube Ads | 2024-06-01 a 2024-06-30 | 2 |

147 linhas de Realizado caem na janela de mais de um flight, e uma delas chega a ser coberta
por 4 flights ao mesmo tempo. Atribuir essa linha a um flight escolhido seria arbitrário, e
atribuí-la a todos seria contá-la mais de uma vez.

A saída adotada é o **bloco de plano**: flights sobrepostos da mesma campanha e veículo viram
uma unidade só, que soma o planejado dos flights e cobre a união das janelas. Os 45 flights
viram 40 blocos, e cada linha de Realizado passa a casar com no máximo um bloco
(`real.max_blocos_por_linha` = 1). A contagem única fica garantida por construção, não por
uma correção aplicada depois.

O custo dessa escolha: dentro de um bloco sobreposto não dá para dizer o pacing de cada
flight isolado. Para Freeshop, Joao Pessoa Meta e Joao Pessoa Youtube o número é do grupo.

## Denominadores

Dois flights têm impressões e cliques planejados iguais a zero e investimento planejado nulo:
`Joao Pessoa / Youtube Ads` e `Joao Pessoa - Não Pulavel / Youtube Ads`, ambos de
2024-06-01 a 2024-06-30. São as únicas divisões por zero possíveis no arquivo.

O primeiro está num bloco com outro flight que tem meta, então o bloco fica com denominador
utilizável. O segundo é um bloco inteiro sem meta: recebeu 26 dias de entrega,
558.959 impressões e R$ 5.949,31, e **fica fora do pacing**, com a razão marcada como
indefinida e nunca como zero.

`registrar` recusa valor não finito, então nenhuma divisão por zero chega a um número citado.

## Tabela de decisões

Cada alternativa foi calculada, não estimada. Os identificadores estão em `analise/numeros.json`.

| Decisão | Alternativa | Resultado escolhido | Resultado da alternativa | Por quê |
|---|---|---|---|---|
| Linha de Realizado em flights sobrepostos conta uma vez só, via bloco de plano | Somar a linha em cada flight que a cobre | Pacing impressões 1,2170 · investimento 1,0075 · cliques 0,4732 | Pacing impressões 2,1925 · investimento 1,5080 · cliques 0,6762 | A alternativa infla impressões em 80% inventando entrega que não existe. É o erro mais caro do arquivo. |
| Bloco sem meta utilizável sai do pacing | Somar a entrega dele com denominador zero | Impressões 1,2170 | Impressões 1,2210 | Somar entrega sem a meta correspondente mistura numerador sem denominador e infla o pacing. Efeito pequeno aqui, mas cresce com o volume sem meta. |
| Pacing agregado: soma do realizado ÷ soma do planejado | Média simples das razões dos blocos | Impressões 1,2170 · cliques 0,4732 | Impressões 1,4500 · cliques 1,4623 | A média simples dá o mesmo peso ao menor bloco, de R$ 3.570,00, e ao maior, de R$ 130.157,56, e inverte o resultado de cliques de forte queda para superação. |
| Casar por campanha **e** veículo | Casar só por campanha e janela | Impressões 1,2170 · investimento 1,0075 | Impressões 1,2280 · investimento 1,0288 | O plano é por veículo; ignorar o veículo deixa entrega de um veículo pagar a meta de outro. Efeito pequeno no total, mas apaga o problema do TikTok. |
| Nome de campanha casa exato | Agrupar variantes por prefixo (`Fds1 Set` → `Fds1`) | Impressões 1,2170 | Impressões 1,2170 | Sem diferença: as 1.361 linhas que mudariam de nome são de 2023, fora de qualquer janela de flight. Registrado porque o perfil apontou as variantes e a conferência precisava ser feita. |

## Universo: o que a conta cobre

O plano cobre 2024-05-28 a 2024-07-31. O Realizado vai de 2023-01-03 a 2024-08-09.

Das 16.764 linhas de Realizado, 884 entram no pacing e 15.880 ficam de fora: 14.375 porque a
campanha e veículo não têm nenhum flight, e 1.505 porque a data cai fora da janela do flight
daquela campanha e veículo. São 166 campanhas com entrega e sem nenhuma linha de plano.

A conta de pacing cobre 6,1% do investimento realizado no arquivo. Esse recorte é o que o
plano permite avaliar, e os R$ 16.027.790,90 restantes não são erro: são atividade fora
deste plano. Nenhuma conclusão sobre o total investido pela área sai desta análise.

## O que esta análise não responde

- Pacing de cada flight isolado dentro dos 3 blocos sobrepostos.
- Se a entrega fora da janela foi replanejamento legítimo ou falha de execução: o arquivo não
  traz o motivo.
- Resultado de negócio. O arquivo tem mídia entregue, não conversão nem receita.
- `Objetivo` tem 18 valores em texto de nulo e `Publico` tem 241. Não foram usados como
  recorte por isso.
