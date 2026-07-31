---
title: "Pre-requisitos do laboratorio de Kubernetes"
date: 2026-07-31
type: runbook
status: active
tags:
  - kubernetes
  - laboratorio
---

# Pré-requisitos do laboratório de Kubernetes

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.

## O que precisa estar instalado

| Ferramenta | Versão mínima | Versão usada na verificação |
|---|---|---|
| Docker Engine | 24 | 28.3.3 |
| kind | 0.32.0 | v0.32.0 |
| kubectl | 1.35 | v1.36.3 |

A versão do kind não é detalhe. O kind embute a imagem do node, e a imagem
padrão do kind 0.32.0 é o Kubernetes v1.36.1. Uma versão antiga do kind sobe um
Kubernetes antigo, e parte do que a apostila afirma deixa de valer.

## Conferir o que você tem

```bash
docker --version
kind version
kubectl version --client
```

Se o `kind version` mostrar algo abaixo de 0.32.0, atualize antes de seguir. A
instalação é o download de um binário, descrita na documentação oficial do
projeto.

## Recursos da máquina

O cluster sobe dois nodes, cada um em um container. Isso pede pouca coisa:

- 2 vCPUs livres
- 4 GB de memória livre
- alguns gigabytes de disco para as imagens

## Proteja o seu kubeconfig

Se você já usa Kubernetes no trabalho, o `~/.kube/config` tem contexto de
cluster real. O laboratório não precisa tocar nele:

```bash
export KUBECONFIG="$PWD/kubeconfig-mentoria"
```

Rode isso em cada terminal novo do laboratório. Um `kubectl delete` disparado no
contexto errado é o tipo de acidente que não tem desfazer.

## Onde o laboratório vive

```bash
cd engenharia_de_dados/modulos/kubernetes/infrastructure
ls
```

Você deve ver `kind-cluster.yaml`, `manifests/` e `runbooks/`.

Próximo passo: [01_subir_cluster.md](01_subir_cluster.md).
