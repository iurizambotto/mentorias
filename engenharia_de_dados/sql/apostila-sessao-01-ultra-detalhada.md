# Apostila — Sessão 01: SQL com foco em JOINs

> Base de leitura da sessão única de 60 minutos.
> Domínio de referência: CRM e marketing (clientes e pedidos).

---

## Sumário

0. Como usar esta apostila
1. Objetivo pedagógico da sessão
2. Contexto de negócio: por que JOIN importa
3. Fundamentos relacionais que sustentam os JOINs
4. JOINs com leitura conceitual e diagrama de Venn
5. `ON` vs `WHERE` (ponto mais importante da sessão)
6. Setup e base de dados da prática
7. Roteiro de condução (60 minutos)
8. Exercícios guiados com gabarito comentado
9. Mini-desafio final com solução e interpretação
10. Rubrica de validação da aprendizagem
11. Erros comuns e como corrigir
12. Plano de continuidade pós-sessão
13. Glossário rápido
14. Referências

---

## 0. Como usar esta apostila

Esta apostila foi escrita para servir como material principal de leitura da sessão.

Uso recomendado:

1. Ler as seções 1 a 5 antes da prática.
2. Executar as queries da seção 8 no editor SQL.
3. Tentar resolver o mini-desafio (seção 9) sem olhar a solução.
4. Voltar à seção 11 para revisar erros e anti-padrões.

Objetivo desta abordagem: transformar o conteúdo em repertório aplicável em cenário real, e não apenas em memorização de sintaxe.

---

## 1. Objetivo pedagógico da sessão

Ao final da sessão, a mentorada deve conseguir:

1. diferenciar quando usar `INNER JOIN`, `LEFT JOIN` e `FULL OUTER JOIN`;
2. explicar por que a posição do filtro (`ON` ou `WHERE`) muda o resultado;
3. montar e interpretar consultas com `JOIN + filtro + agregação`;
4. justificar a escolha da query com base em pergunta de negócio.

Resultado esperado da sessão:

- segurança conceitual para leitura de bases relacionais;
- autonomia para resolver problemas iniciais de análise com SQL.

---

## 2. Contexto de negócio: por que JOIN importa

No domínio de CRM e marketing, os dados quase nunca ficam em uma única tabela.

Exemplo realista:

- tabela `clientes`: quem são os clientes;
- tabela `pedidos`: histórico de compras.

Perguntas típicas:

- quais clientes compraram no período?
- quais clientes ainda não compraram?
- qual é o valor total de compras por cliente?

Sem JOIN, essas perguntas ficam incompletas ou exigem processamento manual.

Com JOIN bem aplicado, conseguimos combinar contexto de negócio com fatos transacionais em uma única leitura analítica.

---

## 3. Fundamentos relacionais que sustentam os JOINs

## 3.1 Grão da tabela (granularidade)

Grão = o que cada linha representa.

- `clientes`: 1 linha = 1 cliente.
- `pedidos`: 1 linha = 1 pedido.

Se o grão não estiver claro, a leitura de JOIN fica confusa e surgem erros de interpretação.

## 3.2 Chave primária e chave estrangeira

- **Chave primária (PK)**: identifica unicamente uma linha.
  - Ex.: `clientes.cliente_id`.
- **Chave estrangeira (FK lógica)**: aponta para a PK de outra tabela.
  - Ex.: `pedidos.cliente_id` referencia `clientes.cliente_id`.

JOIN, na prática, é o vínculo entre essas chaves.

## 3.3 Cardinalidade

Cardinalidade descreve como uma entidade se relaciona com outra:

- `1:1` — um para um;
- `1:N` — um para muitos;
- `N:N` — muitos para muitos (geralmente exige tabela ponte).

No nosso caso:

- um cliente pode ter vários pedidos (`1:N`).

Consequência prática: um cliente pode aparecer várias vezes após o JOIN.

## 3.4 Nulos, linhas faltantes e duplicidades

Três sinais para sempre observar no resultado:

