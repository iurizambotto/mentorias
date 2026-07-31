---
title: "Infraestrutura como codigo"
date: 2026-07-31
type: modulo
status: rascunho
tags: [terraform, mentoria]
---

# Infraestrutura como código

Como a plataforma de dados nasce a partir de arquivos versionados, em vez de
cliques que ninguém sabe repetir.

## Estado

Status na trilha: **rascunho**. A ordem recomendada vive em `trilha.yml`, na
raiz da trilha. Seu roteiro pode cursar este módulo em outra posição.

## O que tem aqui

- `apostila.md`, o material de estudo do módulo
- `infrastructure/modulos/camada-do-lake/`, um módulo Terraform completo
- `infrastructure/ambientes/dev/`, o ambiente que compõe o módulo com `for_each`
- `infrastructure/runbooks/`, validação e o que fica para o operador humano
- `scripts/verificar_iac.py`, o gate de validação em um comando
- `lab.json`, o manifesto de verificação, nível 2, em 2026-07-31

## O que ainda não existe

Diretórios opcionais ausentes neste módulo, declarados aqui de propósito:

- `exercicios/` ausente, os enunciados vivem dentro da apostila
- `diagramas/` ausente

## O teto deste módulo é nível 2, e é por decisão

`terraform plan` e `terraform apply` são proibidos nesta trilha por guardrail do
workspace. Eles mudam infraestrutura de verdade e custam dinheiro de verdade, e
pertencem ao operador humano ou ao pipeline.

O que este laboratório prova: formatação, sintaxe válida contra o schema do
provider, e conformidade com as regras recomendadas do TFLint. Nada mais, e o
`lab.json` declara o limite por escrito.

Isso não é perda didática. O `plan` vira exercício seu, num ambiente seu, e é
onde se aprende mais. O que a trilha entrega é código que passa no gate.

## Como validar

```bash
python3 scripts/verificar_iac.py
```

Saída esperada: seis linhas começando com `OK` e a linha final
`6 checagem(ns), todas em nivel 2`.

Nenhuma conta em nuvem é necessária. O `terraform init` roda com
`-backend=false`, o que baixa apenas o provider declarado do registro público.

O script recusa por construção qualquer subcomando destrutivo. Se alguém editar
o arquivo e acrescentar `plan` ou `apply`, a checagem falha em vez de executar.

## Um laboratório mostra o que a ferramenta não pega

O sexto laboratório da apostila existe para isso. Um valor que viola o bloco
`validation` da própria variável passa pelo `terraform validate` sem erro,
porque essa checagem acontece no `plan`. Saber onde a rede de proteção termina
vale tanto quanto saber que ela existe.
