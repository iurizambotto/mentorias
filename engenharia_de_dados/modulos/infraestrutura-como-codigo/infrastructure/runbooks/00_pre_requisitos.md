---
title: "Pre-requisitos do laboratorio de infraestrutura como codigo"
date: 2026-07-31
type: runbook
status: active
tags:
  - terraform
  - laboratorio
---

# Pré-requisitos do laboratório de infraestrutura como código

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.

## O que precisa estar instalado

| Ferramenta | Versão mínima | Versão usada na verificação |
|---|---|---|
| Terraform | 1.9 | v1.15.8 |
| TFLint | 0.60 | v0.64.0 |
| Python | 3.11 | 3.11 |

O `required_version` do código exige Terraform 1.9 ou superior. Versão anterior
recusa a configuração antes de qualquer outra coisa.

## O que você NÃO precisa

**Conta em nuvem.** Nenhuma. Nenhum comando deste laboratório cria recurso,
consulta recurso existente ou usa credencial.

O `terraform init` roda com `-backend=false`, o que significa que ele apenas
baixa o provider declarado do registro público. Ele não configura backend
remoto, não lê state e não fala com nenhuma conta.

## Conferir o que você tem

```bash
terraform version
tflint --version
```

## Onde o laboratório vive

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure
ls
```

Você deve ver `ambientes/`, `modulos/`, `runbooks/` e `.tflint.hcl`.

## O teto deste laboratório

Este módulo para no nível 2 da escada de verificação, e isso é decisão, não
limitação. `terraform plan` e `terraform apply` são operações do operador humano
ou do pipeline, e não entram em laboratório de estudo nem em automação de
agente.

O que você prova aqui: formatação, sintaxe válida contra o schema do provider e
conformidade com as regras recomendadas do TFLint. O que fica para o operador
está descrito em [02_o_que_fica_para_o_operador.md](02_o_que_fica_para_o_operador.md).

Próximo passo: [01_validar.md](01_validar.md).