1. **Nulos (`NULL`)**: indicam ausência de correspondência (muito comum em `LEFT JOIN`).
2. **Linhas faltantes**: geralmente JOIN muito restritivo ou filtro mal posicionado.
3. **Duplicidades aparentes**: muitas vezes são esperadas pela cardinalidade (ex.: um cliente com dois pedidos).

---

## 4. JOINs com leitura conceitual e diagrama de Venn

Antes dos tipos de JOIN, definimos os conjuntos:

- **A** = conjunto de clientes (`clientes`).
- **B** = conjunto de clientes que aparecem em pedidos (`pedidos`, projetado por `cliente_id`).

Importante: diagrama de Venn ajuda na intuição de pertencimento de conjunto, mas não mostra multiplicidade de linhas.

### 4.1 `INNER JOIN` (interseção)

Retorna apenas o que existe em A e em B ao mesmo tempo.

Leitura em conjuntos:

- `INNER JOIN = A ∩ B`

Diagrama de Venn (conceitual):

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /         \          /         \
    /     A     \________/     B     \
    \           /########\           /
     \_________/##########\_________/

Área hachurada (########) = resultado do INNER JOIN
```

Quando usar:

- quando você quer apenas registros com correspondência nos dois lados.

### 4.2 `LEFT JOIN` (preserva esquerda)

Retorna tudo de A e, quando houver, dados de B.

Leitura em conjuntos:

- `LEFT JOIN = A`

Diagrama de Venn (conceitual):

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /#########\          /         \
    /###########\________/     B     \
    \###########/########\           /
     \#########/##########\_________/

Área hachurada = todo o conjunto A
```

Quando usar:

- quando cobertura da base da esquerda é requisito de negócio.

### 4.3 `FULL OUTER JOIN` (união completa)

Retorna tudo de A e tudo de B.

Leitura em conjuntos:

- `FULL OUTER JOIN = A ∪ B`

Diagrama de Venn (conceitual):

```text
Clientes (A)                    Pedidos (B)
      _________            _________
     /#########\          /#########\
    /###########\________/###########\
    \###########/########\###########/
     \#########/##########\#########/

Área hachurada = A inteiro + B inteiro
```

Quando usar:

- auditoria de cobertura;
- reconciliação entre duas bases.

Observação prática:

- em alguns engines, `FULL OUTER JOIN` pode ter limitações ou não ser suportado.

### 4.4 Comparativo rápido

| Tipo de JOIN | Regra | Melhor uso |
|---|---|---|
| `INNER JOIN` | Apenas correspondência em ambos | Análise de interseção |
| `LEFT JOIN` | Preserva esquerda | Cobertura de base principal |
| `FULL OUTER JOIN` | Preserva ambos | Reconciliação/auditoria |

---

## 5. `ON` vs `WHERE` (ponto mais importante da sessão)

Regra prática:

- `ON` controla como as tabelas se conectam.
- `WHERE` filtra o resultado depois da conexão.

Em `LEFT JOIN`, essa diferença muda o significado da consulta.

### 5.1 Caso correto para preservar todos os clientes

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
   AND p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_periodo DESC, c.cliente_id;
```

Interpretação:

- mantém todos os clientes;
- limita apenas os pedidos considerados na agregação.

### 5.2 Caso que quebra cobertura sem perceber

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
WHERE p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_periodo DESC, c.cliente_id;
```

Interpretação:

- remove clientes sem pedido no período;
- na prática, comporta-se como `INNER JOIN` para essa condição.

Mensagem-chave da sessão:

> Se a intenção é manter todos os clientes, filtros da tabela da direita devem ir no `ON` (quando aplicável ao relacionamento).

---

## 6. Setup e base de dados da prática

Ferramentas sugeridas:

- SQLBolt: https://sqlbolt.com/
- DB Fiddle (PostgreSQL): https://www.db-fiddle.com/
- W3Schools SQL Tryit (contingência): https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all

Script base (copiar e executar):

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

Leitura rápida da base:

- 4 clientes;
- 4 pedidos;
- 1 cliente sem pedido (caso didático para `LEFT JOIN`).

---

## 7. Roteiro de condução (60 minutos)

### Bloco 1 (0–10 min) — Aquecimento

- revisão rápida de `SELECT`, `WHERE`, `GROUP BY`;
- confirmação de PK/FK e grão das tabelas;
- alinhamento de objetivo da sessão.

### Bloco 2 (10–25 min) — Conceito de JOINs

- `INNER JOIN`, `LEFT JOIN`, `FULL OUTER JOIN`;
- leitura dos diagramas de Venn;
- explicação de `ON` vs `WHERE` com exemplo comparativo.

### Bloco 3 (25–45 min) — Prática guiada

Distribuição sugerida:

- 25–32 min: exercício 1 (`INNER JOIN`);
- 32–39 min: exercício 2 (`LEFT JOIN`);
- 39–45 min: exercício 3 (`JOIN + GROUP BY`).

### Bloco 4 (45–55 min) — Mini-desafio

- resolver query final com período e agregação;
- interpretar resultado (nulos, cobertura da base e ordenação).

### Bloco 5 (55–60 min) — Fechamento

- registrar 3 aprendizados;
- registrar 1 dúvida pendente;
- validar se o objetivo da sessão foi atingido.

---

## 8. Exercícios guiados com gabarito comentado

### Exercício 1 — `INNER JOIN` básico

Enunciado:

> Listar cliente, pedido e valor para quem comprou.

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

Resultado esperado:

| cliente_id | nome | pedido_id | valor |
|---:|---|---:|---:|
| 1 | Ana | 101 | 120.00 |
| 1 | Ana | 102 | 80.00 |
| 2 | Bruno | 103 | 50.00 |
| 3 | Carla | 104 | 200.00 |

Leitura didática:

- Diego não aparece porque não possui pedido.

### Exercício 2 — `LEFT JOIN` para cobertura da base

Enunciado:

> Listar todos os clientes e identificar quem não comprou.

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

Resultado esperado:

| cliente_id | nome | pedido_id |
|---:|---|---:|
| 1 | Ana | 101 |
| 1 | Ana | 102 |
| 2 | Bruno | 103 |
| 3 | Carla | 104 |
| 4 | Diego | `NULL` |

Agora, apenas clientes sem pedido:

```sql
SELECT
    c.cliente_id,
    c.nome
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
WHERE p.pedido_id IS NULL;
```

Resultado esperado:

| cliente_id | nome |
|---:|---|
| 4 | Diego |

### Exercício 3 — `JOIN + GROUP BY` (resumo analítico)

Enunciado:

> Calcular total financeiro e quantidade de pedidos por cliente.

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_total,
    COUNT(p.pedido_id) AS total_pedidos
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
GROUP BY c.cliente_id, c.nome
ORDER BY valor_total DESC, c.cliente_id;
```

Resultado esperado:

| cliente_id | nome | valor_total | total_pedidos |
|---:|---|---:|---:|
| 1 | Ana | 200.00 | 2 |
| 3 | Carla | 200.00 | 1 |
| 2 | Bruno | 50.00 | 1 |
| 4 | Diego | 0.00 | 0 |

Leitura didática:

- `COALESCE` evita total nulo para clientes sem pedido;
- `COUNT(p.pedido_id)` conta apenas linhas com pedido válido.

---

## 9. Mini-desafio final com solução e interpretação

### Enunciado

Monte uma query que traga todos os clientes com total de compras apenas no período de `2026-03-01` a `2026-03-10`, incluindo clientes sem compras no período. Ordene por maior valor total.

### Dicas antes do gabarito

1. Comece de `clientes`.
2. Use `LEFT JOIN` para preservar cobertura.
3. Posicione o filtro de período no `ON`.
4. Agregue com `SUM` e trate nulos com `COALESCE`.

### Gabarito

```sql
SELECT
    c.cliente_id,
    c.nome,
    COALESCE(SUM(p.valor), 0) AS valor_total_periodo,
    COUNT(p.pedido_id) AS qtd_pedidos_periodo
FROM clientes c
LEFT JOIN pedidos p
    ON c.cliente_id = p.cliente_id
   AND p.data_pedido BETWEEN DATE '2026-03-01' AND DATE '2026-03-10'
GROUP BY c.cliente_id, c.nome
ORDER BY valor_total_periodo DESC, c.cliente_id;
```

Resultado esperado:

| cliente_id | nome | valor_total_periodo | qtd_pedidos_periodo |
|---:|---|---:|---:|
| 1 | Ana | 200.00 | 2 |
| 2 | Bruno | 50.00 | 1 |
| 3 | Carla | 0.00 | 0 |
| 4 | Diego | 0.00 | 0 |

Interpretação:

- Carla tem pedido fora do período e, por isso, fica com 0 no recorte;
- Diego segue aparecendo por causa do `LEFT JOIN`.

---

## 10. Rubrica de validação da aprendizagem

Considere a sessão bem-sucedida quando a mentorada:

- explica a diferença entre `INNER` e `LEFT` com exemplo próprio;
- identifica por que linhas “somem” em um JOIN;
- evita o erro clássico de filtro no `WHERE` após `LEFT JOIN`;
- entrega mini-desafio com leitura correta do resultado;
- comunica a lógica da query com linguagem de negócio.

Checklist rápido:

- [ ] Entendeu PK/FK e grão das tabelas.
- [ ] Diferenciou `INNER`, `LEFT` e `FULL OUTER`.
- [ ] Demonstrou domínio de `ON` vs `WHERE`.
- [ ] Construiu query final sem ajuda total.

---

## 11. Erros comuns e como corrigir

1. **Esquecer condição de JOIN (`ON`)**
   - Sintoma: explosão de linhas (produto cartesiano).
   - Correção: validar relacionamento por chave antes de executar.

2. **Aplicar filtro da tabela da direita no `WHERE` após `LEFT JOIN`**
   - Sintoma: perda de clientes sem correspondência.
   - Correção: mover o filtro para o `ON` quando a intenção for preservar a esquerda.

3. **Somar sem agrupar corretamente**
   - Sintoma: erro SQL de coluna não agregada.
   - Correção: incluir no `GROUP BY` todas as colunas não agregadas do `SELECT`.

4. **Não tratar `NULL` em saída analítica**
   - Sintoma: métricas em branco e leitura confusa.
   - Correção: usar `COALESCE` na apresentação do resultado.

5. **Interpretar duplicidade como erro sem checar cardinalidade**
   - Sintoma: suspeita falsa de dado duplicado.
   - Correção: confirmar se o relacionamento `1:N` explica múltiplas linhas.

---

## 12. Plano de continuidade pós-sessão

Se houver necessidade de reforço:

1. repetir os exercícios com outra janela de datas;
2. adicionar uma terceira tabela simples (ex.: `campanhas`) para múltiplos JOINs;
3. montar lista curta de 10 queries progressivas (básico -> intermediário);
4. registrar dúvidas e decisões em `../../notes/`.

Próximo degrau natural da trilha:

- avançar para JOIN em mais de duas tabelas e introduzir CTE para legibilidade.

---

## 13. Glossário rápido

- **PK (Primary Key)**: chave única da tabela.
- **FK (Foreign Key)**: chave que referencia outra tabela.
- **Cardinalidade**: padrão de relacionamento entre entidades.
- **JOIN**: operação de combinação de tabelas.
- **`NULL`**: ausência de valor.
- **Agregação**: resumo de dados com funções como `SUM`, `COUNT`, `AVG`.

---

## 14. Referências

- SQLBolt: https://sqlbolt.com/
- DB Fiddle: https://www.db-fiddle.com/
- W3Schools SQL Tryit: https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_all

Materiais locais da sessão:

- `sessao-01-sql-joins.md`
- `plano-aula.md`
- `checklist-execucao-ao-vivo.md`
