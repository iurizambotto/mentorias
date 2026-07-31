---
title: "Apostila, SQL com foco em JOINs"
date: 2026-07-31
type: apostila
status: draft
project: zambotto-mentoria
tags: [engenharia_de_dados, sql]
---

# Apostila, SQL com foco em JOINs

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

## Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. Fundamentos relacionais que sustentam os JOINs](#3-fundamentos-relacionais-que-sustentam-os-joins)
- [4. Os tipos de JOIN](#4-os-tipos-de-join)
- [5. ON contra WHERE, o ponto que decide tudo](#5-on-contra-where-o-ponto-que-decide-tudo)
- [6. A base da prática](#6-a-base-da-prática)
- [7. Exercícios e entregáveis](#7-exercícios-e-entregáveis)
- [8. Mini-desafio com solução](#8-mini-desafio-com-solução)
- [9. Rubrica de validação da aprendizagem](#9-rubrica-de-validação-da-aprendizagem)
- [10. Erros comuns e como corrigir](#10-erros-comuns-e-como-corrigir)
- [11. Plano de continuidade](#11-plano-de-continuidade)
- [12. Glossário](#12-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

## 0. Como usar esta apostila

**Leitura linear.** As seções 1 a 5 constroem o modelo mental e devem ser lidas
antes da prática. A seção 5 é o coração do módulo, e é a que resolve o erro que
mais aparece em análise real.

**Revisão pontual.** Se você já escreve JOIN e veio atrás de um assunto: tipos de
JOIN na 4, `ON` contra `WHERE` na 5, diagnóstico na 10.

**Como praticar.** Execute o script da seção 6 num editor SQL, resolva os
exercícios da seção 7, e tente o mini-desafio da seção 8 antes de olhar o
gabarito. Depois volte à seção 10 para reconhecer os erros com nome.

**Pré-requisitos.** `SELECT`, `WHERE` e `GROUP BY`. Nada além disso.

**Este módulo não tem laboratório em container.** Ele declara `lab: false` no
`trilha.yml`, porque uma tabela de quatro linhas roda em qualquer editor SQL de
navegador, e montar Docker para isso seria atrito sem ganho.

Isso não significa que o SQL daqui não foi executado. Todas as consultas e todas
as tabelas de resultado desta apostila foram rodadas em PostgreSQL 16.13, e a
seção de fontes verificadas registra o quê, quando e com qual versão.

**Versões.** Verificado com PostgreSQL 16.13 em 2026-07-31.

## 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Diferenciar** quando usar `INNER JOIN`, `LEFT JOIN` e `FULL OUTER JOIN`, e
   justificar a escolha pela pergunta de negócio.
2. **Explicar** por que a posição do filtro, no `ON` ou no `WHERE`, muda o
   resultado de um JOIN externo.
3. **Montar** consultas que combinam JOIN, filtro e agregação, e interpretar a
   saída.
4. **Identificar** por que linhas desapareceram de um resultado, a partir do que
   a query diz.
5. **Reconhecer** quando linhas repetidas são erro e quando são consequência
   esperada da cardinalidade.

O verbo de cada item é o que será cobrado. "Explicar" é oral, na call. "Montar" é
query que roda.

## 2. Contexto de negócio

A startup fictícia de marketing e e-commerce da trilha tem os dados espalhados,
como toda empresa tem. Quem são os clientes está num lugar, o que eles compraram
está em outro.

| Tabela | Grão |
|---|---|
| `clientes` | uma linha por cliente |
| `pedidos` | uma linha por pedido |

As perguntas que o negócio faz atravessam as duas:

- Quais clientes compraram no período?
- Quais clientes **não** compraram?
- Qual o valor total de compras por cliente?

A segunda pergunta é a mais interessante das três, e é a que separa quem sabe
JOIN de quem decora sintaxe. Ela pede o que **não** existe no cruzamento, e
responder errado nela é o erro mais caro deste módulo: você entrega uma lista de
clientes inativos sem os clientes que nunca compraram.

Este módulo é o primeiro degrau da trilha em SQL. Os módulos seguintes assumem
que ler um JOIN é automático para você.

## 3. Fundamentos relacionais que sustentam os JOINs

### 3.1 Grão da tabela

**O que é**

Grão é o que cada linha representa. Em `clientes`, uma linha é um cliente. Em
`pedidos`, uma linha é um pedido.

**O equívoco comum**

Começar a escrever o JOIN antes de saber o grão dos dois lados. Sem isso, você
não tem como prever quantas linhas o resultado deve ter, e portanto não tem como
perceber que ele veio errado.

### 3.2 Chave primária e chave estrangeira

**O que é**

A chave primária identifica unicamente uma linha, como `clientes.cliente_id`. A
chave estrangeira aponta para a primária de outra tabela, como
`pedidos.cliente_id`.

JOIN, na prática, é o vínculo entre essas chaves.

**O equívoco comum**

Assumir que a chave estrangeira existe como restrição no banco. Em data
warehouse, frequentemente ela é apenas uma convenção: o relacionamento existe na
cabeça de quem modelou e não é garantido pelo banco. Isso significa que
`pedidos.cliente_id` pode conter um valor que não existe em `clientes`, e o
`INNER JOIN` vai silenciosamente descartar aquele pedido.

### 3.3 Cardinalidade

**O que é**

Cardinalidade descreve como uma entidade se relaciona com outra: um para um, um
para muitos, ou muitos para muitos.

No nosso caso, um cliente pode ter vários pedidos. É um para muitos.

**Como funciona na prática**

A consequência é direta: depois do JOIN, um cliente aparece uma vez por pedido.
Ana, com dois pedidos, aparece duas vezes. Isso não é duplicidade, é o grão do
resultado, que passou a ser o do lado "muitos".

**O equívoco comum**

Somar uma coluna do lado "um" depois de um JOIN um para muitos. Se você somasse
um valor da tabela `clientes` depois de juntar com `pedidos`, o valor de Ana
entraria duas vezes. É o erro de duplicação de métrica, e ele não gera erro de
SQL: gera número errado.

### 3.4 Os três sinais para olhar em todo resultado

| Sinal | O que costuma significar |
|---|---|
| Nulos | Ausência de correspondência, comum e esperada em `LEFT JOIN` |
| Linhas faltando | JOIN restritivo demais, ou filtro na posição errada |
| Linhas repetidas | Em geral, a cardinalidade explicando o grão do resultado |

O terceiro é o que mais gera alarme falso. Antes de tratar repetição como
defeito, confirme a cardinalidade.

## 4. Os tipos de JOIN

Antes dos tipos, os conjuntos. **A** é o conjunto de clientes. **B** é o conjunto
de clientes que aparecem em pedidos.

O diagrama de Venn ajuda na intuição de pertencimento, e tem um limite que vale
dizer logo: **ele não mostra multiplicidade de linhas.** Ana aparece uma vez no
diagrama e duas vezes no resultado.

### 4.1 INNER JOIN, a interseção

Retorna apenas o que existe em A e em B ao mesmo tempo. A documentação do
PostgreSQL descreve assim: para cada linha de T1, a tabela resultante tem uma
linha para cada linha de T2 que satisfaz a condição de junção.

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /         \          /         \
    /     A     \________/     B     \
    \           /########\           /
     \_________/##########\_________/

Area hachurada = resultado do INNER JOIN
```

Quando usar: quando só interessa registro com correspondência nos dois lados.

### 4.2 LEFT JOIN, preserva a esquerda

Retorna tudo de A e, quando houver, os dados de B. A documentação é precisa sobre
o mecanismo: primeiro a junção interna é feita; depois, para cada linha de T1 que
não satisfez a condição com nenhuma linha de T2, uma linha é acrescentada com
nulos nas colunas de T2. Logo a tabela resultante tem sempre pelo menos uma linha
para cada linha de T1.

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /#########\          /         \
    /###########\________/     B     \
    \###########/########\           /
     \#########/##########\_________/

Area hachurada = todo o conjunto A
```

Quando usar: quando cobrir a base da esquerda é requisito de negócio. A pergunta
"quais clientes não compraram" só existe aqui.

### 4.3 FULL OUTER JOIN, a união

Retorna tudo de A e tudo de B. Pelo mecanismo da documentação: a junção interna é
feita, depois entram as linhas de T1 sem correspondência com nulos do lado de T2,
e também as linhas de T2 sem correspondência com nulos do lado de T1.

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /#########\          /#########\
    /###########\________/###########\
    \###########/########\###########/
     \#########/##########\#########/

Area hachurada = A inteiro mais B inteiro
```

Quando usar: auditoria de cobertura e reconciliação entre duas bases. É o JOIN
que responde "o que existe de um lado e não do outro, nos dois sentidos".

Uma ressalva de portabilidade: o `FULL OUTER JOIN` funciona no PostgreSQL, e foi
executado nesta apostila. Alguns engines analíticos o suportam de forma parcial ou
com restrição de sintaxe. Se o seu destino não é PostgreSQL, confira antes de
depender dele.

### 4.4 Comparativo

| Tipo | Regra | Melhor uso | Pergunta que ele responde |
|---|---|---|---|
| `INNER JOIN` | Só correspondência em ambos | Análise de interseção | Quem comprou? |
| `LEFT JOIN` | Preserva a esquerda | Cobertura da base principal | Quem não comprou? |
| `FULL OUTER JOIN` | Preserva os dois lados | Reconciliação e auditoria | O que não bate entre as bases? |

## 5. ON contra WHERE, o ponto que decide tudo

### 5.1 A regra, e a razão dela

**O que é**

`ON` controla como as tabelas se conectam. `WHERE` filtra o resultado depois da
conexão.

A documentação do PostgreSQL diz o porquê em uma frase: uma restrição colocada na
cláusula `ON` é processada **antes** da junção, e uma restrição colocada no
`WHERE` é processada **depois**. Com junção interna isso não importa. Com junção
externa, importa muito.

A mesma documentação alerta que a cláusula `ON` de uma junção externa não é
equivalente a uma condição `WHERE`, porque ela resulta na adição de linhas, para
as linhas sem correspondência, e não apenas na remoção.

### 5.2 O caso correto, filtro no ON

Todos os clientes, com o total apenas do período:

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0.00) AS valor_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
   AND p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_periodo DESC, c.cliente_id;
```

Resultado, executado de verdade:

```
 cliente_id | nome  | valor_periodo
------------+-------+---------------
          1 | Ana   |        200.00
          2 | Bruno |         50.00
          3 | Carla |          0.00
          4 | Diego |          0.00
(4 rows)
```

Quatro clientes, quatro linhas. Carla tem pedido, mas fora do período, e por isso
aparece com zero. Diego não tem pedido nenhum, e também aparece.

### 5.3 O caso que quebra a cobertura em silêncio

O mesmo objetivo, com o filtro no `WHERE`:

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0.00) AS valor_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
WHERE p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_periodo DESC, c.cliente_id;
```

Resultado, executado de verdade:

```
 cliente_id | nome  | valor_periodo
------------+-------+---------------
          1 | Ana   |        200.00
          2 | Bruno |         50.00
(2 rows)
```

**Duas linhas em vez de quatro.** Carla e Diego desapareceram, e nada na saída
avisa que eles existiam. O `LEFT JOIN` os manteve com nulos nas colunas de
`pedidos`, e o `WHERE` os eliminou depois, porque `NULL BETWEEN alguma coisa` não
é verdadeiro.

**O equívoco comum**

Escrever a segunda query, receber um resultado plausível, e entregar. Ela não dá
erro. Ela responde outra pergunta.

**Como inspecionar**

Conte as linhas. Se você começou de uma tabela com quatro clientes e usou
`LEFT JOIN`, o resultado agrupado por cliente tem que ter quatro linhas. Menos que
isso significa que algo filtrou depois da junção.

A mensagem do módulo, em uma frase:

> Se a intenção é manter todos os clientes, o filtro da tabela da direita vai no
> `ON`, não no `WHERE`.

## 6. A base da prática

Qualquer editor SQL de navegador serve. As três opções abaixo respondiam em
2026-07-31:

| Ferramenta | Para quê |
|---|---|
| DB Fiddle, com PostgreSQL | O mais fiel ao que esta apostila executou |
| SQLBolt | Exercício guiado, bom para aquecer |
| W3Schools SQL Tryit | Contingência, quando os outros estiverem fora |

Script base, para copiar e executar:

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, criou as tabelas e inseriu 4 mais 4 linhas, 2026-07-31 -->

```sql
CREATE TABLE clientes (
    cliente_id INT PRIMARY KEY,
    nome TEXT,
    segmento TEXT
);

CREATE TABLE pedidos (
    pedido_id INT PRIMARY KEY,
    cliente_id INT,
    data_pedido DATE,
    valor NUMERIC(10,2)
);

INSERT INTO clientes (cliente_id, nome, segmento) VALUES
(1, 'Ana', 'vip'),
(2, 'Bruno', 'regular'),
(3, 'Carla', 'vip'),
(4, 'Diego', 'novo');

INSERT INTO pedidos (pedido_id, cliente_id, data_pedido, valor) VALUES
(101, 1, '2026-03-01', 120.00),
(102, 1, '2026-03-10', 80.00),
(103, 2, '2026-03-08', 50.00),
(104, 3, '2026-03-15', 200.00);
```

A base é pequena de propósito, e cada linha tem função didática:

- quatro clientes e quatro pedidos;
- Ana tem dois pedidos, para exercitar cardinalidade um para muitos;
- Carla tem um pedido **fora** da janela de 1 a 10 de março, para separar "não
  comprou" de "não comprou no período";
- Diego não tem pedido nenhum, o caso que só o `LEFT JOIN` mostra.

## 7. Exercícios e entregáveis

**Exercício 1: quem comprou**

Objetivo: usar `INNER JOIN` e reconhecer quem o resultado exclui.

Contexto: a base da seção 6.

Entregável: a query que lista cliente, pedido e valor de quem comprou, mais uma
frase dizendo quem ficou de fora e por quê.

Gabarito:

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```sql
SELECT
    c.cliente_id,
    c.nome,
    p.pedido_id,
    p.valor
FROM clientes c
INNER JOIN pedidos p
    ON c.cliente_id = p.cliente_id
ORDER BY c.cliente_id, p.pedido_id;
```

```
 cliente_id | nome  | pedido_id | valor
------------+-------+-----------+--------
          1 | Ana   |       101 | 120.00
          1 | Ana   |       102 |  80.00
          2 | Bruno |       103 |  50.00
          3 | Carla |       104 | 200.00
(4 rows)
```

Por que a resposta é essa: Diego não aparece porque não tem pedido, e o
`INNER JOIN` só devolve o que tem correspondência nos dois lados. Repare também
que Ana ocupa duas linhas, porque o grão do resultado passou a ser o pedido.

**Exercício 2: quem não comprou**

Objetivo: usar `LEFT JOIN` para cobrir a base da esquerda, e isolar os sem
correspondência.

Contexto: a base da seção 6.

Entregável: duas queries, uma listando todos os clientes com o pedido quando
houver, outra listando apenas quem não tem pedido.

Gabarito, parte um:

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```sql
SELECT
    c.cliente_id,
    c.nome,
    p.pedido_id
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
ORDER BY c.cliente_id, p.pedido_id;
```

```
 cliente_id | nome  | pedido_id
------------+-------+-----------
          1 | Ana   |       101
          1 | Ana   |       102
          2 | Bruno |       103
          3 | Carla |       104
          4 | Diego |
(5 rows)
```

Gabarito, parte dois:

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```sql
SELECT
    c.cliente_id,
    c.nome
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
WHERE p.pedido_id IS NULL;
```

```
 cliente_id | nome
------------+-------
          4 | Diego
(1 row)
```

Por que a resposta é essa: a célula vazia de Diego na primeira query é um `NULL`,
e é justamente por ele que a segunda query filtra. Este é o único uso de `WHERE`
sobre coluna da direita que **não** contradiz o `LEFT JOIN`: aqui a intenção é
mesmo ficar só com quem não tem correspondência.

**Exercício 3: resumo por cliente**

Objetivo: combinar JOIN com agregação e tratar ausência de valor.

Contexto: a base da seção 6.

Entregável: a query com valor total e quantidade de pedidos por cliente, mais a
explicação do que acontece com Diego em cada uma das duas colunas.

Gabarito:

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0.00) AS valor_total,
    COUNT(p.pedido_id) AS total_pedidos
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
GROUP BY c.cliente_id, c.nome
ORDER BY valor_total DESC, c.cliente_id;
```

```
 cliente_id | nome  | valor_total | total_pedidos
------------+-------+-------------+---------------
          1 | Ana   |      200.00 |             2
          3 | Carla |      200.00 |             1
          2 | Bruno |       50.00 |             1
          4 | Diego |        0.00 |             0
(4 rows)
```

Por que a resposta é essa. O `COALESCE` troca o total nulo de Diego por zero, e
sem ele a coluna viria vazia. O `COUNT(p.pedido_id)` devolve 0 para Diego porque
`COUNT` de uma coluna ignora nulos; se estivesse escrito `COUNT(*)`, Diego
apareceria com 1, contando a linha que o `LEFT JOIN` fabricou. Essa diferença
entre `COUNT(coluna)` e `COUNT(*)` depois de um `LEFT JOIN` é sutil e cara.

Repare no empate entre Ana e Carla, resolvido pelo `cliente_id` no `ORDER BY`.
Ordenação sem critério de desempate produz saída que muda de execução para
execução.

**Exercício 4: o filtro na posição errada**

Objetivo: reproduzir de propósito o erro da seção 5.

Contexto: a base da seção 6.

Entregável: as duas versões da query de período, a contagem de linhas de cada
uma, e a explicação de qual pergunta cada uma responde.

Gabarito: as duas queries são as das seções 5.2 e 5.3, com quatro e duas linhas
respectivamente. Escrever a explicação com as suas palavras é o exercício.

## 8. Mini-desafio com solução

**Enunciado**

Monte uma query que traga **todos** os clientes com o total de compras apenas no
período de 1 a 10 de março de 2026, incluindo quem não comprou no período. Ordene
por maior valor total.

**Dicas**

1. Comece de `clientes`.
2. Use `LEFT JOIN` para preservar a cobertura.
3. O filtro de período tem uma posição certa, e a seção 5 diz qual.
4. Agregue com `SUM` e trate o nulo.

**Gabarito comentado**

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0.00) AS valor_total_periodo,
    COUNT(p.pedido_id) AS qtd_pedidos_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
   AND p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_total_periodo DESC, c.cliente_id;
```

```
 cliente_id | nome  | valor_total_periodo | qtd_pedidos_periodo
------------+-------+---------------------+---------------------
          1 | Ana   |              200.00 |                   2
          2 | Bruno |               50.00 |                   1
          3 | Carla |                0.00 |                   0
          4 | Diego |                0.00 |                   0
(4 rows)
```

**Interpretação**

Carla e Diego têm o mesmo zero e chegaram nele por caminhos diferentes. Carla
comprou, no dia 15, fora da janela. Diego nunca comprou. A query não distingue os
dois, e essa é a limitação dela.

Se o negócio precisa separar "não comprou no período" de "nunca comprou", isso é
uma coluna a mais, não um JOIN diferente. Perceber isso é o que separa a resposta
correta da boa resposta.

**Um detalhe que só aparece executando**

O fallback do `COALESCE` está escrito como `0.00` e não como `0`. Os dois
funcionam e devolvem tipo numérico, mas a escala do literal aparece na saída: com
`0`, a linha de Diego imprime `0`, e as outras imprimem `200.00`. Coluna
financeira com escala inconsistente na mesma saída é ruído para quem lê, e o
conserto custa dois caracteres.

## 9. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Tipos de JOIN | Usa `INNER` para tudo | Escolhe pelo que a pergunta pede | Justifica com a pergunta de negócio, sem citar sintaxe |
| `ON` contra `WHERE` | Comete o erro e não percebe | Sabe a regra e a aplica | Explica por que o `WHERE` elimina a linha com nulo |
| Grão e cardinalidade | Trata repetição como defeito | Reconhece o grão do resultado | Antecipa a duplicação de métrica antes de somar |
| Tratamento de nulo | Entrega coluna vazia | Usa `COALESCE` na apresentação | Sabe a diferença entre `COUNT(coluna)` e `COUNT(*)` |
| Diagnóstico | Ajusta a query até parecer certa | Conta linhas e compara com o esperado | Localiza a causa a partir da contagem |
| Comunicação | Descreve a query | Descreve o resultado | Traduz o resultado em linguagem de negócio |

Checklist rápido, para a call:

- [ ] Entendeu chave primária, chave estrangeira e grão das tabelas.
- [ ] Diferenciou `INNER`, `LEFT` e `FULL OUTER`.
- [ ] Demonstrou domínio de `ON` contra `WHERE`.
- [ ] Construiu a query do mini-desafio sem gabarito.
- [ ] Explicou a diferença entre o zero de Carla e o zero de Diego.

## 10. Erros comuns e como corrigir

**Explosão de linhas, o produto cartesiano**

Sintoma: o resultado vem com muito mais linhas do que qualquer um dos lados. Com
4 clientes e 4 pedidos, vem com 16.

Causa, e aqui vale desfazer um mito. Escrever `JOIN` **sem** `ON` não produz
produto cartesiano no PostgreSQL: produz erro de sintaxe, e você descobre na hora.

<!-- verificacao: nivel 3, executado em PostgreSQL 16.13, saida real, 2026-07-31 -->

```
ERROR:  syntax error at or near ";"
LINE 1: SELECT count(*) FROM clientes c JOIN pedidos p;
```

O produto cartesiano de verdade vem de dois outros caminhos, os dois medidos na
base desta apostila e os dois devolvendo 16 linhas:

- a junção por vírgula, `FROM clientes c, pedidos p`, sem condição no `WHERE`;
- uma condição que não relaciona as chaves, como `ON 1=1`.

Correção: conferir se o `ON` liga as chaves de verdade, e desconfiar de junção por
vírgula em query nova. A conta de sanidade é rápida: 4 vezes 4 é 16, e 16 nunca
foi a resposta esperada.

**Filtro da tabela da direita no `WHERE` depois de `LEFT JOIN`**

Sintoma: clientes desaparecem do resultado, sem nenhum erro.

Causa: o `WHERE` roda depois da junção e elimina as linhas em que a coluna da
direita é nula.

Correção: mover o filtro para o `ON`. Confirmar contando as linhas, como na seção
5.3.

**Somar sem agrupar corretamente**

Sintoma: erro de coluna que não está em função de agregação nem no `GROUP BY`.

Causa: coluna no `SELECT` que não é agregada e não foi agrupada.

Correção: incluir no `GROUP BY` toda coluna não agregada do `SELECT`.

**`COUNT(*)` depois de `LEFT JOIN`**

Sintoma: cliente sem pedido aparece com contagem 1 em vez de 0.

Causa: `COUNT(*)` conta a linha que o `LEFT JOIN` fabricou com nulos. `COUNT` de
uma coluna ignora nulos.

Correção: contar a coluna do lado direito, como `COUNT(p.pedido_id)`.

**Não tratar nulo na saída analítica**

Sintoma: métrica em branco no relatório.

Causa: agregação sobre conjunto vazio devolve nulo, não zero.

Correção: `COALESCE` na apresentação, com o literal na mesma escala das outras
linhas.

**Interpretar repetição como duplicidade**

Sintoma: suspeita de dado duplicado onde não há.

Causa: relacionamento um para muitos. Ana com dois pedidos ocupa duas linhas.

Correção: confirmar a cardinalidade antes de investigar. Se a repetição é
esperada e o problema é a métrica, agregue.

**Ordenação sem desempate**

Sintoma: a mesma query devolve linhas em ordem diferente entre execuções.

Causa: `ORDER BY` por uma coluna com valores repetidos, como o empate de 200.00
entre Ana e Carla.

Correção: acrescentar uma coluna estável de desempate, como a chave.

## 11. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 2 e 4. O quarto é o que mais se parece com o erro que você vai
cometer em produção.

**O que estudar em seguida, dentro da trilha**

O próximo degrau natural é JOIN entre mais de duas tabelas, e a introdução de CTE
para manter a query legível. Depois disso, o bloco de armazenamento da trilha
mostra onde essas tabelas moram de verdade e por que a forma de guardá-las decide
o custo da consulta.

O módulo de transformação com dbt retoma tudo isto num contexto novo: lá os
`SELECT` que você escreve aqui viram modelos versionados e testados.

**O que aprofundar por conta**

Reescreva os exercícios com outra janela de datas, e depois com uma terceira
tabela, por exemplo campanhas, para exercitar o JOIN em cadeia. Não precisa de
ferramenta nova.

**O que não perseguir agora**

Otimização de plano de execução e índices. Eles importam, e importam depois de a
leitura de JOIN ser automática para você.

## 12. Glossário

| Termo | Significado |
|---|---|
| Agregação | Resumo de dados com funções como `SUM`, `COUNT` e `AVG` |
| Cardinalidade | Padrão de relacionamento entre duas entidades |
| Chave estrangeira | Coluna que referencia a chave primária de outra tabela |
| Chave primária | Coluna que identifica unicamente uma linha |
| `COALESCE` | Função que devolve o primeiro valor não nulo da lista |
| Grão | O que cada linha de uma tabela representa |
| JOIN | Operação que combina linhas de duas tabelas por uma condição |
| Junção externa | JOIN que preserva linhas sem correspondência, com nulos |
| Junção interna | JOIN que devolve apenas linhas com correspondência |
| `NULL` | Ausência de valor, diferente de zero e de texto vazio |
| Produto cartesiano | Cruzamento de todas as linhas com todas, quando falta condição |

## Referências

Documentação oficial do PostgreSQL 16, consultada em 2026-07-31:

- Expressões de tabela e tipos de junção: https://www.postgresql.org/docs/16/queries-table-expressions.html
- Funções condicionais, incluindo `COALESCE`: https://www.postgresql.org/docs/16/functions-conditional.html

Ferramentas de prática, conferidas em 2026-07-31:

- DB Fiddle: https://www.db-fiddle.com/
- SQLBolt: https://sqlbolt.com/
- W3Schools SQL Tryit: https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all

## Fontes verificadas (2026-07-31)

- Uma restrição na cláusula `ON` é processada antes da junção, e uma restrição no
  `WHERE` é processada depois. Isso não importa em junção interna e importa muito
  em junção externa. A mesma documentação afirma que a cláusula `ON` de uma junção
  externa não é equivalente a uma condição `WHERE`, porque resulta na adição de
  linhas para as entradas sem correspondência, e não apenas na remoção.
  https://www.postgresql.org/docs/16/queries-table-expressions.html
- O mecanismo do `LEFT OUTER JOIN` é: primeiro a junção interna, depois, para cada
  linha de T1 sem correspondência em T2, uma linha com nulos nas colunas de T2.
  Logo o resultado tem sempre pelo menos uma linha por linha de T1. O
  `FULL OUTER JOIN` faz o mesmo nos dois sentidos.
  https://www.postgresql.org/docs/16/queries-table-expressions.html
- Todo o SQL desta apostila foi executado em PostgreSQL 16.13 em 2026-07-31, em
  container descartável, e todas as tabelas de resultado transcritas aqui são a
  saída real do `psql`. Isso inclui o script de criação, as quatro consultas dos
  exercícios, as duas consultas comparativas da seção 5, o mini-desafio e o
  `FULL OUTER JOIN`. Nenhuma tabela de resultado desta apostila foi escrita de
  memória.
- O contraste central do módulo foi medido: com o filtro no `ON`, a consulta da
  seção 5.2 devolve 4 linhas; com o mesmo filtro no `WHERE`, a consulta da seção
  5.3 devolve 2. As duas foram executadas na mesma base.
- O `FULL OUTER JOIN` foi executado com sucesso no PostgreSQL 16.13, devolvendo 5
  linhas. A ressalva de portabilidade da seção 4.3 não foi testada em outros
  engines, e está escrita como ressalva justamente por isso.
- A escala do literal usado como fallback do `COALESCE` aparece na saída. Com
  `COALESCE(SUM(p.valor), 0)` a linha sem pedido imprime `0`, e com
  `COALESCE(SUM(p.valor), 0.00)` imprime `0.00`. Nos dois casos o tipo devolvido é
  numérico, conferido com `pg_typeof`. Esta apostila usa a forma decimal, e as
  tabelas de resultado refletem isso.
  https://www.postgresql.org/docs/16/functions-conditional.html
- As três ferramentas de prática da seção 6 responderam com código 200 em
  2026-07-31.
- O `JOIN` sem `ON` é erro de sintaxe no PostgreSQL 16.13, e não produto
  cartesiano. O produto cartesiano de 16 linhas foi reproduzido de duas outras
  formas na base desta apostila: junção por vírgula sem condição, e `ON 1=1`. A
  versão anterior desta apostila atribuía a explosão de linhas à ausência do `ON`,
  e a execução mostrou que isso está errado.
