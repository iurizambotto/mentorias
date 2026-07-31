---
title: "Validar e derrubar o laboratorio de Kubernetes"
date: 2026-07-31
type: runbook
status: active
tags:
  - kubernetes
  - laboratorio
---

# Validar e derrubar o laboratório de Kubernetes

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.
Este runbook assume o [01_subir_cluster.md](01_subir_cluster.md) concluído, e a
variável `KUBECONFIG` ainda exportada.

## 1. O estado do namespace

```bash
cd engenharia_de_dados/modulos/kubernetes/infrastructure
kubectl -n campanhas get pods
```

Saída esperada, com quatro situações diferentes ao mesmo tempo:

```
NAME                                   READY   STATUS      RESTARTS   AGE
consumidor-de-memoria                  0/1     OOMKilled   0          34s
servico-de-consulta-7d69958dfb-7hvfr   1/1     Running     0          34s
servico-de-consulta-7d69958dfb-bpw7w   1/1     Running     0          34s
servico-de-consulta-7d69958dfb-vmwpn   1/1     Running     0          34s
transformacao-diaria-4b75d             0/1     Completed   0          34s
testador-de-dns                        0/1     Completed   0          34s
```

O sufixo dos nomes muda a cada execução, e isso é esperado.

`OOMKilled` e `Completed` são resultados diferentes, e os dois estão certos. O
`consumidor-de-memoria` foi escrito para estourar o limite, e o Job e o testador
foram escritos para terminar.

## 2. O Job leu o ConfigMap e o Secret

```bash
kubectl -n campanhas logs job/transformacao-diaria
```

Saída esperada:

```
janela de 7 dias
canais: google_ads,meta_ads,tiktok_ads
processando google_ads
processando meta_ads
processando tiktok_ads
canais processados: 3
```

A janela e a lista de canais vieram do ConfigMap, e o script veio do mesmo
objeto montado como arquivo.

## 3. A assinatura do OOMKilled

```bash
kubectl -n campanhas describe pod consumidor-de-memoria
```

Procure estas linhas:

```
      Reason:       OOMKilled
      Exit Code:    137
    Limits:
      memory:  64Mi
```

Código 137 é 128 mais 9, o sinal `SIGKILL`. Quem matou o processo foi o kernel,
não o Kubernetes, e o Kubernetes apenas reportou.

## 4. O Service pelo nome interno

```bash
kubectl -n campanhas logs testador-de-dns
```

Saída esperada: o HTML de boas vindas do nginx, buscado em
`http://servico-de-consulta.campanhas.svc.cluster.local/`.

Para alcançar do seu navegador:

```bash
kubectl -n campanhas port-forward svc/servico-de-consulta 18080:80
```

Em outro terminal:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:18080/
```

Saída esperada: `200`.

Repare que o Service escuta na porta 80 e o container na 8080. O `targetPort`
faz a tradução, e é por isso que o `port-forward` aponta para a porta do Service.

## 5. Reconciliação: apague um Pod

```bash
POD=$(kubectl -n campanhas get pods -l app=servico-de-consulta -o jsonpath='{.items[0].metadata.name}')
kubectl -n campanhas delete pod "$POD"
kubectl -n campanhas get pods -l app=servico-de-consulta
```

Saída esperada: a contagem de Pods continua a mesma, e um deles tem nome novo e
poucos segundos de idade. Ninguém mandou criar; o controller apenas aproximou o
estado real do desejado.

## 6. Quebrar um rollout de propósito

```bash
kubectl -n campanhas scale deploy/servico-de-consulta --replicas=5
kubectl -n campanhas set image deploy/servico-de-consulta servidor=nginxinc/nginx-unprivileged:9.9-inexistente
kubectl -n campanhas get pods -l app=servico-de-consulta
```

Saída esperada, com os dois estados convivendo:

```
servico-de-consulta-7686d488b9-lqj6q   0/1     ImagePullBackOff   0   25s
servico-de-consulta-7686d488b9-rc4lr   0/1     ImagePullBackOff   0   25s
servico-de-consulta-7686d488b9-rvnct   0/1     ImagePullBackOff   0   25s
servico-de-consulta-7d69958dfb-bpw7w   1/1     Running            0   112s
servico-de-consulta-7d69958dfb-kddqw   1/1     Running            0   64s
```

O serviço continuou de pé. O rollout só derruba um Pod antigo depois que o novo
fica pronto, e o novo nunca ficou.

Desfazendo:

```bash
kubectl -n campanhas rollout undo deploy/servico-de-consulta
kubectl -n campanhas get deploy servico-de-consulta -o jsonpath='{.spec.template.spec.containers[0].image}'
```

Saída esperada: `nginxinc/nginx-unprivileged:1.29-alpine`.

O `undo` emite um aviso dizendo que a anotação de última configuração aplicada
não é atualizada. Leia esse aviso: num fluxo em que o Git é a fonte da verdade,
o `undo` conserta o cluster e não conserta o repositório, e o próximo `apply`
traz a imagem quebrada de volta. O conserto de verdade é reverter o commit.

## 7. Derrubar o cluster

```bash
kind delete cluster --name mentoria-dados
```

Saída esperada:

```
Deleting cluster "mentoria-dados" ...
Deleted nodes: ["mentoria-dados-control-plane" "mentoria-dados-worker"]
```

Isso remove os containers dos nodes e tudo que estava dentro deles. Deixar o
cluster de pé consome memória da sua máquina sem servir para nada.
