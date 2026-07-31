---
title: "O que fica para o operador humano"
date: 2026-07-31
type: runbook
status: active
tags:
  - terraform
  - operacao
---

# O que fica para o operador humano

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.

Este runbook não tem comando para você rodar no laboratório. Ele descreve o que
acontece **depois** do gate de validação, num projeto real, e por quem.

## A fronteira

| Etapa | Quem faz |
|---|---|
| Escrever o código | você |
| `fmt`, `validate`, TFLint | você, e o pipeline repete |
| Revisar o pull request | outra pessoa do time |
| `terraform plan` | o pipeline, e o resultado vai para o pull request |
| Ler o plano | quem revisa e quem aprova |
| `terraform apply` | o pipeline, depois da aprovação |
| `terraform destroy` | operador humano, com intenção explícita |

Esta trilha não executa as três últimas linhas, e a razão é o guardrail do
workspace: `plan` e `apply` mudam infraestrutura de verdade e custam dinheiro de
verdade, então eles pertencem a quem responde por isso.

## Como o plano é lido

O `plan` mostra três tipos de mudança, e o símbolo importa:

| Símbolo | Significado |
|---|---|
| `+` | recurso será criado |
| `~` | recurso será alterado no lugar |
| `-/+` | recurso será **destruído e recriado** |
| `-` | recurso será destruído |

As duas últimas linhas são as que exigem atenção. Num bucket de data lake,
`-/+` significa perder o conteúdo, e a causa costuma ser a mudança de um atributo
que o provider marca como imutável, por exemplo o nome do bucket.

A regra prática: **destroy inesperado no plano é aviso, nunca detalhe a
ignorar.** Se você não sabe explicar por que aquele recurso está sendo
recriado, não aprove.

## O que fazer antes do primeiro apply

1. **Criar o backend remoto à mão, uma vez.** O bucket de state não pode ser
   provisionado pelo mesmo código que o usa, porque ele precisa existir antes.
2. **Restringir o acesso ao state.** Ele guarda valor sensível em texto claro,
   conforme a própria documentação da ferramenta. Criptografia em repouso e
   acesso por IAM restrito não são opcionais.
3. **Descomentar o bloco `backend` em `ambientes/dev/main.tf`** e trocar os nomes
   pelos reais.
4. **Trocar o `prefixo_do_bucket`.** Nome de bucket é único no mundo inteiro, e o
   valor do laboratório é um exemplo.

## Quando o console foi usado por engano

Alguém mexeu no console e o `plan` passou a mostrar diferença. As opções são
duas, e nenhuma delas é aplicar por cima sem pensar:

- **`import`**, para trazer ao código um recurso que existe e não está no state;
- **`moved`**, para renomear no código algo que já está sob gestão, sem destruir.

Aplicar por cima é a terceira opção, e ela reescreve a mudança manual. Às vezes
é o que se quer, e às vezes a mudança manual era um conserto de emergência que
alguém não documentou. Pergunte antes.

## O fluxo que elimina o apply do terminal

O valor real da prática aparece quando ninguém mais aplica do próprio terminal:

1. Você abre um pull request com a mudança de código.
2. O pipeline roda `fmt`, `validate` e TFLint, que é exatamente o gate do
   [01_validar.md](01_validar.md).
3. O pipeline roda `plan` e publica o resultado no pull request.
4. Alguém revisa o código e o plano.
5. Depois do merge, o pipeline roda `apply`.

Sem isso não existe revisão, não existe rastreio de quem mudou o quê, e não
existe trava contra dois `apply` simultâneos.
