---
title: "Subir o cluster e aplicar o estado desejado"
date: 2026-07-31
type: runbook
status: active
tags:
  - kubernetes
  - laboratorio
---

# Subir o cluster e aplicar o estado desejado

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.

## 1. Entrar no diretório e isolar o kubeconfig

```bash
cd engenharia_de_dados/modulos/kubernetes/infrastructure
export KUBECONFIG="$PWD/kubeconfig-mentoria"
```

## 2. Criar o cluster

```bash
kind create cluster --config kind-cluster.yaml
```

A primeira execução baixa a imagem do node, que tem algumas centenas de
megabytes. As seguintes reaproveitam.

Confira:

```bash
kubectl get nodes
```

Saída esperada, com os dois nodes em `Ready`:

```
NAME                           STATUS   ROLES           AGE   VERSION
mentoria-dados-control-plane   Ready    control-plane   50s   v1.36.1
mentoria-dados-worker          Ready    <none>          40s   v1.36.1
```

O cluster tem dois nodes de propósito. Com um só, a diferença entre control
plane e worker nunca aparece, e o `nodeSelector` do Job não teria para onde
apontar.

## 3. Aplicar o namespace primeiro

```bash
kubectl apply -f manifests/00-namespace.yaml
```

A ordem importa. Todo objeto seguinte vive dentro do namespace `campanhas`, e o
`apply` da pasta inteira em um cluster novo pode reclamar de namespace
inexistente antes de o namespace ser criado.

## 4. Aplicar o resto

```bash
kubectl apply -f manifests/
```

Saída esperada, sem nenhum aviso de `PodSecurity`:

```
namespace/campanhas unchanged
configmap/parametros-etl created
secret/credenciais-do-lake created
deployment.apps/servico-de-consulta created
service/servico-de-consulta created
job.batch/transformacao-diaria created
pod/consumidor-de-memoria created
pod/testador-de-dns created
```

A ausência de aviso é resultado, não acaso. O namespace aplica o perfil
`restricted` do Pod Security Admission, e todas as cargas deste laboratório
foram escritas para satisfazê-lo.

## 5. Acompanhar o rollout

```bash
kubectl -n campanhas rollout status deploy/servico-de-consulta
```

Saída esperada, na última linha:

```
deployment "servico-de-consulta" successfully rolled out
```

Próximo passo: [02_validar.md](02_validar.md).
