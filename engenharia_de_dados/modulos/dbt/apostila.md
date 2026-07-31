---
title: "Apostila, dbt: transformacao com SQL versionado e testado"
date: 2026-07-31
type: apostila
status: draft
project: zambotto-mentoria
tags: [engenharia_de_dados, dbt]
---

# Apostila, dbt: transformação com SQL versionado e testado

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

## Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O que o dbt é, e o que ele não é](#3-o-que-o-dbt-é-e-o-que-ele-não-é)
- [4. Model, ref e o DAG](#4-model-ref-e-o-dag)
- [5. Materializações](#5-materializações)
- [6. Camadas: sources, staging e marts](#6-camadas-sources-staging-e-marts)
- [7. Seeds e snapshots](#7-seeds-e-snapshots)
- [8. Jinja e macros](#8-jinja-e-macros)
- [9. Testes: genéricos, singulares e unitários](#9-testes-genéricos-singulares-e-unitários)
- [10. Contratos, documentação e linhagem](#10-contratos-documentação-e-linhagem)
- [11. Laboratório](#11-laboratório)
- [12. Exercícios e entregáveis](#12-exercícios-e-entregáveis)
- [13. Mini-desafio com solução](#13-mini-desafio-com-solução)
- [14. Rubrica de validação da aprendizagem](#14-rubrica-de-validação-da-aprendizagem)
- [15. Erros comuns e como corrigir](#15-erros-comuns-e-como-corrigir)
- [16. Plano de continuidade](#16-plano-de-continuidade)
- [17. Glossário](#17-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

## 0. Como usar esta apostila

**Leitura linear.** Seções 1 a 10 constroem o modelo mental. A seção 11 é o
laboratório, e ela só faz sentido depois da 6. As seções 12 a 14 são o que você
entrega e como isso é avaliado na call.

**Revisão pontual.** Se você já usa dbt e veio atrás de um assunto específico,
vá direto: materialização na 5, teste na 9, contrato na 10. A seção 15 é a que
mais economiza tempo de quem já está com o projeto na mão.

**Pré-requisitos.** SQL com JOIN e agregação, no nível do módulo de SQL da
trilha. Docker rodando na sua máquina, no nível do módulo de Docker. Você não
precisa saber Python, e não precisa de conta em nuvem.

**Versões desta apostila.** Tudo foi verificado com dbt Core 1.12.0 e
dbt-duckdb 1.10.1, em 2026-07-31. Onde a versão importa para o comportamento, a
apostila diz qual.

## 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** por que o dbt existe e qual problema do ELT ele resolve, sem
   recorrer a "porque é a ferramenta padrão".
2. **Escrever** um model em SQL que o dbt materializa como view, table ou
   incremental, e justificar a escolha por custo e frequência.
3. **Conectar** models pelo `ref()` e ler o DAG resultante, entendendo por que a
   ordem de execução não é escrita por você.
4. **Organizar** um projeto em sources, staging e marts, dizendo o que entra em
   cada camada e o que nunca entra.
5. **Testar** dados com teste genérico, teste singular e unit test, sabendo qual
   dos três responde a qual pergunta.
6. **Declarar** um contrato de model e prever o que quebra quando o contrato é
   violado.
7. **Diagnosticar** as falhas mais comuns de um projeto dbt a partir da
   mensagem de erro, sem tentativa e erro.

O verbo de cada item é o que será cobrado. "Explicar" é oral, na call.
"Escrever" e "testar" são código que roda.

## 2. Contexto de negócio

A startup fictícia de marketing e e-commerce da trilha continua a mesma. Ela
veicula campanhas pagas em Google Ads, Meta Ads e TikTok Ads, e nos módulos
anteriores você já construiu a parte de baixo do pipeline: o object storage
guardando o dado bruto, o particionamento decidindo o custo da leitura, o
Airflow orquestrando a ingestão e o Kafka trazendo o evento quase em tempo real.

O que ainda não existe é a camada que responde à pergunta do negócio. Hoje o
analista abre o dado cru e escreve, de novo, o mesmo JOIN entre campanha,
veiculação e conversão. Cada um escreve um pouco diferente. Quando a diretoria
pergunta qual canal tem o melhor custo por conversão, chegam dois números.

A pergunta deste módulo é essa: **quanto custou cada conversão, por canal e por
dia, com um número só, calculado num lugar só.**

O que este módulo acrescenta ao projeto:

| Camada | Já existia | Este módulo acrescenta |
|---|---|---|
| Ingestão | Airflow, Kafka, MinIO | nada |
| Armazenamento | Parquet particionado | nada |
| Transformação | query solta de analista | models versionados, testados e documentados |
| Consumo | planilha | uma tabela fato com uma definição única |

## 3. O que o dbt é, e o que ele não é

### 3.1 O recorte do dbt no ELT

**O que é**

O dbt é a camada de transformação de um pipeline ELT. Ele não extrai dado e não
carrega dado: ele pega o que já está no banco e produz tabelas e views novas a
partir de SELECT.

A sigla ajuda a lembrar do recorte. No ETL clássico, você transforma antes de
carregar, geralmente numa máquina intermediária. No ELT, você carrega primeiro e
transforma dentro do próprio banco, usando o poder de processamento dele. O dbt
é o "T" do ELT, e só ele.

**Como funciona na prática**

Você escreve um arquivo `.sql` com um SELECT. O dbt envolve esse SELECT no DDL
apropriado e submete ao banco. Você nunca escreve `CREATE TABLE`, `DROP TABLE`
nem `CREATE SCHEMA`.

**O equívoco comum**

Muita gente descreve o dbt como "um orquestrador". Ele ordena a execução dos
próprios models, o que é diferente de orquestrar um pipeline. Ele não agenda,
não tenta de novo com backoff, não observa fonte externa e não dispara alerta
por si. Quem faz isso é o Airflow, do módulo de orquestração. Em produção os
dois convivem: o Airflow chama o dbt.

**Como inspecionar**

O comando `dbt compile` mostra o SQL que seria enviado ao banco, sem enviar.
É a forma mais direta de ver que o dbt é um gerador de SQL, não um motor de
processamento.

### 3.2 Analytics engineering, a prática por trás da ferramenta

O dbt trouxe para o trabalho analítico quatro coisas que a engenharia de
software já tinha: versionamento, teste automatizado, documentação junto do
código e integração contínua.

O ganho não é a ferramenta, é a mudança de quem responde pela definição. Antes
do dbt, "receita líquida" morava dentro de uma query no BI, de um Excel e da
cabeça de duas pessoas. Depois, mora num arquivo com histórico no Git.

### 3.3 dbt Core, dbt Cloud e o motor Fusion

| Sabor | O que é | Quando faz sentido |
|---|---|---|
| dbt Core | CLI open source, roda local ou em qualquer orquestrador | Todo projeto começa aqui, e muitos ficam |
| dbt Cloud | Plataforma gerenciada, com IDE, agendador, documentação e CI | Time sem engenheiro de plataforma disponível |
| Fusion | Motor escrito em Rust, com entendimento nativo de SQL por dialeto | Hoje é o padrão da instalação nova do dbt |

O Fusion merece atenção porque o cenário mudou rápido. A documentação oficial
descreve o Fusion como a experiência padrão ao instalar o dbt, construída sobre
o runtime Apache 2.0 do dbt Core 2.0. Ao mesmo tempo, a página de versões do
dbt Core lista o 2.0 como alpha, e o 1.12, de 2026-07-16, como a versão em
suporte ativo.

As duas coisas convivem, e a leitura honesta é: o Fusion é o caminho declarado,
e a linha 1.x é a que está em suporte ativo hoje. O laboratório deste módulo fixa
o dbt Core 1.12.0 por esse motivo. Quando você for escolher para um projeto real,
confira as duas páginas na data da decisão, porque essa fronteira anda.

Nada do que você aprende aqui muda de nome com o Fusion. Model, `ref`, teste,
materialização e contrato são o framework, não o motor.

## 4. Model, ref e o DAG

### 4.1 O model é um SELECT

**O que é**

Um model é um arquivo `.sql` dentro de `models/`, com um SELECT. O nome do
arquivo vira o nome do objeto no banco.

**Como funciona na prática**

Este é um model real do laboratório, o `stg_campanhas`:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```sql
select
    cast(campanha_id as integer)             as campanha_id,
    trim(nome)                               as nome_campanha,
    lower(trim(canal))                       as canal,
    cast(data_inicio as date)                as data_inicio,
    cast(orcamento_diario as decimal(10, 2)) as orcamento_diario
from {{ source('bruto', 'campanhas') }}
```

O passo a passo do que acontece quando você roda `dbt run`:

1. O dbt lê todos os arquivos do projeto e monta o manifesto, que é o mapa de
   tudo que existe e de quem depende de quem.
2. Ele resolve o `{{ source(...) }}` para o nome real da tabela ou do arquivo.
3. Ele envolve o SELECT no DDL da materialização escolhida.
4. Ele submete o SQL ao banco e registra o resultado.

**O equívoco comum**

Que o nome do model precisa ser declarado em algum lugar. Não precisa. O nome do
arquivo é o nome do model, e é ele que o `ref()` procura. Renomear o arquivo
renomeia o objeto e quebra todo `ref()` que apontava para o nome antigo.

**Como inspecionar**

O SQL final fica em `target/compiled/`. Abrir esse arquivo é o hábito que mais
acelera o aprendizado no começo, porque ele elimina a dúvida sobre o que o Jinja
virou.

### 4.2 ref, a função que constrói o grafo

**O que é**

`ref('nome_do_model')` é como um model aponta para outro. Ela devolve o nome
qualificado do objeto no banco e, ao mesmo tempo, declara uma dependência.

**Como funciona na prática**

```sql
select * from {{ ref('stg_eventos_campanha') }}
```

O dbt lê isso e conclui duas coisas: onde buscar o dado e que este model precisa
rodar depois do `stg_eventos_campanha`. É a mesma linha respondendo às duas
perguntas, e é por isso que o grafo nunca desatualiza em relação ao código.

**O equívoco comum**

Escrever o nome da tabela direto, porque "funciona igual". Funciona na primeira
execução e falha na segunda. Sem o `ref()`, o dbt não sabe da dependência, roda
os dois models na ordem errada e você recebe um erro de tabela inexistente que
não tem relação aparente com o que você escreveu.

O mesmo vale para o `source()`: ele marca a fronteira entre o que o dbt produz e
o que ele apenas consome.

**Como inspecionar**

`dbt list --select stg_campanhas+` lista o model e tudo que depende dele. O `+`
à direita significa descendentes, e à esquerda, ancestrais.

### 4.3 O DAG não é escrito, é derivado

**O que é**

O grafo acíclico dirigido do projeto é o conjunto de todas as dependências
declaradas por `ref()` e `source()`. Ninguém escreve a ordem de execução.

**O equívoco comum**

Achar que existe um arquivo de ordenação para editar quando a execução sai
errada. Não existe, e isso é a característica central. Se a ordem está errada,
a dependência está errada, e o conserto é no `ref()`.

**Como inspecionar**

No laboratório, o `dbt build` imprime a ordem que ele escolheu, numerada. Foi
assim que o Lab 2 mostrou os models de staging rodando antes do mart, sem que
nada no projeto declare isso.

## 5. Materializações

### 5.1 As cinco materializações

**O que é**

A materialização decide como o resultado do SELECT é persistido. A
documentação oficial lista cinco embutidas: `table`, `view`, `incremental`,
`ephemeral` e `materialized view`. O padrão, quando você não declara nada, é
`view`.

| Materialização | O que o dbt faz | Custo de armazenamento | Custo de leitura |
|---|---|---|---|
| `view` | Cria uma view, recriada a cada execução | nenhum | paga a transformação a cada consulta |
| `table` | Recria a tabela inteira a cada execução | tamanho do resultado | baixo |
| `incremental` | Processa só o que chegou desde a última vez | tamanho do resultado | baixo |
| `ephemeral` | Não cria objeto, injeta o SQL como CTE | nenhum | herdado de quem a consome |
| `materialized view` | Delega ao banco a atualização da view | depende do banco | baixo |

**Como funciona na prática**

Você declara no bloco `config` do próprio model, ou por pasta no
`dbt_project.yml`. O laboratório usa a segunda forma, porque a decisão é da
camada, não do arquivo:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
models:
  campanhas:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

**O equívoco comum**

Marcar tudo como `table` porque "table é mais rápido". Rápido para ler, caro
para construir. Uma camada de staging que só renomeia e converte tipo raramente
justifica o custo de reescrever a tabela inteira a cada execução.

A regra prática que funciona: staging em `view`, mart em `table`, e `incremental`
apenas quando a tabela cheia começa a doer no tempo ou na fatura.

### 5.2 Incremental, o que muda de verdade

**O que é**

Um model incremental transforma todas as linhas na primeira execução e, nas
seguintes, apenas as que você filtrar. O filtro é seu, não do dbt.

**Como funciona na prática**

Este é o `fct_custo_diario` do laboratório:

<!-- verificacao: nivel 3, docker compose run --rm dbt run --select fct_custo_diario, dbt-core 1.12.0, 2026-07-31 -->

```sql
{{ config(materialized="incremental", unique_key=["campanha_id", "data_evento"]) }}

select
    campanha_id,
    data_evento,
    sum(custo) as custo
from {{ ref('stg_eventos_campanha') }}

{% if is_incremental() %}
    where data_evento > (
        select coalesce(max(data_evento), date '1900-01-01') from {{ this }}
    )
{% endif %}

group by campanha_id, data_evento
```

A macro `is_incremental()` devolve verdadeiro quando três condições valem ao
mesmo tempo, segundo a documentação oficial: o model já existe como tabela no
banco, a execução não passou `--full-refresh`, e o model está configurado como
`incremental`.

No Lab 4 você vê isso acontecer. Na primeira execução o bloco `{% if %}`
desaparece do SQL compilado. Na segunda, ele aparece:

<!-- verificacao: nivel 3, saida real de target/compiled na 2a execucao, 2026-07-31 -->

```sql
    where data_evento > (
        select coalesce(max(data_evento), date '1900-01-01')
        from "campanhas"."main"."fct_custo_diario"
    )
```

**O equívoco comum**

Achar que o `unique_key` faz o filtro. Ele não faz. O `unique_key` decide o que
acontece com uma linha que já existe, atualizar em vez de duplicar. Quem decide
o que sequer é lido é o `where` dentro do `is_incremental()`. Sem ele, o
incremental lê tudo e só economiza escrita.

**Como inspecionar**

Rode o model duas vezes e compare `target/compiled/` entre as execuções. É a
prova, não a explicação.

## 6. Camadas: sources, staging e marts

### 6.1 A fronteira do source

**O que é**

Um `source` declara uma tabela que o dbt lê mas não produz. É a fronteira do
projeto.

**Como funciona na prática**

No laboratório, os arquivos brutos são CSV lidos diretamente pelo adapter:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-duckdb 1.10.1, 2026-07-31 -->

```yaml
sources:
  - name: bruto
    meta:
      external_location: "dados_brutos/{name}.csv"
    tables:
      - name: campanhas
      - name: eventos_campanha
      - name: conversoes
```

A chave `external_location` é específica do dbt-duckdb, e existe para que o
adapter leia o arquivo no lugar de uma tabela do catálogo. Num data warehouse de
nuvem você não usaria isso: as tabelas cruas já estariam carregadas, e o source
apenas declararia schema e nome.

**O equívoco comum**

Usar `source()` para uma tabela que o próprio dbt cria. Isso desliga a
dependência, e o resultado é o mesmo erro de ordem de execução da seção 4.2. A
regra é curta: se o dbt cria, é `ref`. Se alguém entrega, é `source`.

### 6.2 Staging, uma fonte por model

**O que é**

A camada de staging tem um model por tabela de origem. Ela faz apenas o que é
mecânico: renomear coluna, converter tipo, normalizar texto.

**O equívoco comum**

Colocar regra de negócio no staging. O sintoma aparece meses depois, quando dois
marts precisam da mesma origem com regras diferentes e alguém decide duplicar o
staging. A partir daí existem duas verdades.

O teste mental: se a resposta a "por que essa linha está aqui" envolve uma
decisão de negócio, a linha não é de staging.

### 6.3 Marts, o modelo que o negócio consome

**O que é**

O mart é o modelo final por domínio. É onde vive a regra de negócio, a junção
entre fontes e o cálculo que a diretoria vai citar em reunião.

**Como funciona na prática**

O `fct_desempenho_campanha` junta veiculação, cadastro, conversão e o de para de
canal, e produz o número que o módulo prometeu na seção 2. Rodado no Lab 3, ele
responde:

<!-- verificacao: nivel 3, docker compose run --rm dbt show, saida real, 2026-07-31 -->

```
| grupo_de_canal |   custo | conversoes | custo_por_conversao |
| -------------- | ------- | ---------- | ------------------- |
| Social         | 4,747.9 |          7 |              678.27 |
| Search         | 4,126.8 |          5 |              825.36 |
```

O dado é fictício, e o formato da resposta não é. É esse recorte que encerra a
discussão de qual canal está mais caro.

**O equívoco comum**

Uma camada intermediária que ninguém consegue explicar. Modelos `int_` existem
para reaproveitar junção usada por mais de um mart. Quando existe um `int_` com
um consumidor só, ele geralmente é um mart mal nomeado.

## 7. Seeds e snapshots

### 7.1 Seed, o CSV que é código

**O que é**

Um seed é um arquivo CSV dentro de `seeds/`, carregado como tabela pelo comando
`dbt seed`. Ele serve para dado pequeno, estável e versionado.

**Como funciona na prática**

O laboratório usa um de para de canal:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, 2026-07-31 -->

```csv
canal,grupo_de_canal,e_pago
google_ads,Search,true
meta_ads,Social,true
tiktok_ads,Social,true
```

**O equívoco comum**

Usar seed para carregar dado de produção. Seed vive no Git, e Git não é lugar de
volume nem de dado pessoal. O critério é: cabe numa revisão de pull request e
muda por decisão humana? Então é seed.

### 7.2 Snapshot, o histórico que a origem não guarda

**O que é**

Um snapshot registra como uma linha era em cada momento. É a resposta ao problema
de origem que sobrescreve o próprio dado, e implementa o padrão conhecido como
dimensão de mudança lenta, ou SCD tipo 2.

**Como funciona na prática**

A partir do dbt Core 1.9 o snapshot é declarado em YAML:

<!-- verificacao: nivel 3, docker compose run --rm dbt snapshot, dbt-core 1.12.0, 2026-07-31 -->

```yaml
snapshots:
  - name: snap_campanhas
    relation: ref('stg_campanhas')
    config:
      unique_key: campanha_id
      strategy: check
      check_cols: ["orcamento_diario"]
```

Existem duas estratégias. A `timestamp` usa uma coluna de data de alteração da
própria origem, e é a preferida quando ela existe. A `check` compara os valores
das colunas listadas a cada execução, e é o que sobra quando a origem não traz
data confiável.

O dbt acrescenta colunas de controle, entre elas `dbt_scd_id`, `dbt_valid_from`,
`dbt_valid_to` e `dbt_updated_at`. No Lab 5 você altera o orçamento de uma
campanha e vê o resultado:

<!-- verificacao: nivel 3, docker compose run --rm dbt show, saida real, 2026-07-31 -->

```
| campanha_id | orcamento_diario |       dbt_valid_from |         dbt_valid_to |
| ----------- | ---------------- | -------------------- | -------------------- |
|           3 |              450 | 2026-07-31 16:22:... | 2026-07-31 16:23:... |
|           3 |              500 | 2026-07-31 16:23:... |                      |
```

A linha antiga não foi apagada. Ela foi fechada, e a nova nasceu aberta. Quem
consome a tabela hoje filtra `dbt_valid_to is null`; quem precisa saber qual era
o orçamento em junho consulta pela data.

**O equívoco comum**

Rodar o snapshot uma vez por semana e esperar histórico diário. O snapshot só
enxerga o que existe no instante em que roda. Mudança que aconteceu e voltou
atrás entre duas execuções é invisível, para sempre. A frequência do snapshot é
a resolução do seu histórico.

## 8. Jinja e macros

### 8.1 Jinja é a parte que roda antes do SQL

**O que é**

Jinja é a linguagem de template que o dbt usa. Ela é processada antes de o SQL
chegar ao banco, e produz texto.

Duas sintaxes bastam para começar: `{{ ... }}` insere um valor no texto, e
`{% ... %}` executa lógica sem inserir nada.

**O equívoco comum**

Tratar Jinja como se fosse parte do SQL. O banco nunca vê Jinja. Isso explica
por que um validador de SQL puro rejeita um model do dbt: para ele, `{{` não é
sintaxe válida. Também explica por que erro de Jinja aparece na compilação, e
erro de SQL aparece na execução.

### 8.2 Macro, a função que você escreve

**O que é**

Uma macro é um bloco reutilizável de Jinja e SQL, declarado em `macros/`.

**Como funciona na prática**

O laboratório tem uma macro pequena e útil, que evita divisão por zero:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```jinja
{% macro razao_segura(numerador, denominador) %}
    {{ numerador }} / nullif({{ denominador }}, 0)
{% endmacro %}
```

E o mart a chama:

<!-- verificacao: nivel 3, docker compose run --rm dbt build, 2026-07-31 -->

```sql
cast(
    {{ razao_segura('eventos.custo', 'conversoes_por_dia.conversoes') }}
    as decimal(12, 2)
) as custo_por_conversao
```

Os argumentos vão entre aspas porque a macro recebe o **texto** do nome da
coluna, não o valor dela.

**O equívoco comum**

Criar macro cedo demais. Duas ocorrências de um trecho ainda são duas
ocorrências. Na terceira, o padrão está claro e a macro nasce com o nome certo.
Macro criada na primeira ocorrência costuma abstrair a coisa errada.

**Como inspecionar**

O `target/compiled/` mostra a macro já expandida. Se a expansão surpreende, o
problema é a macro, não o model.

## 9. Testes: genéricos, singulares e unitários

### 9.1 Os três tipos, e a pergunta de cada um

| Tipo | Pergunta que responde | Roda quando |
|---|---|---|
| Genérico | Este dado obedece a uma regra conhecida? | depois de o model existir |
| Singular | Esta condição específica do meu negócio se sustenta? | depois de o model existir |
| Unitário | Minha lógica está certa para uma entrada que eu escolhi? | antes de o model ser materializado |

A diferença entre os dois primeiros e o terceiro é a que mais confunde. Teste
genérico e singular olham o dado que existe. Unit test olha a lógica, com dado
que você inventou de propósito.

### 9.2 Testes genéricos

**O que é**

O dbt traz quatro testes genéricos embutidos: `unique`, `not_null`,
`accepted_values` e `relationships`.

**Como funciona na prática**

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
models:
  - name: stg_campanhas
    columns:
      - name: campanha_id
        data_tests:
          - unique
          - not_null
      - name: canal
        data_tests:
          - accepted_values:
              arguments:
                values: ["google_ads", "meta_ads", "tiktok_ads"]
```

Duas mudanças de sintaxe importam aqui, e as duas já pegaram gente de surpresa:

1. A chave é `data_tests`, não `tests`. O nome antigo ainda aparece em muito
   material na internet.
2. Os argumentos do teste vivem dentro de `arguments`, disponível a partir da
   versão 1.10.5. Versões anteriores esperavam o argumento no nível de cima.

**O equívoco comum**

Achar que teste genérico é enfeite de projeto maduro. O Lab 6 mostra o
contrário: uma linha com canal desconhecido no CSV bruto derruba o build antes
que o número errado chegue ao mart.

**Como inspecionar**

Quando um teste falha, o dbt informa o caminho do SQL compilado. Abrir esse
arquivo e rodar a query mostra exatamente quais linhas quebraram a regra.

### 9.3 Testes singulares

**O que é**

Um teste singular é um arquivo `.sql` em `tests/` com uma query que precisa
devolver zero linhas. Cada linha devolvida é uma violação.

<!-- verificacao: nivel 3, docker compose run --rm dbt build, 2026-07-31 -->

```sql
select
    campanha_id,
    data_evento,
    custo
from {{ ref('fct_desempenho_campanha') }}
where custo < 0
```

A inversão de lógica é a fonte de erro mais comum aqui. Você escreve a query que
encontra o **problema**, não a que confirma que está tudo bem.

### 9.4 Unit tests

**O que é**

Unit tests chegaram no dbt Core 1.8. Eles validam a lógica do model com entradas
fixas, antes de materializar qualquer coisa.

**Como funciona na prática**

Este unit test do laboratório protege uma decisão de negócio real: dia sem
conversão precisa ter custo por conversão nulo, e não zero.

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
unit_tests:
  - name: test_dia_sem_conversao_nao_vira_zero
    model: fct_desempenho_campanha
    given:
      - input: ref('stg_eventos_campanha')
        rows:
          - {evento_id: 1, campanha_id: 1, data_evento: "2026-06-01", impressoes: 100, cliques: 10, custo: 50.00}
      - input: ref('stg_conversoes')
        rows: []
    expect:
      rows:
        - {campanha_id: 1, data_evento: "2026-06-01", conversoes: 0, custo_por_conversao: null}
```

Zero diria que a conversão saiu de graça, que é o contrário do que aconteceu.
Nenhum dado real do laboratório expõe essa diferença hoje, e é exatamente por
isso que ela precisa de um teste com dado inventado.

**O equívoco comum**

Escrever unit test para o que o banco já garante. Testar que `sum()` soma gasta
tempo e não protege nada. Unit test vale para lógica sua: janela, regex, cálculo
condicional, tratamento de nulo.

Uma restrição prática: todo `ref()` e `source()` que o model usa precisa
aparecer em `given`. Não dá para fornecer metade das entradas.

## 10. Contratos, documentação e linhagem

### 10.1 Contrato de model

**O que é**

Um contrato declara a forma que a saída do model precisa ter: nome e tipo de
cada coluna, e restrições opcionais. Com `enforced: true`, o model falha ao
construir quando a saída não bate.

**Como funciona na prática**

<!-- verificacao: nivel 3, docker compose run --rm dbt build, dbt-core 1.12.0, 2026-07-31 -->

```yaml
models:
  - name: fct_desempenho_campanha
    config:
      contract:
        enforced: true
    columns:
      - name: campanha_id
        data_type: integer
        constraints:
          - type: not_null
      - name: custo
        data_type: decimal(12,2)
```

O contrato faz duas coisas: uma checagem prévia comparando as colunas do SELECT
com as declaradas, e a inclusão de tipos e restrições no DDL enviado ao banco.

A segunda parte é visível. Depois do Lab 2, o DuckDB mostra a coluna como não
anulável de verdade:

<!-- verificacao: nivel 3, describe main.fct_desempenho_campanha, saida real, 2026-07-31 -->

```
│     column_name     │  column_type  │  null   │
├─────────────────────┼───────────────┼─────────┤
│ campanha_id         │ INTEGER       │ NO      │
│ custo               │ DECIMAL(12,2) │ YES     │
```

A restrição não ficou só no YAML. Ela virou DDL.

**O equívoco comum**

Confundir contrato com teste. Teste roda depois e reprova o dado. Contrato roda
junto da construção e reprova a **estrutura**. Uma coluna renomeada por engano
passa em todos os testes de valor e é barrada pelo contrato.

Vale saber o limite: contrato funciona em `table`, `view` com restrições
limitadas, e `incremental`. Não funciona em `ephemeral` nem em `materialized
view`.

### 10.2 Documentação e linhagem

O `dbt docs generate` produz um site navegável com a descrição de cada model e
coluna, mais o DAG clicável. A descrição vem do mesmo YAML onde vivem os testes,
que é o ponto: documentação que mora longe do código envelhece sem que ninguém
perceba.

Este módulo não gera a documentação no laboratório. O comando existe e está na
referência oficial citada no fim da apostila, e o exercício 4 pede que você o
rode.

## 11. Laboratório

O laboratório roda inteiro em Docker, com dbt Core 1.12.0, dbt-duckdb 1.10.1 e
DuckDB 1.5.5. Nada sai da sua máquina, e não há credencial de nuvem envolvida.

Os runbooks em `infrastructure/runbooks/` trazem o passo a passo completo. O
resumo abaixo diz o que cada laboratório prova.

### Lab 0: Construir a imagem

Pré-condição: Docker Engine 28 ou superior e Docker Compose v2.

```bash
cd engenharia_de_dados/modulos/dbt/infrastructure
export DBT_UID=$(id -u)
export DBT_GID=$(id -g)
docker compose build
```

Saída esperada: ` mentoria-dbt:1.12.0  Built`.

As duas variáveis existem por um motivo prático: sem elas o container escreve
`target/` e `logs/` como root no seu disco, e você precisa de `sudo` para
limpar depois.

### Lab 1: Conferir a conexão

```bash
docker compose run --rm dbt debug
```

Saída esperada: `Connection test: [OK connection ok]` e `All checks passed!`.

O `dbt debug` confere projeto, perfil, dependências e conexão. Quando ele
reclama, o problema está antes do seu SQL.

### Lab 2: Rodar o projeto inteiro

```bash
docker compose run --rm dbt build
```

Saída esperada: `Done. PASS=22 WARN=0 ERROR=0 SKIP=0 NO-OP=0 REUSED=0 TOTAL=22`.

Os 22 nós são 1 seed, 3 models de staging, 1 mart em `table`, 1 model
incremental, 1 snapshot, 14 data tests e 1 unit test. O `dbt build` executa
model, teste, snapshot e seed na ordem do DAG.

Repare na ordem impressa: o unit test roda **antes** do model que ele testa, e
os testes de staging rodam antes de o mart existir. Ninguém escreveu essa ordem.

### Lab 3: Ler o resultado

```bash
docker compose run --rm dbt show --inline "select grupo_de_canal, sum(custo) as custo, sum(conversoes) as conversoes, round(sum(custo) / nullif(sum(conversoes), 0), 2) as custo_por_conversao from {{ ref('fct_desempenho_campanha') }} group by grupo_de_canal order by custo_por_conversao"
```

Saída esperada: `Social` com custo por conversão 678.27 e `Search` com 825.36.

Esta é a pergunta da seção 2 respondida com um número só.

### Lab 4: Ver o incremental funcionar

Pré-condição: Lab 2 concluído.

```bash
docker compose run --rm dbt run --select fct_custo_diario
sed -n '1,20p' projeto_dbt/target/compiled/campanhas/models/marts/fct_custo_diario.sql
```

Saída esperada: o SQL compilado da segunda execução traz a cláusula `where
data_evento > (...)`, que não existia na primeira.

### Lab 5: Ver o snapshot registrar uma mudança

Pré-condição: Lab 2 concluído.

```bash
sed -i 's/^3,Remarketing Carrinho,meta_ads,2026-06-03,450.00$/3,Remarketing Carrinho,meta_ads,2026-06-03,500.00/' projeto_dbt/dados_brutos/campanhas.csv
docker compose run --rm dbt snapshot
docker compose run --rm dbt show --inline "select campanha_id, orcamento_diario, dbt_valid_from, dbt_valid_to from {{ ref('snap_campanhas') }} where campanha_id = 3 order by dbt_valid_from"
sed -i 's/^3,Remarketing Carrinho,meta_ads,2026-06-03,500.00$/3,Remarketing Carrinho,meta_ads,2026-06-03,450.00/' projeto_dbt/dados_brutos/campanhas.csv
```

Saída esperada: duas linhas para a campanha 3, a de 450 com `dbt_valid_to`
preenchido e a de 500 com `dbt_valid_to` vazio.

O último comando devolve o CSV ao estado original.

### Lab 6: Quebrar um teste de propósito

```bash
printf '6,Teste Linkedin,linkedin_ads,2026-06-07,200.00\n' >> projeto_dbt/dados_brutos/campanhas.csv
docker compose run --rm dbt build --select stg_campanhas
sed -i '$d' projeto_dbt/dados_brutos/campanhas.csv
```

Saída esperada:

```
[ERROR]: in test accepted_values_stg_campanhas_canal__google_ads__meta_ads__tiktok_ads
  Got 1 result, configured to fail if != 0
Done. PASS=6 WARN=0 ERROR=1 SKIP=0 NO-OP=0 REUSED=0 TOTAL=7
```

Este é o laboratório mais importante da lista. Ver o pipeline parar por causa de
um dado ruim é o que transforma teste de dados de burocracia em rede de
proteção.

### Lab 7: Derrubar o ambiente

```bash
docker compose run --rm dbt clean
docker compose down --rmi local
```

A ordem importa. O `clean` precisa da imagem ainda de pé.

## 12. Exercícios e entregáveis

**Exercício 1: Escolha de materialização**

Objetivo: justificar materialização por custo e frequência, não por hábito.

Contexto: os quatro models do laboratório, mais dois hipotéticos, uma tabela de
eventos com 400 milhões de linhas atualizada de hora em hora, e um relatório
executivo consultado três vezes por mês.

Entregável: tabela com uma linha por model, contendo materialização escolhida,
justificativa em uma frase e o que aconteceria com a escolha oposta.

**Exercício 2: Um teste que pega um erro real**

Objetivo: escrever teste a partir de uma falha plausível, não de uma lista.

Contexto: o `fct_desempenho_campanha` do laboratório.

Entregável: um teste genérico novo e um teste singular novo, os dois no projeto,
mais a demonstração de cada um falhando. Para demonstrar a falha, altere o CSV
bruto, rode, capture a saída e desfaça a alteração, como no Lab 6.

**Exercício 3: Camada intermediária**

Objetivo: reconhecer quando um `int_` se justifica.

Contexto: suponha um segundo mart, `fct_funil_por_canal`, que precisa da mesma
junção entre eventos, campanhas e de para de canal.

Entregável: proposta de refatoração indicando o que vira `int_`, o que fica no
mart, e o critério que você usou. Se a sua conclusão for que não vale a pena
criar o `int_`, defenda isso, que também é resposta.

**Exercício 4: Documentação e linhagem**

Objetivo: usar o material de documentação que o projeto já produz.

Contexto: o projeto do laboratório, depois do Lab 2.

Entregável: as descrições de coluna do `fct_desempenho_campanha` preenchidas no
YAML, mais a saída do comando de geração de documentação e uma observação sobre
o que o DAG mostrou que você não esperava.

## 13. Mini-desafio com solução

**Enunciado**

O time de marketing pede uma tabela nova: receita por grupo de canal e semana,
com a variação percentual em relação à semana anterior. A tabela vai para um
painel executivo consultado algumas vezes por mês.

Requisitos:

1. Um model novo, com materialização justificada.
2. Reaproveitar o que já existe, sem reescrever junção.
3. Pelo menos um teste que proteja a conta.
4. Tratar o caso da primeira semana, que não tem semana anterior.

**Dicas**

- A junção entre eventos, campanhas e canal já existe em algum lugar do projeto.
- Variação percentual é uma divisão, e o projeto já tem uma macro para divisão
  que pode dar zero no denominador.
- A primeira semana é o mesmo problema do dia sem conversão da seção 9.4.

**Gabarito comentado**

Materialização `table`. O consumo é raro, então o custo de leitura importa pouco;
o volume é pequeno, então `incremental` só acrescenta complexidade. `view`
também funcionaria, e a diferença é irrelevante nessa escala. O que não se
justifica é `incremental`, e a razão é que a complexidade tem um custo de
manutenção que o ganho não paga.

Reaproveitamento: o model parte de `ref('fct_desempenho_campanha')`, que já
resolveu a junção. Partir do staging de novo criaria a segunda definição de
receita, que é o problema que o módulo inteiro existe para evitar.

Esqueleto da lógica:

```sql
with semanal as (
    select
        grupo_de_canal,
        date_trunc('week', data_evento) as semana,
        sum(receita) as receita
    from {{ ref('fct_desempenho_campanha') }}
    group by grupo_de_canal, date_trunc('week', data_evento)
)

select
    grupo_de_canal,
    semana,
    receita,
    lag(receita) over (partition by grupo_de_canal order by semana) as receita_anterior,
    {{ razao_segura(
        'receita - lag(receita) over (partition by grupo_de_canal order by semana)',
        'lag(receita) over (partition by grupo_de_canal order by semana)'
    ) }} as variacao
from semanal
```

<!-- verificacao: nivel 1, esqueleto didatico conferido contra a doc de macros e de window function, nao executado no laboratorio, 2026-07-31 -->

Este bloco é esqueleto de resposta, não código do laboratório. Ele foi conferido
contra a documentação de macro do dbt, e não foi executado. Rodá-lo é parte do
desafio.

Primeira semana: o `lag` devolve nulo, o `nullif` dentro da macro impede o erro
de divisão, e o resultado é nulo. Nulo é a resposta certa aqui, porque não houve
variação a medir. Preencher com zero afirmaria estabilidade que não existiu.

Teste que protege a conta: um teste singular que devolve as linhas onde
`variacao` é nula e `receita_anterior` não é. Se isso acontecer, a macro está
errada, não o dado.

**Interpretação**

O que separa a boa resposta da resposta correta é o item 2. Quem parte do mart
existente entendeu que o valor do dbt está na definição única. Quem reescreve a
junção produziu SQL que funciona e um problema de governança.

## 14. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Papel do dbt | Descreve como orquestrador ou como banco | Situa como camada de transformação do ELT | Explica a fronteira com o Airflow e por que os dois convivem |
| ref e DAG | Escreve nome de tabela direto | Usa `ref` e `source` corretamente | Diagnostica erro de ordem de execução a partir da mensagem |
| Materialização | Usa `table` em tudo | Escolhe por custo e frequência, e justifica | Sabe quando `incremental` não compensa e defende a escolha |
| Camadas | Mistura regra de negócio no staging | Separa staging de mart com critério | Argumenta quando um `int_` se justifica e quando não |
| Testes | Só usa `not_null` e `unique` | Usa os três tipos na situação certa | Escreve teste a partir de uma falha real observada |
| Contrato | Confunde com teste de dado | Declara contrato e prevê o que ele barra | Explica o limite por materialização |
| Diagnóstico | Tenta e erra até funcionar | Lê a mensagem e vai ao ponto | Usa `target/compiled/` como primeiro passo |

A avaliação é feita na call, sobre o código que você entregou nos exercícios.

## 15. Erros comuns e como corrigir

**O seed não encontra o próprio CSV**

Sintoma: `IO Error: No files found that match the pattern`, com um caminho
absoluto que não existe dentro do container.

Causa: o `target/` foi escrito por uma execução fora do Docker. O manifesto
guardou o caminho da máquina de fora, e o parse parcial reaproveitou.

Correção: `dbt clean` e rodar de novo. Esse erro apareceu de verdade na
construção deste laboratório, na primeira vez em que o projeto rodou no host e
depois no container.

**Model roda antes da dependência**

Sintoma: erro de tabela ou view inexistente, num model que estava funcionando.

Causa: nome de tabela escrito direto em vez de `ref()`. Sem o `ref()` não existe
aresta no grafo, e sem aresta não existe ordem.

Correção: trocar por `ref()`. Confirmar com `dbt list --select <model>+`.

**O incremental não economiza nada**

Sintoma: o tempo de execução não cai depois da primeira vez.

Causa: falta o bloco `{% if is_incremental() %}` com o filtro. O `unique_key`
sozinho evita duplicata, não evita leitura.

Correção: acrescentar o filtro e comparar `target/compiled/` entre duas
execuções.

**O teste passa e o número está errado**

Sintoma: todos os testes verdes, e o negócio aponta um valor que não fecha.

Causa: os testes existentes cobrem forma, não regra. `not_null` e `unique` não
sabem o que é uma conversão.

Correção: escrever teste singular a partir da regra de negócio, e unit test para
a lógica que o dado atual não exercita, como o caso do dia sem conversão.

**`tests:` não funciona como o tutorial mostra**

Sintoma: o teste declarado no YAML é ignorado, ou o parse reclama.

Causa: material antigo. A chave é `data_tests`, e o argumento do teste vive
dentro de `arguments` a partir da versão 1.10.5.

Correção: conferir a sintaxe na documentação da sua versão, e a versão com
`dbt --version`.

**Arquivos root no seu diretório**

Sintoma: `target/` e `logs/` que você não consegue apagar sem `sudo`.

Causa: container rodando como root sobre um volume montado.

Correção: exportar `DBT_UID` e `DBT_GID` antes do `docker compose`, como no
Lab 0.

**O `dbt debug` reclama de git**

Sintoma: `Could not find command, ensure it is in the user's PATH: "git"`.

Causa: imagem base enxuta sem git. O dbt usa git para baixar pacote.

Correção: instalar git na imagem. O `Dockerfile` do laboratório já faz isso, e
esse erro foi a razão.

## 16. Plano de continuidade

**Antes da próxima call**

Termine os exercícios 1 e 2. Eles são a base da conversa.

**O que estudar em seguida, dentro da trilha**

O próximo bloco é Nuvem e escala. O módulo de cloud para dados mostra onde esse
projeto dbt rodaria de verdade, com o data warehouse no lugar do DuckDB. O de
infraestrutura como código trata de como esse ambiente nasce sem ninguém clicar
em console.

O módulo de orquestração com Airflow, que você já viu, ganha um recorte novo
depois deste: em produção o `dbt build` é uma tarefa chamada pelo agendador, e a
integração entre os dois DAGs é um assunto por si.

**O que aprofundar por conta**

Pacotes do ecossistema, a começar por `dbt_utils`, que resolve problema comum
com macro pronta. Depois, integração contínua: rodar apenas o que mudou num pull
request é o ganho que mais aparece quando o projeto passa de algumas dezenas de
models.

**O que não perseguir agora**

Semantic layer e exposures são úteis e não mudam nada até o projeto ter
consumidor de verdade. Deixe para quando existir painel apontando para o mart.

## 17. Glossário

| Termo | Significado |
|---|---|
| Adapter | Biblioteca que traduz o SQL do dbt para um banco específico |
| Contrato | Declaração da forma da saída de um model, verificada na construção |
| DAG | Grafo de dependências entre models, derivado dos `ref` e `source` |
| Data test | Teste que avalia o dado depois de o model existir |
| Ephemeral | Materialização que não cria objeto, injetada como CTE |
| Incremental | Materialização que processa apenas o recorte filtrado por você |
| Jinja | Linguagem de template processada antes de o SQL chegar ao banco |
| Macro | Bloco reutilizável de Jinja e SQL, declarado em `macros/` |
| Manifesto | Arquivo em `target/` com o mapa completo do projeto |
| Mart | Camada final, por domínio de negócio |
| Materialização | Estratégia de persistência do resultado de um model |
| Model | Arquivo `.sql` com um SELECT que o dbt transforma em objeto no banco |
| ref | Função que aponta para outro model e cria a dependência |
| SCD tipo 2 | Padrão que guarda cada versão de uma linha ao longo do tempo |
| Seed | CSV versionado, carregado como tabela por `dbt seed` |
| Snapshot | Captura periódica que registra mudança de linha ao longo do tempo |
| source | Função e declaração de tabela que o dbt lê mas não produz |
| Staging | Camada de limpeza mecânica, um model por origem |
| Unit test | Teste da lógica do model com entradas fixas, antes de materializar |

## Referências

Documentação oficial do dbt, consultada em 2026-07-31:

- Materializações: https://docs.getdbt.com/docs/build/materializations
- Models incrementais: https://docs.getdbt.com/docs/build/incremental-models
- Snapshots: https://docs.getdbt.com/docs/build/snapshots
- Jinja e macros: https://docs.getdbt.com/docs/build/jinja-macros
- Data tests: https://docs.getdbt.com/reference/resource-properties/data-tests
- Unit tests: https://docs.getdbt.com/docs/build/unit-tests
- Contratos de model: https://docs.getdbt.com/docs/collaborate/govern/model-contracts
- Comandos: https://docs.getdbt.com/reference/dbt-commands
- Comando build: https://docs.getdbt.com/reference/commands/build
- Versões do dbt Core: https://docs.getdbt.com/docs/dbt-versions/core
- Motor Fusion: https://docs.getdbt.com/docs/fusion/about-fusion
- Adapter dbt-duckdb: https://github.com/duckdb/dbt-duckdb

## Fontes verificadas (2026-07-31)

- O dbt tem cinco materializações embutidas, `table`, `view`, `incremental`,
  `ephemeral` e `materialized view`, e o padrão é `view`.
  https://docs.getdbt.com/docs/build/materializations
- `is_incremental()` é verdadeiro quando o model já existe como tabela, a
  execução não passou `--full-refresh` e o model é `incremental`.
  https://docs.getdbt.com/docs/build/incremental-models
- O snapshot é declarado em YAML com `relation`, `unique_key`, `strategy` e
  `check_cols`, e o dbt acrescenta `dbt_scd_id`, `dbt_valid_from`,
  `dbt_valid_to` e `dbt_updated_at`. https://docs.getdbt.com/docs/build/snapshots
- Os quatro testes genéricos embutidos são `unique`, `not_null`,
  `accepted_values` e `relationships`, declarados sob `data_tests`.
  https://docs.getdbt.com/reference/resource-properties/data-tests
- A chave `arguments` para argumento de teste genérico está disponível a partir
  da versão 1.10.5, e versões anteriores usam o argumento no nível de cima.
  https://docs.getdbt.com/reference/resource-properties/data-tests
- Unit tests foram introduzidos no dbt Core 1.8, exigem todos os `ref` e
  `source` do model em `given`, e não suportam `materialized view`.
  https://docs.getdbt.com/docs/build/unit-tests
- Contrato com `enforced: true` faz checagem prévia das colunas e inclui tipos e
  restrições no DDL, e falha o build quando violado. Ele suporta `table`,
  `view` com restrições limitadas e `incremental`, e não suporta `ephemeral`
  nem `materialized view`.
  https://docs.getdbt.com/docs/collaborate/govern/model-contracts
- O `dbt build` executa models, tests, snapshots, seeds e funções definidas pelo
  usuário, em ordem do DAG. https://docs.getdbt.com/reference/commands/build
- O dbt Core 1.12 foi lançado em 2026-07-16 e está em suporte ativo; o 1.11 é de
  2025-12-19 e o dbt Core 2.0 aparece como alpha.
  https://docs.getdbt.com/docs/dbt-versions/core
- O motor Fusion é escrito em Rust e é descrito como a experiência padrão da
  instalação do dbt, sobre o runtime Apache 2.0 do dbt Core 2.0.
  https://docs.getdbt.com/docs/fusion/about-fusion
- O dbt-duckdb 1.10.1 foi publicado em 2026-02-17, exige Python 3.10 ou
  superior, `dbt-core>=1.8.0` e `duckdb>=1.0.0`.
  https://pypi.org/project/dbt-duckdb/
- O dbt-duckdb lê arquivo externo como source pela chave `external_location`
  declarada em `meta`. https://github.com/duckdb/dbt-duckdb
- As saídas de laboratório citadas nesta apostila, incluindo
  `PASS=22 WARN=0 ERROR=0`, o SQL compilado do incremental, as duas linhas do
  snapshot e a coluna `campanha_id` como não anulável, foram capturadas em
  execução real com dbt Core 1.12.0, dbt-duckdb 1.10.1 e DuckDB 1.5.5. O
  registro completo, com comando e nível, está em `lab.json`.
