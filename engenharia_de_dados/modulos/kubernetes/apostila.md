---
title: "Apostila, Kubernetes para engenharia de dados"
date: 2026-07-31
type: apostila
status: draft
project: zambotto-mentoria
tags: [engenharia_de_dados, kubernetes]
---

# Apostila, Kubernetes para engenharia de dados

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

## Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O problema que o Kubernetes resolve](#3-o-problema-que-o-kubernetes-resolve)
- [4. Arquitetura do cluster](#4-arquitetura-do-cluster)
- [5. Pod, a unidade de execução](#5-pod-a-unidade-de-execução)
- [6. Workloads, quem gerencia os Pods](#6-workloads-quem-gerencia-os-pods)
- [7. Configuração e segredo](#7-configuração-e-segredo)
- [8. Rede, do Service ao que entra no cluster](#8-rede-do-service-ao-que-entra-no-cluster)
- [9. Recursos, limites e QoS](#9-recursos-limites-e-qos)
- [10. Agendamento, onde o Pod roda](#10-agendamento-onde-o-pod-roda)
- [11. Escalonamento](#11-escalonamento)
- [12. Segurança](#12-segurança)
- [13. Kubernetes na engenharia de dados](#13-kubernetes-na-engenharia-de-dados)
- [14. Laboratório](#14-laboratório)
- [15. Exercícios e entregáveis](#15-exercícios-e-entregáveis)
- [16. Mini-desafio com solução](#16-mini-desafio-com-solução)
- [17. Rubrica de validação da aprendizagem](#17-rubrica-de-validação-da-aprendizagem)
- [18. Erros comuns e como corrigir](#18-erros-comuns-e-como-corrigir)
- [19. Plano de continuidade](#19-plano-de-continuidade)
- [20. Glossário](#20-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

## 0. Como usar esta apostila

**Leitura linear.** As seções 3 a 6 constroem o modelo mental, e sem elas o
resto vira decoreba de YAML. Da 7 à 12 cada seção trata de uma decisão concreta.
A 13 é o recorte de engenharia de dados, e é onde tudo se junta.

**Revisão pontual.** Se você já opera Kubernetes e veio atrás de um assunto:
recursos e QoS na 9, agendamento na 10, segurança na 12, diagnóstico na 18.

**Pré-requisitos.** O módulo de Docker e ambiente local. Você precisa saber o
que é uma imagem, o que é um container e por que a imagem é imutável. Não
precisa de cluster no trabalho, e não precisa de nuvem.

**O laboratório é o centro deste módulo.** Kubernetes é conceito simples com
consequência não óbvia, e a única forma de fixar é ver o cluster reagir. A seção
14 tem oito laboratórios, todos executados de verdade, com saída capturada.

**Versões.** Tudo foi verificado com Kubernetes v1.36.1 no cluster, kind v0.32.0
e kubectl v1.36.3, em 2026-07-31. Onde a versão muda o comportamento, a apostila
diz qual.

## 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** o modelo de estado desejado e por que ninguém "sobe" um Pod.
2. **Ler** um manifesto e dizer o que cada bloco faz, sem copiar de exemplo.
3. **Escolher** entre Deployment, StatefulSet, DaemonSet e Job para uma carga de
   dados, e justificar.
4. **Definir** requests e limits de uma tarefa, prever a classe de QoS
   resultante e o que acontece sob pressão de memória.
5. **Diagnosticar** as quatro assinaturas de falha mais comuns a partir do que o
   cluster mostra, sem tentativa e erro.
6. **Relacionar** o Kubernetes ao Airflow que você já conhece, entendendo o que
   o executor faz por baixo.

## 2. Contexto de negócio

A startup fictícia de marketing e e-commerce chegou aqui com um pipeline que
funciona e um problema novo.

O Airflow orquestra tarefas de ingestão, transformação e carga. Cada tarefa tem
dependências próprias: uma precisa de uma biblioteca de scraping, outra de um
cliente de banco, outra de uma versão específica de uma biblioteca de dados. Com
tudo rodando no mesmo processo, atualizar a dependência de uma tarefa quebra
outra. O time já perdeu uma manhã por causa disso.

Existe também o problema do custo. A carga é irregular: quase nada durante o
dia, um pico grande na madrugada. A máquina precisa ser dimensionada para o
pico, e fica parada o resto do tempo.

A pergunta deste módulo é: **como dar a cada tarefa o seu próprio ambiente e a
sua própria fatia de máquina, sem manter servidor ocioso e sem que uma tarefa
contamine a outra.**

O que este módulo acrescenta:

| Aspecto | Como estava | Com Kubernetes |
|---|---|---|
| Dependências | Compartilhadas, conflito entre tarefas | Uma imagem por tarefa |
| Capacidade | Dimensionada para o pico, ociosa o resto | Alocada por tarefa e devolvida |
| Falha de uma tarefa | Pode derrubar o processo | Isolada no próprio Pod |
| Recuperação | Alguém percebe e reinicia | Reconciliação contínua |

## 3. O problema que o Kubernetes resolve

### 3.1 O que o container não resolve

**O que é**

O container resolveu empacotar: a aplicação e suas dependências viajam juntas e
rodam igual em qualquer lugar. Ele não resolveu operar dezenas ou centenas
deles.

Falta escolher em qual máquina cada container roda, reiniciar o que morreu,
substituir sem derrubar o serviço, dar endereço estável ao que muda de lugar e
distribuir capacidade entre cargas que competem.

**O equívoco comum**

Achar que Kubernetes é "Docker em escala". Ele é um sistema de reconciliação
que por acaso executa containers. Entender isso muda o modo de pensar: você não
manda executar, você declara o que quer existir.

### 3.2 Estado desejado e reconciliação

**O que é**

Você escreve o resultado que quer. O cluster compara continuamente o estado real
com o desejado e age para reduzir a diferença. Esse laço nunca termina.

**Como funciona na prática**

No Lab 2 você apaga um Pod à mão. Ninguém manda criar outro, e outro aparece:

```
NAME                                   READY   STATUS    RESTARTS   AGE
servico-de-consulta-7d69958dfb-65j9q   1/1     Running   0          9s
servico-de-consulta-7d69958dfb-f7mlm   1/1     Running   0          3m13s
servico-de-consulta-7d69958dfb-kddqw   1/1     Running   0          3m40s
```

O Pod de 9 segundos é o substituto. O controller do Deployment viu que existiam
menos réplicas do que o declarado e criou a diferença.

**O equívoco comum**

Tentar consertar o cluster com comandos imperativos. Apagar um Pod problemático
funciona por trinta segundos, porque o controller recria exatamente o mesmo Pod
a partir do mesmo manifesto. O conserto é sempre no estado desejado.

**Como inspecionar**

`kubectl get pods` com a coluna `AGE`. Idade que reinicia é sinal de que algo
está sendo recriado, e a coluna `RESTARTS` diz se é o container ou o Pod.

## 4. Arquitetura do cluster

**O que é**

Um cluster tem dois planos. O control plane decide, os nodes executam.

| Componente | Papel |
|---|---|
| kube-apiserver | Porta de entrada única. Valida e persiste todo objeto |
| etcd | Banco chave-valor que guarda o estado desejado |
| kube-scheduler | Escolhe em qual node cada Pod novo vai rodar |
| controller-manager | Laços de reconciliação que aproximam real do desejado |
| kubelet | Agente do node, sobe e vigia os containers |
| runtime de container | Executa de fato, via containerd ou equivalente |

**Como funciona na prática**

Tudo passa pelo apiserver, inclusive o `kubectl`. Quando você aplica um
manifesto, o `kubectl` não fala com o node: ele fala com o apiserver, que valida
e grava. O scheduler percebe um Pod sem node, escolhe um, e o kubelet daquele
node percebe que tem trabalho.

Nenhum desses componentes chama o outro diretamente. Todos observam o apiserver.
É por isso que o cluster continua funcionando quando um controller cai: o estado
está no etcd, e a reconciliação recomeça quando o controller volta.

**O equívoco comum**

Achar que o control plane executa as cargas. Ele decide. Num cluster gerenciado
de nuvem você nem enxerga essas máquinas. No laboratório o cluster tem dois
nodes justamente para a diferença ficar visível.

**Como inspecionar**

```bash
kubectl get nodes
```

No Lab 0 a saída mostra `mentoria-dados-control-plane` com a role
`control-plane` e `mentoria-dados-worker` sem role, os dois em `Ready` e na
versão v1.36.1.

## 5. Pod, a unidade de execução

### 5.1 O Pod não é um container

**O que é**

O Kubernetes não agenda containers, agenda Pods. Um Pod é um ou mais containers
que compartilham rede e volumes, e que vivem e morrem juntos.

Containers do mesmo Pod conversam por `localhost`, porque compartilham o
namespace de rede. O Pod tem um IP, não cada container.

**O equívoco comum**

Colocar dois processos independentes no mesmo Pod porque "andam juntos". Se um
pode escalar sem o outro, são dois Pods. O Pod é a unidade de escala, e o que
está junto escala junto.

### 5.2 Init containers e sidecars

**O que é**

Um init container roda antes dos containers principais, em ordem, até terminar.
Serve para preparar dado ou esperar dependência.

O sidecar nativo é um init container com `restartPolicy: Always`, o que faz com
que ele continue rodando durante toda a vida do Pod, em vez de apenas na
inicialização.

```yaml
initContainers:
  - name: coletor-de-log
    image: alpine:3.22
    restartPolicy: Always
    command: ["sh", "-c", "tail -F /opt/logs.txt"]
```

**Atenção à versão, porque o deck da aula generaliza aqui.** O recurso está
ativo por padrão desde o Kubernetes 1.29, e passou a **estável** no 1.33. São
coisas diferentes: entre 1.29 e 1.32 ele funcionava como recurso ainda em
evolução, sujeito a mudança. Em cluster nessa faixa, confira antes de depender.

### 5.3 O Pod é efêmero

**O que é**

Pod não é atualizado, é substituído. Mudar a imagem cria Pods novos e apaga os
antigos.

**O equívoco comum**

Depender do IP ou do nome de um Pod. Os dois mudam. É exatamente por isso que
existe o Service, e é por isso que o laboratório mostra o nome do Pod mudando a
cada substituição.

### 5.4 Probes

| Probe | Pergunta que responde | O que acontece se falhar |
|---|---|---|
| `readinessProbe` | Está pronto para receber tráfego? | Sai do balanceamento do Service |
| `livenessProbe` | Ainda está vivo? | O container é reiniciado |
| `startupProbe` | Já terminou de subir? | Protege o lento de ser morto cedo |

**O equívoco comum**

Confundir `readiness` com `liveness`. Uma aplicação que está subindo e ainda não
respondeu ao primeiro tráfego não está quebrada, está ocupada. Configurar
`liveness` agressivo nesse caso cria um laço de reinício sem causa real.

## 6. Workloads, quem gerencia os Pods

**O que é**

Na prática você quase nunca cria um Pod diretamente. Você declara um controller,
e ele cuida de criar, substituir e escalar.

| Controller | Para que serve | Exemplo em dados |
|---|---|---|
| Deployment | Aplicação sem estado, com rollout e rollback | Serviço de query, API interna |
| StatefulSet | Identidade e disco estáveis por réplica | Banco, broker de mensagem |
| DaemonSet | Um Pod por node | Agente de log ou de métrica |
| Job | Executa até concluir, com repetição em caso de falha | Transformação diária |
| CronJob | Job com agenda | Carga periódica sem orquestrador |

**Como funciona na prática**

O laboratório usa dois. O `servico-de-consulta` é um Deployment, porque é um
serviço sem estado que precisa de rollout controlado. A `transformacao-diaria` é
um Job, porque roda, termina e sai.

Na saída do Lab 1 os dois convivem, com estados diferentes e ambos corretos:

```
servico-de-consulta-7d69958dfb-7hvfr   1/1     Running     0   34s
transformacao-diaria-4b75d             0/1     Completed   0   34s
```

`Completed` com `0/1` pronto não é falha. É um Job que fez o que devia.

**O equívoco comum**

Usar Deployment para carga que termina. O Deployment quer réplicas rodando o
tempo todo, então ele reinicia o processo que terminou com sucesso, e você
recebe um `CrashLoopBackOff` de algo que funcionou. Carga que termina é Job.

**Como inspecionar**

`kubectl get all -n <namespace>` mostra a cadeia Deployment, ReplicaSet e Pod. O
ReplicaSet no meio é o que permite o rollback: cada versão tem o seu.

## 7. Configuração e segredo

**O que é**

A imagem é imutável, então configuração precisa entrar de fora. É isso que
separa uma imagem reaproveitável de uma imagem por ambiente.

O ConfigMap guarda parâmetro não sensível. O Secret guarda credencial e token.

**Como funciona na prática**

O ConfigMap do laboratório carrega dois parâmetros e um arquivo inteiro:

```yaml
data:
  JANELA_DIAS: "7"
  CANAIS: "google_ads,meta_ads,tiktok_ads"
  transformar.sh: |
    #!/bin/sh
    echo "janela de ${JANELA_DIAS} dias"
```

O Job injeta os parâmetros como variáveis de ambiente e monta o script como
arquivo. No Lab 3 o resultado aparece no log:

```
janela de 7 dias
canais: google_ads,meta_ads,tiktok_ads
processando google_ads
processando meta_ads
processando tiktok_ads
canais processados: 3
```

Nada disso está na imagem. A mesma imagem `alpine:3.22` roda outro script se o
ConfigMap mudar.

**O equívoco comum**

Achar que Secret é criptografia. Não é. O valor é codificado em base64, e quem
tem permissão de leitura no objeto lê o conteúdo. O que protege um Secret é RBAC
restrito mais criptografia em repouso no etcd.

Em ambiente real o Secret não vive no Git. Ele vem de um cofre gerenciado, por
um operador que o injeta no cluster. O arquivo `11-secret.yaml` do laboratório
existe para ser lido, e o valor dele é um marcador.

**Como inspecionar**

Um Secret mudado não chega sozinho ao Pod que o consome por variável de
ambiente. Variável de ambiente é lida na criação do processo, então mudar o
Secret exige recriar o Pod. Montado como volume o comportamento é outro, e o
arquivo é atualizado.

## 8. Rede, do Service ao que entra no cluster

### 8.1 O Service dá endereço estável

**O que é**

Pods nascem e morrem com IPs diferentes. O Service dá um nome DNS estável e
balanceia entre os Pods que casam com o seletor.

**Como funciona na prática**

No Lab 5 um Pod alcança o serviço pelo nome completo, de dentro do cluster:

```
http://servico-de-consulta.campanhas.svc.cluster.local/
```

O formato é `<service>.<namespace>.svc.cluster.local`. Dentro do mesmo
namespace, `servico-de-consulta` basta.

Repare numa sutileza do laboratório: o Service escuta na porta 80 e o container
na 8080. O `targetPort` faz a tradução. Isso é comum quando a imagem roda como
usuário sem privilégio, porque portas abaixo de 1024 exigem capacidade extra.

**O equívoco comum**

Achar que o Service aponta para o Deployment. Ele não aponta para nada: ele
seleciona por label. Um erro de label faz o Service existir com zero endpoints,
e o sintoma é conexão recusada sem nenhum erro no Deployment.

**Como inspecionar**

```bash
kubectl -n campanhas get endpoints servico-de-consulta
```

Lista vazia significa que o seletor não casou com nenhum Pod pronto.

### 8.2 Como o tráfego externo entra

| Recurso | O que faz |
|---|---|
| ClusterIP | Endereço interno, o padrão |
| NodePort | Abre uma porta em cada node |
| LoadBalancer | Pede um balanceador ao provedor de nuvem |
| Gateway API | Roteamento HTTP com papéis separados entre infra e aplicação |

**Uma decisão de projeto, não de detalhe.** O Ingress NGINX, que foi o padrão de
fato por anos, foi arquivado em 24 de março de 2026, e o próprio projeto
recomenda que quem não o usa hoje não comece a usar, escolhendo uma
implementação da Gateway API. Material anterior a 2026 vai ensinar Ingress
NGINX, e é preciso saber que aquele caminho fechou.

Para desenvolvimento, nada disso é necessário. O `port-forward` do Lab 5 leva a
porta do Service para a sua máquina e resolve o dia a dia.

## 9. Recursos, limites e QoS

### 9.1 requests e limits fazem coisas diferentes

**O que é**

`requests` é o que o scheduler reserva, e decide **onde** o Pod cabe. `limits` é
teto rígido, e decide **o que acontece** quando o processo passa dele.

| Recurso | Passar do limite causa |
|---|---|
| Memória | O processo é morto, com `OOMKilled` |
| CPU | O processo é afunilado, e fica lento |

A assimetria é importante. Memória não tem como ser emprestada, então a única
saída do kernel é matar. CPU é divisível no tempo, então dá para atrasar.

**Como funciona na prática**

O Lab 4 mostra o caso. O Pod pede 200 MiB contra um limite de 64 MiB:

```
      Reason:       OOMKilled
      Exit Code:    137
    Limits:
      memory:  64Mi
```

O código 137 é 128 mais 9, o sinal `SIGKILL`. Quem matou foi o kernel, e o
Kubernetes apenas reportou. Isso importa no diagnóstico: não adianta procurar
erro no log da aplicação, porque ela não teve chance de escrever nada.

**O equívoco comum**

Definir `limits` de CPU generosos achando que ajuda. Limite de CPU produz
afunilamento mesmo com a máquina ociosa, porque o teto é por período de tempo,
não por disponibilidade. Em carga de dados, é comum definir `requests` de CPU e
deixar o `limits` de CPU de fora, mantendo o de memória.

### 9.2 As classes de QoS

**O que é**

A classe é derivada, não declarada. Ela decide quem é despejado primeiro quando
o node fica sem memória.

| Classe | Como se obtém | Ordem de despejo |
|---|---|---|
| Guaranteed | `requests` igual a `limits`, em todos os containers | último |
| Burstable | `requests` menor que `limits`, ou só um dos dois | meio |
| BestEffort | Nenhum `requests` nem `limits` | primeiro |

**Como inspecionar**

No laboratório, todas as cargas saem como `Burstable`, porque em todas o
`requests` é menor que o `limits`:

```
POD                                    QOS         NODE
consumidor-de-memoria                  Burstable   mentoria-dados-worker
servico-de-consulta-7d69958dfb-7hvfr   Burstable   mentoria-dados-worker
transformacao-diaria-4b75d             Burstable   mentoria-dados-worker
```

Para obter `Guaranteed`, iguale os dois valores. Vale para a tarefa que não pode
morrer no meio, e custa reserva de capacidade que fica sua mesmo sem uso.

### 9.3 Mudar recurso sem recriar o Pod

Desde o Kubernetes 1.35, redimensionar CPU e memória de um Pod em execução é
recurso estável. Antes disso, mudar recurso significava substituir o Pod.

Para carga de dados isso muda um hábito: dá para ajustar uma tarefa longa que
está apertada, em vez de matá-la e recomeçar do zero.

## 10. Agendamento, onde o Pod roda

**O que é**

Em cluster de dados os nodes não são iguais. Existe node com muita memória, node
com GPU e node barato que pode ser retomado a qualquer momento.

| Mecanismo | O que faz |
|---|---|
| `nodeSelector` | Filtro simples por label do node |
| Affinity | Regras ricas, obrigatórias ou preferenciais |
| Taints e tolerations | O node repele Pods; só entra quem tolera |
| Topology spread | Distribui réplicas entre zonas e nodes |
| PriorityClass | Define quem é despejado primeiro quando falta capacidade |

**Como funciona na prática**

O cluster do laboratório declara um label no node worker:

```yaml
  - role: worker
    labels:
      workload: batch
```

E o Job pede exatamente aquele node:

```yaml
      nodeSelector:
        workload: batch
```

É o padrão real de separar carga de lote da carga que responde a usuário.

**O equívoco comum**

Confundir `nodeSelector` com taint. O seletor diz onde o Pod **quer** ir, e não
impede que outro Pod vá para o mesmo node. O taint é o inverso: o node repele
quem não declara tolerância. Para reservar node caro, o seletor sozinho não
basta.

## 11. Escalonamento

**O que é**

Escala tem dois níveis, e eles são complementares: mais réplicas da aplicação, e
mais máquinas no cluster.

| Mecanismo | Escala o quê | Reage a |
|---|---|---|
| HPA | Réplicas do Pod | CPU, memória ou métrica customizada |
| VPA | `requests` e `limits` do Pod | Consumo observado |
| Escalonamento por evento | Réplicas, inclusive até zero | Fila, lag de tópico, evento externo |
| Autoscaler de node | Máquinas do cluster | Pods que não couberam |

**Como funciona na prática**

Escalar à mão é uma linha, e o Lab 6 começa por ela:

```bash
kubectl -n campanhas scale deploy/servico-de-consulta --replicas=5
```

Em produção o número não é escrito à mão. Para pipeline de dados o gatilho
raramente é CPU: o sinal útil costuma ser o tamanho da fila ou o atraso do
consumidor, e é por isso que escalonamento por evento externo domina esse
cenário.

**O equívoco comum**

Ligar escalonamento de Pod sem escalonamento de node. Os Pods novos são criados,
não cabem em lugar nenhum e ficam em `Pending`. A métrica de escala sobe, o
número de réplicas sobe, e nada é processado.

## 12. Segurança

### 12.1 RBAC e identidade do Pod

**O que é**

O RBAC define permissões por verbo e recurso, ligadas a uma identidade. Um Pod
tem identidade própria, a ServiceAccount.

**O equívoco comum**

Guardar chave de nuvem em Secret para o Pod usar. Existe caminho melhor em toda
nuvem: associar a ServiceAccount a um papel do provedor, e o Pod recebe
credencial temporária sem que nenhuma chave seja escrita. Menos coisa para
vazar, e rotação automática.

### 12.2 Pod Security Admission

**O que é**

O Pod Security Admission é o controlador que recusa Pod fora do padrão. Ele é
estável desde o Kubernetes 1.25 e substituiu o PodSecurityPolicy.

Ele tem três níveis e três modos:

| Nível | O que permite |
|---|---|
| `privileged` | Tudo |
| `baseline` | Bloqueia o que é notoriamente perigoso |
| `restricted` | Exige boas práticas: sem root, sem escalar privilégio, sem capacidades |

| Modo | O que faz na violação |
|---|---|
| `enforce` | Recusa o Pod |
| `audit` | Registra no log de auditoria |
| `warn` | Mostra aviso a quem aplicou |

A configuração é por label no namespace, no formato
`pod-security.kubernetes.io/<MODO>: <NÍVEL>`.

**Como funciona na prática**

O namespace do laboratório aplica o nível mais estrito nos três modos:

```yaml
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

E toda carga foi escrita para satisfazê-lo:

```yaml
      securityContext:
        runAsNonRoot: true
        runAsUser: 101
        seccompProfile:
          type: RuntimeDefault
```

Por isso a saída do Lab 1 não tem nenhum aviso. Isso é resultado, não acaso: a
primeira versão deste laboratório usava a imagem oficial do nginx, que roda como
root e precisa da capacidade `CHOWN` para preparar o próprio cache. Ela entrou
em `CrashLoopBackOff` com a mensagem
`chown("/var/cache/nginx/client_temp", 101) failed (1: Operation not permitted)`.
A correção não foi devolver a capacidade, e sim trocar por uma imagem que já roda
sem privilégio.

**O equívoco comum**

Começar por `enforce: restricted` num namespace que já tem carga rodando. Você
recusa Pod em produção. O caminho é ligar `warn` e `audit` primeiro, corrigir o
que aparecer, e só então mudar o `enforce`. O laboratório pode começar no
estrito porque nasceu assim.

### 12.3 Imagem

Tag imutável, registro privado e varredura de vulnerabilidade no processo de
entrega. O laboratório usa `nginxinc/nginx-unprivileged:1.29-alpine` e não
`latest`, e a razão aparece no Lab 6: sem tag fixa, você não sabe para onde o
rollback está voltando.

## 13. Kubernetes na engenharia de dados

### 13.1 O que muda no pipeline

**O que é**

Para o time de dados o Kubernetes é o substrato que dá isolamento de dependência
e elasticidade por tarefa.

| Ferramenta | Como aparece no cluster |
|---|---|
| Airflow | Um Pod por task, com imagem e recursos próprios |
| Spark | Um operador dedicado, com o job como recurso do cluster |
| dbt | Um Job efêmero que roda e sai |
| Query engine | Um Deployment, porque precisa estar de pé |

O `transformacao-diaria` do laboratório é o formato de todos os itens de lote
dessa tabela: um Job, com sua imagem, seus recursos e seu node.

### 13.2 Airflow no Kubernetes

**Como funciona na prática**

Com o `KubernetesPodOperator`, cada task vira um Pod. É isso que resolve o
conflito de dependências que abriu a seção 2 desta apostila.

```python
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from kubernetes.client import models as k8s

extrair = KubernetesPodOperator(
    task_id="extrair_precos",
    image="registry.exemplo/etl-python:1.0.0",
    cmds=["python", "-m", "coletores.precos"],
    container_resources=k8s.V1ResourceRequirements(
        requests={"cpu": "1", "memory": "2Gi"},
        limits={"memory": "2Gi"},
    ),
    node_selector={"workload": "batch"},
    on_finish_action="delete_pod",
)
```

<!-- verificacao: nivel 1, conferido contra a referencia do provider cncf.kubernetes, nao executado, 2026-07-31 -->

Dois detalhes deste bloco custam tempo de quem descobre sozinho, e por isso
estão aqui:

**`container_resources` espera um objeto, não um dicionário.** O tipo é
`kubernetes.client.models.V1ResourceRequirements`. Passar um dicionário é o erro
mais comum de quem migra de exemplo antigo.

**`on_finish_action` substituiu `is_delete_operator_pod`.** Os valores são
`delete_pod`, `delete_succeeded_pod`, `keep_pod` e `delete_active_pod`. Material
que ainda usa o parâmetro antigo está desatualizado.

Este bloco foi conferido contra a referência oficial do provider, e **não foi
executado**. O laboratório deste módulo não sobe Airflow, e afirmar mais do que
isso seria inventar.

### 13.3 O que o Kubernetes não resolve

Ele não agenda por tempo com dependência entre tarefas, não observa fonte
externa e não faz backfill. Isso continua sendo do orquestrador, que é o assunto
do módulo de Airflow. O CronJob resolve carga periódica simples e não substitui
um DAG.

## 14. Laboratório

O laboratório roda num cluster local criado com kind, em Docker, com Kubernetes
v1.36.1. Não precisa de nuvem e não custa nada.

Os runbooks em `infrastructure/runbooks/` trazem o passo a passo completo,
inclusive como isolar o seu kubeconfig antes de começar. Faça isso: se você usa
Kubernetes no trabalho, um comando no contexto errado não tem desfazer.

### Lab 0: Criar o cluster local

Pré-condição: Docker, kind 0.32.0 ou superior, kubectl 1.35 ou superior.

```bash
cd engenharia_de_dados/modulos/kubernetes/infrastructure
export KUBECONFIG="$PWD/kubeconfig-mentoria"
kind create cluster --config kind-cluster.yaml
kubectl get nodes
```

Saída esperada: `mentoria-dados-control-plane` e `mentoria-dados-worker`, ambos
em `Ready` e na versão `v1.36.1`.

### Lab 1: Aplicar o estado desejado

```bash
kubectl apply -f manifests/00-namespace.yaml
kubectl apply -f manifests/
kubectl -n campanhas rollout status deploy/servico-de-consulta
```

Saída esperada: `deployment "servico-de-consulta" successfully rolled out`, sem
nenhum aviso de `PodSecurity`.

O namespace vai primeiro de propósito. Aplicar a pasta inteira num cluster novo
pode falhar, porque os objetos seguintes referenciam um namespace que ainda não
existe.

### Lab 2: Apagar um Pod e ver o cluster reconciliar

```bash
POD=$(kubectl -n campanhas get pods -l app=servico-de-consulta -o jsonpath='{.items[0].metadata.name}')
kubectl -n campanhas delete pod "$POD"
kubectl -n campanhas get pods -l app=servico-de-consulta
```

Saída esperada: a contagem de Pods continua a mesma, e um deles tem nome novo e
poucos segundos de idade.

### Lab 3: Ver ConfigMap e Secret injetados

```bash
kubectl -n campanhas logs job/transformacao-diaria
```

Saída esperada: a janela de 7 dias, os três canais e a linha
`canais processados: 3`. Nada disso está dentro da imagem.

### Lab 4: Ler a assinatura do OOMKilled

```bash
kubectl -n campanhas get pod consumidor-de-memoria
kubectl -n campanhas describe pod consumidor-de-memoria
```

Saída esperada: `STATUS OOMKilled` na listagem, e `Reason: OOMKilled` com
`Exit Code: 137` no detalhe.

Este Pod é quebrado de propósito. Ver a assinatura aqui é mais barato do que
encontrá-la pela primeira vez com o pipeline parado.

### Lab 5: Alcançar o Service

```bash
kubectl apply -f manifests/50-pod-testador.yaml
kubectl -n campanhas logs testador-de-dns
kubectl -n campanhas port-forward svc/servico-de-consulta 18080:80
```

Saída esperada: o HTML de boas vindas do nginx no log do testador, e código 200
ao acessar `http://127.0.0.1:18080/` com o `port-forward` de pé.

O testador é um manifesto e não um `kubectl run` de uma linha por um motivo
concreto: o namespace aplica o perfil `restricted`, e o Pod padrão que o
`kubectl run` monta não o satisfaz.

### Lab 6: Escalar, quebrar o rollout e desfazer

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

Este é o laboratório mais importante da lista. O serviço não caiu, porque o
rollout só derruba um Pod antigo depois que o novo fica pronto, e o novo nunca
ficou. É o mecanismo que transforma um deploy errado em incidente sem impacto.

Desfazendo:

```bash
kubectl -n campanhas rollout undo deploy/servico-de-consulta
```

Leia o aviso que aparece. Ele diz que a anotação de última configuração aplicada
não é atualizada, e isso tem consequência: num fluxo em que o Git é a fonte da
verdade, o `undo` conserta o cluster e deixa o repositório errado. O próximo
`apply` traz a imagem quebrada de volta. O conserto real é reverter o commit.

### Lab 7: Derrubar o cluster

```bash
kind delete cluster --name mentoria-dados
```

Saída esperada: `Deleting cluster "mentoria-dados"` seguido de `Deleted nodes`.

## 15. Exercícios e entregáveis

**Exercício 1: Escolha de controller**

Objetivo: escolher o controller pela natureza da carga.

Contexto: cinco cargas do projeto de campanhas.

- Um serviço de query que responde ao painel.
- A transformação diária, que roda e termina.
- Um agente de coleta de métrica que precisa existir em todo node.
- Um broker de mensagem com disco próprio por réplica.
- Uma carga de reprocessamento que roda uma vez, sob demanda.

Entregável: tabela com o controller escolhido por carga, a justificativa em uma
frase, e o que quebraria com a escolha errada.

**Exercício 2: Recursos e QoS**

Objetivo: prever comportamento a partir do manifesto.

Contexto: os manifestos do laboratório.

Entregável: para cada carga, a classe de QoS resultante e por quê; depois, a
alteração necessária para o `servico-de-consulta` virar `Guaranteed`, aplicada e
confirmada com `kubectl get pods -o custom-columns`. Diga também o que essa
mudança custa.

**Exercício 3: Ler a falha**

Objetivo: diagnosticar pela assinatura, não por tentativa.

Contexto: crie três falhas de propósito no cluster do laboratório.

1. Um Pod que pede mais memória do que qualquer node tem.
2. Um Pod com uma imagem que não existe.
3. Um Deployment cujo Service não encontra nenhum Pod.

Entregável: para cada uma, o `STATUS` observado, o comando que revelou a causa e
a correção. O terceiro caso não gera erro no Deployment, e descobrir isso é o
exercício.

**Exercício 4: Do Airflow para o cluster**

Objetivo: ligar o que você já sabe ao que acabou de aprender.

Contexto: uma DAG com três tasks que hoje compartilham o mesmo ambiente e têm
dependências conflitantes.

Entregável: a descrição de como cada task viraria um Pod, com imagem, recursos e
seletor de node propostos, mais uma observação sobre o que **não** melhora com a
mudança.

## 16. Mini-desafio com solução

**Enunciado**

A transformação diária passou a falhar de forma intermitente. Nos dias de maior
volume ela termina com `OOMKilled`; nos demais, funciona. O time aumentou o
limite de memória e o problema diminuiu, mas não sumiu, e o custo do cluster
subiu porque a reserva foi aplicada a todas as execuções.

Proponha uma solução e explique por que ela é melhor do que aumentar o limite.

**Dicas**

- `requests` e `limits` fazem coisas diferentes, e só um deles reserva
  capacidade.
- Existe mais de uma forma de dar mais memória a uma tarefa, e uma delas não
  exige recriar o Pod.
- A pergunta "quanto ela realmente usa" ainda não foi respondida por ninguém.

**Gabarito comentado**

Primeiro, medir. Ninguém sabe o consumo real, e todas as decisões até agora
foram palpite. Sem a curva de uso por execução, qualquer número novo é outro
palpite mais caro.

Segundo, separar `requests` de `limits`. O que subiu o custo foi mexer nos dois
juntos: o `requests` é o que reserva capacidade em todo dia, inclusive nos dias
pequenos. Manter o `requests` no consumo típico e o `limits` no pico absorve o
dia atípico sem reservar para o dia normal. O custo disso é a classe de QoS, que
deixa de ser `Guaranteed`, e portanto a tarefa passa a ser candidata a despejo
antes das que reservam.

Terceiro, considerar o redimensionamento em execução, estável desde o 1.35. Para
uma tarefa longa que aperta no meio, ajustar sem recriar evita perder o trabalho
já feito.

Quarto, olhar a causa. `OOMKilled` proporcional ao volume quase sempre significa
que o processo carrega o conjunto inteiro na memória. Processar em blocos resolve
o problema em vez de administrá-lo, e é a única alternativa que não fica mais
cara conforme o dado cresce.

**Interpretação**

A resposta fraca escolhe um número novo. A resposta boa mede antes, separa
`requests` de `limits` com intenção, e reconhece que aumentar limite é comprar
tempo. Quem chegou no quarto ponto entendeu que o Kubernetes estava reportando o
sintoma de um problema de código.

## 17. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Estado desejado | Trata o cluster com comandos imperativos | Explica reconciliação | Diagnostica um problema pelo desvio entre real e desejado |
| Pod e workload | Cria Pod solto | Escolhe o controller certo | Justifica pela natureza da carga e prevê o que quebra |
| Recursos e QoS | Copia valores de exemplo | Define requests e limits com intenção | Prevê a classe de QoS e o comportamento sob pressão |
| Rede | Confunde Service com Deployment | Entende seletor e endpoints | Diagnostica Service sem endpoint por erro de label |
| Segurança | Deixa tudo como veio | Aplica securityContext e entende PSA | Planeja a migração de baseline para restricted |
| Diagnóstico | Tenta e erra | Lê a assinatura e vai à causa | Sabe quando o log da aplicação não vai ter nada |
| Ligação com dados | Vê Kubernetes como assunto de infra | Liga ao executor do Airflow | Sabe o que o cluster não resolve e continua no orquestrador |

## 18. Erros comuns e como corrigir

**Pending**

Sintoma: o Pod fica em `Pending` sem sair do lugar.

Causa: nenhum node tem recurso suficiente, ou nenhum node satisfaz o seletor, a
afinidade ou a tolerância declarada.

Correção: `kubectl describe pod` e ler os eventos, que dizem qual filtro
eliminou cada node. Ajustar `requests`, o seletor, ou acrescentar capacidade.

**CrashLoopBackOff**

Sintoma: o container sobe e morre em laço, e o intervalo entre tentativas cresce.

Causa: o processo termina logo depois de iniciar. Falta de configuração e
permissão insuficiente são as causas mais comuns.

Correção: `kubectl logs <pod> --previous`, que lê o container que já morreu. Sem
o `--previous` você lê o container atual, que ainda não escreveu nada.

Foi assim que o próprio laboratório foi corrigido: a primeira versão usava a
imagem oficial do nginx com todas as capacidades removidas, e o log anterior
mostrou `chown(...) failed (1: Operation not permitted)`.

**OOMKilled**

Sintoma: `STATUS OOMKilled` e código de saída 137.

Causa: o processo passou do limite de memória e foi morto pelo kernel.

Correção: medir o consumo real antes de mexer no número. Depois separar
`requests` de `limits`, e investigar se o processo carrega tudo em memória.

Não procure erro no log da aplicação. Ela foi morta com `SIGKILL` e não teve
chance de escrever nada.

**ImagePullBackOff**

Sintoma: o Pod não sai do lugar e a imagem nunca chega.

Causa: tag inexistente, nome errado, ou falta de credencial no registro privado.

Correção: conferir a tag e o registro; se for privado, conferir o
`imagePullSecrets`. No Lab 6 essa falha é provocada de propósito, e o ponto é
que os Pods antigos continuam servindo.

**Service sem endpoint**

Sintoma: conexão recusada, sem nenhum erro no Deployment nem nos Pods.

Causa: o seletor do Service não casa com os labels dos Pods, ou nenhum Pod está
pronto pela `readinessProbe`.

Correção: `kubectl get endpoints <service>`. Lista vazia confirma o diagnóstico.

**O rollback conserta o cluster e deixa o Git errado**

Sintoma: você desfaz um deploy ruim, e ele volta na próxima sincronização.

Causa: `kubectl rollout undo` altera o cluster e não altera o repositório. O
próprio comando avisa que a anotação de última configuração aplicada não é
atualizada.

Correção: reverter o commit. Num fluxo em que o Git é a fonte da verdade, o
`undo` serve para parar o sangramento, não para consertar.

**O apply da pasta falha em cluster novo**

Sintoma: `namespaces "campanhas" not found` em vários arquivos de uma vez.

Causa: os objetos referenciam um namespace que está sendo criado no mesmo
comando, e a ordem não é garantida.

Correção: aplicar o namespace primeiro, como faz o Lab 1. O mesmo vale para
`--dry-run=server`, que falha em cascata porque nada é realmente criado.

## 19. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 2 e 3. O terceiro é o que mais se parece com o trabalho real.

**O que estudar em seguida, dentro da trilha**

O módulo de infraestrutura como código, que responde como esse cluster nasce sem
ninguém digitar comando. Depois, revisite o módulo de Airflow: o
`KubernetesPodOperator` e o executor que cria um Pod por task passam a fazer
sentido completo agora.

**O que aprofundar por conta**

Empacotamento e entrega. Helm e Kustomize resolvem o mesmo problema de formas
diferentes, e entrega baseada em Git fecha o ciclo. O ganho que mais aparece é
revisão por pull request e rollback por commit.

**O que não perseguir agora**

Operar o control plane, ajustar rede do cluster e escrever operator. É trabalho
de plataforma, e você precisa primeiro ser um bom usuário do cluster. A leitura
de manifesto e o diagnóstico de falha valem mais no seu dia a dia do que
qualquer detalhe do etcd.

## 20. Glossário

| Termo | Significado |
|---|---|
| ConfigMap | Objeto que guarda parâmetro não sensível |
| Control plane | Conjunto de componentes que decide o que roda onde |
| DaemonSet | Controller que mantém um Pod por node |
| Deployment | Controller de aplicação sem estado, com rollout e rollback |
| Estado desejado | O que você declara que deve existir |
| Job | Controller de carga que executa até concluir |
| kubelet | Agente do node que sobe e vigia containers |
| limits | Teto rígido de recurso para o container |
| Namespace | Divisão lógica de objetos dentro do cluster |
| Node | Máquina que executa cargas |
| OOMKilled | Estado do container morto pelo kernel por estourar a memória |
| Pod | Unidade de execução, um ou mais containers que vivem juntos |
| Pod Security Admission | Controlador que recusa Pod fora do perfil do namespace |
| Probe | Verificação periódica de prontidão ou de vida do container |
| QoS | Classe derivada de requests e limits que decide a ordem de despejo |
| RBAC | Controle de permissão por verbo e recurso |
| Reconciliação | Laço que aproxima o estado real do desejado |
| requests | Recurso que o scheduler reserva para o container |
| Secret | Objeto que guarda credencial, codificado e não criptografado |
| Service | Nome e endereço estáveis para um conjunto de Pods |
| ServiceAccount | Identidade de um Pod dentro do cluster |
| StatefulSet | Controller com identidade e disco estáveis por réplica |
| Taint e toleration | Mecanismo pelo qual um node repele Pods que não o toleram |

## Referências

Documentação oficial do Kubernetes, consultada em 2026-07-31:

- Versões e suporte: https://kubernetes.io/releases/
- Sidecar containers: https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/
- Pod Security Admission: https://kubernetes.io/docs/concepts/security/pod-security-admission/
- Redimensionar recursos do container: https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/

Outras fontes oficiais, consultadas em 2026-07-31:

- Repositório do Ingress NGINX, com o aviso de arquivamento: https://github.com/kubernetes/ingress-nginx
- Referência do KubernetesPodOperator: https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_api/airflow/providers/cncf/kubernetes/operators/pod/index.html
- Projeto kind: https://kind.sigs.k8s.io/

## Fontes verificadas (2026-07-31)

- O sidecar nativo está ativo por padrão desde o Kubernetes 1.29 e passou a
  estável no 1.33. A sintaxe é um init container com `restartPolicy: Always`.
  https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/
- O Pod Security Admission é estável desde o Kubernetes 1.25 e substituiu o
  PodSecurityPolicy. Os níveis são `privileged`, `baseline` e `restricted`, os
  modos são `enforce`, `audit` e `warn`, e a configuração é por label no formato
  `pod-security.kubernetes.io/<MODO>: <NÍVEL>`.
  https://kubernetes.io/docs/concepts/security/pod-security-admission/
- O redimensionamento de CPU e memória de Pod em execução é estável desde o
  Kubernetes 1.35.
  https://kubernetes.io/docs/tasks/configure-pod-container/resize-container-resources/
- A versão mais recente do Kubernetes em 2026-07-31 é a 1.36.2, de 2026-06-09, e
  as versões com suporte são 1.34, 1.35 e 1.36. https://kubernetes.io/releases/
- O repositório do Ingress NGINX foi arquivado em 24 de março de 2026, está em
  modo somente leitura, e o próprio projeto recomenda que quem ainda não o usa
  escolha uma implementação da Gateway API em vez dele.
  https://github.com/kubernetes/ingress-nginx
- No `KubernetesPodOperator`, o parâmetro `container_resources` espera
  `kubernetes.client.models.V1ResourceRequirements`, e `on_finish_action`
  substitui o antigo `is_delete_operator_pod`, aceitando `delete_pod`,
  `delete_succeeded_pod`, `keep_pod` e `delete_active_pod`. O bloco Python da
  seção 13 foi conferido contra essa referência e não foi executado.
  https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/_api/airflow/providers/cncf/kubernetes/operators/pod/index.html
- Todas as saídas de laboratório citadas nesta apostila foram capturadas em
  execução real num cluster kind v0.32.0 com Kubernetes v1.36.1, kubectl v1.36.3
  e containerd 2.3.1, em 2026-07-31. Isso inclui a reconciliação do Pod apagado,
  o log do Job com ConfigMap injetado, o `OOMKilled` com código 137, as classes
  de QoS, o `ImagePullBackOff` convivendo com os Pods antigos em `Running` e o
  rollback restaurando a imagem. O registro completo, com comando e nível, está
  em `lab.json`.
- A falha de `chown` citada na seção 12 foi observada de verdade durante a
  construção deste laboratório, na versão que usava a imagem oficial do nginx com
  todas as capacidades removidas.
