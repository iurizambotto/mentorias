---
title: "Kubernetes para engenharia de dados"
date: 2026-07-31
type: modulo
status: rascunho
tags: [kubernetes, mentoria]
---

# Kubernetes para engenharia de dados

O substrato que dá isolamento de dependência e elasticidade por tarefa, sem
manter servidor ocioso. O recorte é o de quem opera pipeline, não o de quem
opera cluster.

## Estado

Status na trilha: **rascunho**. A ordem recomendada vive em `trilha.yml`, na
raiz da trilha. Seu roteiro pode cursar este módulo em outra posição.

## O que tem aqui

- `apostila.md`, o material de estudo do módulo
- `infrastructure/kind-cluster.yaml`, o cluster local de dois nodes
- `infrastructure/manifests/`, os objetos aplicados no laboratório
- `infrastructure/runbooks/`, o passo a passo para subir, validar e derrubar
- `lab.json`, o manifesto de verificação, nível 3, em 2026-07-31

## O que ainda não existe

Diretórios opcionais ausentes neste módulo, declarados aqui de propósito:

- `scripts/` ausente
- `exercicios/` ausente, os enunciados vivem dentro da apostila
- `diagramas/` ausente

## Como rodar

Siga os runbooks em ordem, a partir da raiz do repositório clonado:

```bash
cat engenharia_de_dados/modulos/kubernetes/infrastructure/runbooks/00_pre_requisitos.md
```

O laboratório roda num cluster local criado com kind, em Docker. Não precisa de
nuvem, não precisa de cluster de trabalho e não custa nada.

**Isole o seu kubeconfig antes de começar.** O runbook de pré-requisitos mostra
como. Se você usa Kubernetes no trabalho, um comando disparado no contexto
errado é um acidente sem desfazer.

## Dois manifestos são quebrados de propósito

O `40-pod-que-estoura-memoria.yaml` pede mais memória do que o próprio limite
permite, e termina em `OOMKilled`. O passo do rollout com tag inexistente
produz `ImagePullBackOff`. Os dois existem para você ler a assinatura da falha
antes de encontrá-la em produção.
