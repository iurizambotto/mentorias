---
title: "Apostila, cloud para dados: o que muda quando o dado sai da sua maquina"
date: 2026-07-31
type: apostila
status: draft
project: zambotto-mentoria
tags: [engenharia_de_dados, cloud]
---

# Apostila, cloud para dados: o que muda quando o dado sai da sua máquina

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

## Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O que a nuvem realmente muda](#3-o-que-a-nuvem-realmente-muda)
- [4. Modelos de serviço e responsabilidade compartilhada](#4-modelos-de-serviço-e-responsabilidade-compartilhada)
- [5. As quatro primitivas](#5-as-quatro-primitivas)
- [6. Armazenamento de objetos e o custo de esquecer a classe](#6-armazenamento-de-objetos-e-o-custo-de-esquecer-a-classe)
- [7. Compute, do controle total ao serverless](#7-compute-do-controle-total-ao-serverless)
- [8. O destino analítico](#8-o-destino-analítico)
- [9. Identidade, o novo perímetro](#9-identidade-o-novo-perímetro)
- [10. Rede, a VPC](#10-rede-a-vpc)
- [11. FinOps, o custo é decisão de arquitetura](#11-finops-o-custo-é-decisão-de-arquitetura)
- [12. O mapa entre provedores](#12-o-mapa-entre-provedores)
- [13. Mão na massa sem gastar](#13-mão-na-massa-sem-gastar)
- [14. Exercícios e entregáveis](#14-exercícios-e-entregáveis)
- [15. Mini-desafio com solução](#15-mini-desafio-com-solução)
- [16. Rubrica de validação da aprendizagem](#16-rubrica-de-validação-da-aprendizagem)
- [17. Erros comuns e como corrigir](#17-erros-comuns-e-como-corrigir)
- [18. Plano de continuidade](#18-plano-de-continuidade)
- [19. Glossário](#19-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

## 0. Como usar esta apostila

**Leitura linear.** As seções 3 a 5 montam o vocabulário. Da 6 à 11 cada seção
trata de uma decisão que você vai tomar de verdade. A 12 é consulta, não
leitura.

**Revisão pontual.** Se você já trabalha em nuvem e veio atrás de um assunto,
vá direto: classes de armazenamento na 6, IAM na 9, custo na 11.

**Pré-requisitos.** Os módulos de object storage, particionamento e formatos de
tabela. Este módulo assume que você já sabe o que é um data lake e por que a
chave de partição decide o custo da query. Aqui a pergunta é outra: o que muda
quando isso tudo roda na infraestrutura de outra pessoa.

**Este módulo não tem laboratório.** Subir recurso de verdade custa dinheiro e
exige credencial, e a trilha não pede que você abra conta em nuvem. O que dá
para provar sem conta está provado: os blocos de código desta apostila passam
por `scripts/verificar_blocos.py`, que confere sintaxe de SQL, de política IAM e
de comando da AWS CLI sem tocar a rede. Nível 2 da escada de verificação, e a
apostila diz onde ele para.

**Este módulo é um mapa, não um destino.** Quase todo assunto tratado aqui tem
dono em outro módulo da trilha. A seção diz quem é o dono e trata apenas do
recorte de nuvem.

## 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** o que a nuvem troca em relação ao servidor próprio, em termos de
   custo e de risco, sem cair em "é mais barato".
2. **Situar** um serviço no espectro IaaS, PaaS e SaaS, e dizer o que sobra para
   você em cada ponto do espectro.
3. **Escolher** a classe de armazenamento de um conjunto de dados a partir do
   padrão de acesso, e prever o que a escolha errada custa.
4. **Escrever** uma política IAM de menor privilégio para um caso concreto de
   leitura de data lake.
5. **Traduzir** um serviço entre AWS, GCP e Azure quando ler uma vaga, uma
   arquitetura ou um artigo.
6. **Identificar** as três ou quatro decisões que respondem pela maior parte da
   fatura de um pipeline de dados.

## 2. Contexto de negócio

A startup fictícia de marketing e e-commerce da trilha chegou até aqui rodando
tudo em Docker na máquina de quem desenvolve: MinIO fazendo o papel do object
storage, Trino consultando, Airflow orquestrando, Kafka transportando evento e
dbt transformando.

Isso funcionou para aprender e não funciona para operar. Três fatos empurram a
mudança:

1. O volume de eventos de campanha cresceu, e a máquina que roda tudo é a mesma
   que alguém usa para trabalhar.
2. O relatório precisa existir quando quem trabalha está dormindo.
3. Se o notebook morrer, o histórico morre junto.

A pergunta deste módulo é: **o que exatamente estamos alugando, o que continua
sendo nossa responsabilidade, e onde o dinheiro vai embora.**

O que este módulo acrescenta ao projeto:

| Camada | Local, até aqui | Na nuvem |
|---|---|---|
| Object storage | MinIO em container | S3, Cloud Storage ou Blob |
| Query engine | Trino em container | Athena, BigQuery ou Redshift |
| Orquestração | Airflow em container | Airflow gerenciado |
| Transformação | dbt na sua máquina | o mesmo dbt, chamado pelo orquestrador |
| Responsabilidade por backup, disco e rede | sua | dividida, e a divisão tem regra |

## 3. O que a nuvem realmente muda

### 3.1 A troca de investimento por consumo

**O que é**

No servidor próprio, você compra capacidade antes de precisar dela e paga por
ela parada. Na nuvem, você aluga capacidade e paga pelo que consome.

**Como funciona na prática**

A consequência prática não é o preço, é **quando** você decide. Comprar servidor
obriga a acertar a previsão de carga com meses de antecedência. Alugar permite
errar a previsão e corrigir no mesmo dia.

**O equívoco comum**

Que nuvem é mais barata. Não é, por unidade de recurso. Um servidor próprio bem
utilizado, com carga estável e previsível, costuma sair mais barato por hora de
CPU. O que a nuvem vende é elasticidade e a eliminação do risco de errar a
compra, e isso tem preço.

Quem migra carga estável esperando economia se decepciona. Quem migra carga
irregular esperando não decidir com antecedência acerta.

### 3.2 Região e zona de disponibilidade

**O que é**

Uma região é uma área geográfica separada. Dentro de cada região existem várias
zonas de disponibilidade, que são locais isolados entre si.

A AWS declara hoje 39 regiões lançadas e 123 zonas de disponibilidade, com cada
região tendo pelo menos três zonas independentes e fisicamente separadas.

**Como funciona na prática**

Você escolhe a região por três motivos, nesta ordem de frequência: onde o dado
pode legalmente ficar, onde estão seus usuários, e o preço, que varia por região.

Distribuir a carga entre zonas protege da falha de um local dentro da região.
Distribuir entre regiões protege da falha da região inteira, e custa muito mais.

**O equívoco comum**

Achar que a nuvem replica tudo sozinha. A documentação da AWS é explícita: as
regiões são isoladas umas das outras e os recursos **não são replicados
automaticamente** entre elas. Quem não configurou a replicação não tem
replicação, e descobre isso no pior dia possível.

**Como inspecionar**

Ao listar recursos no console ou na CLI, você vê apenas o que existe na região
selecionada. Recurso que "sumiu" quase sempre está em outra região.

## 4. Modelos de serviço e responsabilidade compartilhada

### 4.1 O espectro IaaS, PaaS e SaaS

**O que é**

Os três nomes descrevem quanto da pilha o provedor opera por você.

| Modelo | Você opera | O provedor opera | Exemplo em dados |
|---|---|---|---|
| IaaS | Sistema operacional, runtime e aplicação | Hardware, rede e virtualização | Uma VM rodando seu Spark |
| PaaS | Apenas sua aplicação e seus dados | A plataforma inteira | Um data warehouse gerenciado |
| SaaS | Apenas a configuração e o uso | Tudo | Uma ferramenta de BI |

**O equívoco comum**

Ler o espectro como uma escada de qualidade, em que o mais gerenciado é sempre
melhor. É uma escada de **troca**: quanto menos você opera, menos você controla
e menos consegue prever o custo em carga atípica.

### 4.2 O que continua sendo seu

**O que é**

O modelo de responsabilidade compartilhada divide a segurança em duas partes. A
AWS descreve a sua como "segurança **da** nuvem" e a sua parte como "segurança
**na** nuvem".

| Lado | Do que responde |
|---|---|
| Provedor | Infraestrutura que roda os serviços: hardware, software, rede, instalações, sistema operacional do hospedeiro e camada de virtualização |
| Você | Sistema operacional convidado e seus patches, aplicação instalada, configuração de security group, gestão e criptografia dos dados, permissões de IAM |

**O equívoco comum**

Ler "gerenciado" como "seguro". O provedor garante que o serviço funciona e que
o data center é protegido. Bucket aberto para a internet, chave de acesso
commitada e permissão ampla demais são responsabilidade sua, e são a origem da
maioria dos vazamentos noticiados.

A própria documentação registra que a divisão varia por serviço: um serviço de
infraestrutura exige mais configuração sua, e um serviço abstrato transfere mais
operação ao provedor.

## 5. As quatro primitivas

Quase todo serviço de nuvem é combinação de quatro coisas. Entender as quatro
destrava o catálogo inteiro, que tem centenas de nomes.

| Primitiva | O que resolve | Onde aparece em dados |
|---|---|---|
| Compute | Executar código | Ingestão, transformação, query |
| Storage | Guardar bytes | Data lake, warehouse, backup |
| Rede | Ligar e isolar | Acesso privado ao lake, saída de dados |
| Identidade | Dizer quem pode o quê | Todo o resto |

A ordem não é acidental. Identidade vem por último na lista e primeiro na
consequência: um erro de compute derruba um job, e um erro de identidade
vaza a base inteira.

## 6. Armazenamento de objetos e o custo de esquecer a classe

O conceito de object storage tem dono na trilha, que é o módulo de object
storage com MinIO. Aqui tratamos só do que é específico de nuvem: as classes de
armazenamento e o que elas cobram.

### 6.1 Durabilidade não é o problema

**O que é**

A AWS declara durabilidade de 99,999999999 por cento, os onze noves, para todas
as classes do S3 exceto a Reduced Redundancy Storage, que fica em 99,99 por
cento e a própria AWS recomenda não usar.

**O equívoco comum**

Confundir durabilidade com disponibilidade. Durabilidade é a chance de o objeto
continuar existindo. Disponibilidade é a chance de você conseguir lê-lo agora.
São números diferentes e a diferença importa: a S3 One Zone-IA tem os mesmos
onze noves de durabilidade da Standard, e disponibilidade projetada de 99,5 por
cento contra 99,99 por cento, porque vive em uma zona só.

E há um detalhe que a palavra durabilidade esconde: nenhuma classe protege
contra você apagar o objeto. Isso é versionamento e política de retenção, não
durabilidade.

### 6.2 A tabela que decide a fatura

**Como funciona na prática**

| Classe | Disponibilidade projetada | Zonas | Duração mínima | Tamanho mínimo faturável |
|---|---|---|---|---|
| S3 Standard | 99,99% | 3 ou mais | nenhuma | nenhum |
| S3 Intelligent-Tiering | 99,9% | 3 ou mais | nenhuma | nenhum |
| S3 Standard-IA | 99,9% | 3 ou mais | 30 dias | 128 KB |
| S3 One Zone-IA | 99,5% | 1 | 30 dias | 128 KB |
| S3 Glacier Instant Retrieval | 99,9% | 3 ou mais | 90 dias | 128 KB |
| S3 Glacier Flexible Retrieval | 99,99% após restaurar | 3 ou mais | 90 dias | sem mínimo declarado |
| S3 Glacier Deep Archive | 99,99% após restaurar | 3 ou mais | 180 dias | sem mínimo declarado |

Duas colunas fazem mais estrago do que o preço por gigabyte:

**A duração mínima.** Objeto movido para Standard-IA e apagado em 5 dias é
cobrado por 30. Em Deep Archive, por 180. Uma política de ciclo de vida mal
calibrada em cima de dado que gira rápido aumenta a fatura em vez de reduzir.

**O tamanho mínimo faturável.** Objeto de 8 KB em Standard-IA é cobrado como
128 KB. Um lake com milhões de arquivos pequenos, que é exatamente o que uma
ingestão de streaming mal configurada produz, paga dezesseis vezes o que
armazena.

**O equívoco comum**

Mover o lake inteiro para uma classe fria para economizar. As classes de acesso
infrequente cobram taxa de recuperação por gigabyte. Dado que a análise lê toda
semana sai mais caro em Standard-IA do que em Standard.

A regra prática: a classe segue o padrão de acesso, não a idade do dado. Idade é
apenas um bom palpite sobre o padrão de acesso, e palpite erra.

### 6.3 Quando você não sabe o padrão de acesso

A classe Intelligent-Tiering existe para esse caso. Ela move o objeto entre
camadas conforme o acesso observado, cobra uma taxa de monitoramento por objeto
e não cobra taxa de recuperação.

Um detalhe muda a conta: objetos com menos de 128 KB não são monitorados e ficam
sempre na camada de acesso frequente. Num lake de arquivos pequenos, a taxa de
monitoramento é paga sem o benefício correspondente.

## 7. Compute, do controle total ao serverless

**O que é**

Compute na nuvem é um espectro, do controle total do servidor até a função que
escala a zero.

| Forma | Você gerencia | Bom para | Ruim para |
|---|---|---|---|
| Máquina virtual | Sistema operacional e tudo acima | Carga contínua, software exigente | Carga esporádica, paga parada |
| Container gerenciado | A imagem | Job de pipeline, serviço de médio porte | Escala a zero com latência sensível |
| Serverless | Apenas o código | Evento esporádico, cola entre serviços | Job longo, dependência pesada |

O conceito de orquestração de containers tem dono na trilha, que é o módulo de
Kubernetes. Aqui interessa uma decisão só: **quanto do seu pipeline precisa
estar de pé o tempo todo.**

**O equívoco comum**

Colocar transformação pesada em serverless porque "escala a zero". Serviços de
função têm limite de tempo de execução e de memória, e um job que ultrapassa o
limite falha no meio, sem estado. O que escala a zero bem é a cola: reagir a um
arquivo que chegou, disparar um pipeline, notificar.

## 8. O destino analítico

Os formatos de arquivo e os tipos de tabela têm dono na trilha, que é o módulo
de formatos e tipos de tabela. Aqui tratamos da escolha do destino.

### 8.1 Warehouse, lake e lakehouse

**O que é**

O data warehouse guarda o dado num formato proprietário, otimizado para query, e
cobra por armazenamento e processamento. O data lake guarda arquivo em formato
aberto no object storage, e alguma engine consulta por cima. O lakehouse é a
tentativa de ter o armazenamento barato do lake com a garantia transacional do
warehouse, através de formato de tabela aberto.

| Critério | Warehouse | Lake com engine | Lakehouse |
|---|---|---|---|
| Custo de armazenamento | maior | menor | menor |
| Facilidade de começar | maior | menor | média |
| Portabilidade do dado | menor | maior | maior |
| Garantia transacional | forte | fraca ou nenhuma | forte |

**O equívoco comum**

Escolher pela arquitetura de referência de um fornecedor. A pergunta que decide
é mais simples: quantos consumidores diferentes vão ler esse dado? Um consumidor
só, com equipe pequena, é caso de warehouse gerenciado, e a discussão de formato
aberto é prematura. Muitos consumidores com ferramentas diferentes é caso de
formato aberto, e aí o lakehouse paga o próprio custo de complexidade.

### 8.2 Query sobre o lake, e o modelo de cobrança que ela traz

**Como funciona na prática**

Serviços que consultam direto no object storage cobram por dado escaneado. Isso
muda o que significa uma query cara: não é a que demora, é a que lê muito.

A documentação de preço do Athena é explícita sobre a alavanca: comprimir o
arquivo e convertê-lo para um formato colunar como o Parquet permite que a
engine leia apenas a coluna relevante, e isso reduz o que você paga. A mesma
página usa a taxa de 5 dólares por terabyte como exemplo ilustrativo do cálculo.

Este é o ponto onde o módulo de particionamento e performance deixa de ser
teoria. Lá você aprendeu que a chave de partição decide quanto o engine lê. Aqui
a mesma decisão aparece na fatura, com nome e valor.

<!-- verificacao: nivel 2, sqlglot 30.14.0 dialetos hive e trino, scripts/verificar_blocos.py, 2026-07-31 -->

```sql
CREATE EXTERNAL TABLE raw.eventos_campanha (
    evento_id   BIGINT,
    campanha_id INT,
    impressoes  BIGINT,
    cliques     BIGINT,
    custo       DECIMAL(12, 2)
)
PARTITIONED BY (data_evento DATE)
STORED AS PARQUET
LOCATION 's3://empresa-data-lake/raw/eventos_campanha/'
```

E a query que aproveita a partição:

<!-- verificacao: nivel 2, sqlglot 30.14.0 dialeto trino, scripts/verificar_blocos.py, 2026-07-31 -->

```sql
SELECT canal, sum(custo) AS custo
FROM raw.eventos_campanha
WHERE data_evento BETWEEN DATE '2026-06-01' AND DATE '2026-06-30'
GROUP BY canal
```

Os dois blocos passaram no parse, o que prova a sintaxe e nada além. Não existe
tabela, não existe bucket e ninguém executou a query. Isso é o teto honesto de
um módulo sem laboratório em nuvem.

## 9. Identidade, o novo perímetro

### 9.1 Menor privilégio, escrito

**O que é**

Uma política concede o acesso estritamente necessário, e nada mais. A frase é
fácil e a prática é chata, porque escrever a permissão exata dá mais trabalho do
que conceder acesso amplo.

**Como funciona na prática**

Esta política permite ler apenas o prefixo `raw/` de um bucket, e listar apenas
esse prefixo:

<!-- verificacao: nivel 2, json valido com 2 statements, scripts/verificar_blocos.py, 2026-07-31 -->

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LerApenasOPrefixoRaw",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::empresa-data-lake/raw/*"
    },
    {
      "Sid": "ListarApenasOPrefixoRaw",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::empresa-data-lake",
      "Condition": {"StringLike": {"s3:prefix": ["raw/*"]}}
    }
  ]
}
```

Repare que são dois blocos com recursos diferentes. Ler objeto age sobre o
objeto, e o recurso termina em `/raw/*`. Listar age sobre o bucket, e o recurso é
o bucket, com a restrição de prefixo indo na condição. Confundir os dois é o
erro mais comum de quem escreve a primeira política, e o sintoma é uma listagem
que não funciona apesar de a leitura funcionar.

Este bloco foi validado como JSON. Isso prova a sintaxe, e não prova que a
política concede exatamente o que você quer: para isso é preciso testar contra a
conta, o que este módulo não faz.

**O equívoco comum**

Usar credencial de longa duração no código. Chave de acesso em repositório é a
origem clássica do incidente. A alternativa existe em toda nuvem: papel assumido
pelo serviço, sem chave escrita em lugar nenhum, e segredo em cofre gerenciado
quando a credencial for de terceiro.

### 9.2 Criptografia

Dado em repouso e em trânsito cifrado é o padrão, não a exceção. O que costuma
faltar é a decisão sobre a chave: gerenciada pelo provedor resolve a maior parte
dos casos, e chave própria só se justifica quando há exigência regulatória ou de
auditoria que a peça por escrito.

## 10. Rede, a VPC

**O que é**

A rede virtual privada isola seus recursos num espaço de endereços próprio, com
sub-redes públicas e privadas, e regras de firewall por recurso.

**Como funciona na prática**

Para engenharia de dados, três decisões cobrem quase tudo:

1. **Sub-rede privada para o que processa.** Quem transforma dado não precisa de
   endereço público. Se precisa sair para a internet, sai por um gateway
   controlado.
2. **Acesso privado ao object storage.** Um endpoint privado faz o tráfego para
   o storage não passar pela internet pública, o que ajuda em segurança e, em
   alguns casos, no custo de transferência.
3. **Regra de firewall por origem e porta.** A porta do banco aberta para o
   mundo é falha de configuração, e configuração é o seu lado do modelo de
   responsabilidade compartilhada.

**O equívoco comum**

Tratar rede como assunto de outra equipe. A conta de transferência de dados e a
lentidão inexplicável de um job frequentemente moram aqui, e quem lê a fatura é
quem toca o pipeline.

## 11. FinOps, o custo é decisão de arquitetura

### 11.1 O que responde pela fatura

**O que é**

Numa carga de dados, a maior parte do custo costuma vir de poucas decisões:

| Decisão | Efeito na fatura |
|---|---|
| Formato e particionamento do dado | Define quanto a query lê, e a query é cobrada por leitura |
| Classe de armazenamento e ciclo de vida | Define o preço por gigabyte e as multas de duração mínima |
| Recurso ligado sem uso | Paga hora parada, principalmente cluster e VM |
| Transferência de dados entre regiões e para fora | Cobrada por gigabyte, e não aparece até chegar |

O primeiro item é o mais importante e o menos citado. Melhorar o formato do dado
reduz o custo de toda query futura, e nenhuma negociação comercial faz isso.

### 11.2 Os três modelos de preço

| Modelo | Como funciona | Bom para |
|---|---|---|
| Sob demanda | Paga pelo uso, sem compromisso | Carga nova ou irregular |
| Compromisso de uso | Desconto em troca de compromisso de prazo | Baseline previsível e medida |
| Capacidade interrompível | Desconto grande, o provedor pode retomar o recurso | Job tolerante a falha e reinício |

**O equívoco comum**

Assinar compromisso de uso antes de ter medida. O desconto é real e o
compromisso também: você paga o prazo inteiro mesmo que a carga caia. A ordem
certa é medir por alguns meses, achar o piso de consumo, e comprometer apenas o
piso.

### 11.3 O que fazer antes de otimizar

Sem rótulo de custo por time e por projeto, otimização vira palpite. Rotular
recurso e ligar alerta de orçamento custa pouco tempo e é o que transforma "a
fatura subiu" em "a fatura subiu por causa disto".

## 12. O mapa entre provedores

Três provedores dominam a infraestrutura de nuvem. Segundo dados da Synergy
Research Group para o primeiro trimestre de 2026, a AWS tinha 28 por cento do
mercado, a Microsoft Azure 21 por cento e o Google Cloud 14 por cento, num
mercado de 129 bilhões de dólares no trimestre.

O mesmo conceito muda de nome em cada nuvem. Esta tabela existe para você ler
uma arquitetura ou uma vaga sem travar no nome:

| Conceito | AWS | GCP | Azure |
|---|---|---|---|
| Object storage | S3 | Cloud Storage | Blob Storage |
| Data warehouse | Redshift | BigQuery | Synapse |
| Query sobre o lake | Athena | BigQuery | Synapse Serverless |
| Streaming gerenciado | Kinesis e MSK | Pub/Sub | Event Hubs |
| ETL gerenciado | Glue | Dataflow | Data Factory |
| Spark gerenciado | EMR | Dataproc | Synapse Spark |
| Airflow gerenciado | MWAA | Cloud Composer | Data Factory Managed Airflow |
| Função serverless | Lambda | Cloud Functions | Azure Functions |
| Container gerenciado | ECS e EKS | GKE | AKS |
| Identidade | IAM | IAM | Entra ID |
| Chaves | KMS | Cloud KMS | Key Vault |

**O equívoco comum**

Escolher provedor pelo catálogo. Os três atendem engenharia de dados com folga.
O que decide na prática é onde a empresa já está, qual contrato já existe, e
quem no time já sabe operar. Multi-nuvem evita dependência de fornecedor e
multiplica a complexidade operacional por dois ou três, o que raramente compensa
em time pequeno.

## 13. Mão na massa sem gastar

Você não precisa de conta para ler o que um comando faz. A AWS CLI interpreta o
comando localmente, e dois recursos dela permitem conferir a sintaxe sem
credencial e sem chamada de rede.

**O esqueleto do comando** mostra a estrutura de entrada de uma operação de API:

<!-- verificacao: nivel 2, AWS CLI 2.25.5, codigo 0 sem credencial e sem rede, scripts/verificar_blocos.py, 2026-07-31 -->

```bash
aws s3api create-bucket --generate-cli-skeleton
aws athena start-query-execution --generate-cli-skeleton
```

**O modo de ensaio** mostra o que aconteceria, sem acontecer:

<!-- verificacao: nivel 2, AWS CLI 2.25.5, codigo 0 sem credencial e sem rede, scripts/verificar_blocos.py, 2026-07-31 -->

```bash
aws s3 cp vendas.parquet s3://empresa-data-lake/raw/vendas/ --dryrun
```

A saída é a linha `(dryrun) upload: ...`, e nada foi enviado.

Uma diferença que confunde: o modo de ensaio existe nos comandos de alto nível
`aws s3`, e não em todos. O `aws s3 mb` não aceita a opção, e a forma
verificável dele é o esqueleto do `aws s3api create-bucket`.

Para conferir tudo de uma vez, no diretório do módulo:

<!-- verificacao: nivel 3, execucao real do proprio script, codigo 0 com 7 checagens, 2026-07-31 -->

```bash
python3 scripts/verificar_blocos.py
```

Saída esperada: sete linhas começando com `OK` e a linha final
`7 checagem(ns), todas em nivel 2`.

## 14. Exercícios e entregáveis

**Exercício 1: Classe de armazenamento por padrão de acesso**

Objetivo: escolher classe a partir do acesso, não da idade.

Contexto: quatro conjuntos do projeto de campanhas.

- Eventos crus do mês corrente, lidos várias vezes por dia pelo pipeline.
- Eventos crus de meses anteriores, lidos uma vez por mês no fechamento.
- Exportações para auditoria, lidas quase nunca, guardadas por sete anos.
- Arquivos de log de aplicação, milhões de objetos de poucos kilobytes cada.

Entregável: tabela com classe escolhida por conjunto, justificativa em uma
frase, e o que a escolha erraria se você decidisse apenas pela idade do dado.
O quarto item tem uma pegadinha, e ela está na seção 6.

**Exercício 2: Política de menor privilégio**

Objetivo: escrever permissão exata, não permissão que funciona.

Contexto: uma ferramenta de BI precisa ler apenas o prefixo `curated/` do bucket
do lake, e precisa listar esse prefixo para navegar.

Entregável: a política em JSON, validada com `python3 -m json.tool`, mais uma
frase explicando por que os dois blocos apontam para recursos diferentes.

**Exercício 3: De onde vem a fatura**

Objetivo: ligar decisão técnica a linha de custo.

Contexto: um pipeline que lê 2 TB de CSV não particionado por execução, roda de
hora em hora, e alimenta um painel consultado três vezes por dia.

Entregável: lista das três mudanças que mais reduziriam o custo, em ordem de
impacto, com a justificativa de cada uma. Diga também o que você mediria antes
de assinar qualquer compromisso de uso.

**Exercício 4: Tradução entre nuvens**

Objetivo: ler arquitetura sem travar no nome.

Contexto: uma descrição de vaga pede experiência com S3, Glue, Athena e MWAA.

Entregável: a mesma arquitetura escrita com os serviços equivalentes do GCP e do
Azure, mais uma observação sobre qual equivalência é a menos exata e por quê.

## 15. Mini-desafio com solução

**Enunciado**

O time decidiu levar o pipeline de campanhas para a nuvem. O volume é de cerca
de 50 GB novos por mês em eventos de campanha. O pipeline roda de hora em hora,
o painel é consultado algumas dezenas de vezes por dia, e a auditoria exige
guardar o dado cru por cinco anos.

Proponha a arquitetura mínima e diga, para cada escolha, o que ela custa e o que
ela deixa de fora.

**Dicas**

- Comece pela pergunta de negócio, não pelo catálogo de serviços.
- Cinco anos de retenção e acesso diário são requisitos diferentes sobre o mesmo
  dado, e isso sugere mais de uma classe de armazenamento.
- O maior custo recorrente de um pipeline de query sobre lake não costuma ser o
  armazenamento.

**Gabarito comentado**

Armazenamento em duas faixas. O mês corrente em classe padrão, porque o pipeline
lê todo dia. O histórico movido por política de ciclo de vida para uma classe de
acesso infrequente, que tem duração mínima de 30 dias, prazo compatível com dado
que só será relido no fechamento. Para os cinco anos de auditoria, uma cópia em
arquivamento profundo, cuja duração mínima de 180 dias não é problema para dado
que ninguém pretende ler.

Formato e particionamento antes de qualquer serviço. Converter para Parquet e
particionar por data de evento é a decisão que mais reduz custo, porque ela
reduz o que **toda** query futura lê. Fazer isso depois de escolher a engine é a
ordem errada, ainda que funcione.

Query sobre o lake, não warehouse dedicado. Com 50 GB por mês e algumas dezenas
de consultas por dia, um warehouse dedicado cobra capacidade parada. Cobrança
por dado escaneado combina melhor com esse perfil, e a conta muda se o número de
consultas crescer uma ordem de grandeza.

Orquestração gerenciada. O Airflow que você já conhece, sem o servidor para
manter de pé. É a troca típica: paga mais por hora e não paga o custo de operar.

Identidade desde o primeiro dia. Um papel para o pipeline com escrita apenas nos
prefixos que ele produz, um papel para o BI com leitura apenas do curado.
Deixar isso para depois significa nunca fazer.

**O que a solução deixa de fora, e isso faz parte da resposta**

Não há alta disponibilidade entre regiões. A perda de uma região inteira
interrompe o pipeline, e a decisão é consciente: o custo de duplicar não se
justifica para um painel de marketing. Escrever isso é parte do entregável,
porque risco não declarado é risco assumido sem querer.

Também não há estimativa de custo em reais. Preço varia por região e muda sem
aviso, e este material não cita valor que não pôde ser conferido na data. O
caminho certo é a calculadora oficial do provedor, com os seus números.

**Interpretação**

A resposta fraca lista serviços. A resposta boa liga cada serviço a um requisito
e diz o que ficou de fora. Quem escreveu o parágrafo sobre o que a solução não
cobre entendeu o que este módulo ensina.

## 16. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Trade-off da nuvem | Diz que nuvem é mais barata | Explica a troca entre investimento e consumo | Identifica quando o servidor próprio ainda ganha |
| Responsabilidade compartilhada | Assume que gerenciado é seguro | Sabe o que fica do seu lado | Aponta o próprio risco numa arquitetura concreta |
| Classe de armazenamento | Escolhe pela idade do dado | Escolhe pelo padrão de acesso | Antecipa duração mínima e tamanho mínimo faturável |
| IAM | Concede acesso amplo que funciona | Escreve menor privilégio correto | Explica a diferença entre recurso de objeto e de bucket |
| Custo | Trata custo como assunto financeiro | Liga decisão técnica a linha de fatura | Ordena as mudanças por impacto e diz o que mediria antes |
| Tradução entre nuvens | Trava fora da nuvem que conhece | Traduz os serviços principais | Aponta onde a equivalência é imperfeita |
| Honestidade técnica | Afirma número que não conferiu | Cita fonte e data | Declara explicitamente o que não foi verificado |

A última linha vale para todos os módulos, e é a que mais separa profissional de
entusiasta.

## 17. Erros comuns e como corrigir

**Recurso que sumiu**

Sintoma: o bucket ou a instância não aparece no console nem na listagem.

Causa: você está em outra região. Regiões são isoladas e não replicam nada
automaticamente.

Correção: conferir a região selecionada antes de qualquer outra hipótese.

**A fatura de armazenamento subiu depois de uma política de ciclo de vida**

Sintoma: mover dado para classe fria aumentou o custo.

Causa: duração mínima ou tamanho mínimo faturável. Dado que gira antes do prazo
paga o prazo inteiro, e arquivo pequeno paga como se tivesse 128 KB.

Correção: comparar o tempo de vida real do objeto com a duração mínima da
classe, e consolidar arquivos pequenos antes de mover.

**A listagem falha, mas a leitura funciona**

Sintoma: a aplicação lê o objeto quando recebe o caminho, e falha ao listar.

Causa: a política concedeu `s3:GetObject` no prefixo e esqueceu `s3:ListBucket`
no bucket. São recursos diferentes.

Correção: dois blocos na política, como na seção 9.

**A query custa caro e ninguém sabe por quê**

Sintoma: o valor da consulta ao lake não cai mesmo com filtros.

Causa: o filtro não é de partição, ou o dado está em formato de linha. A
cobrança é por dado escaneado, e o filtro em coluna comum não evita a leitura.

Correção: particionar pela coluna que aparece no filtro e converter para formato
colunar. O módulo de particionamento e performance é o dono deste assunto.

**Credencial no repositório**

Sintoma: chave de acesso encontrada num commit.

Causa: uso de credencial de longa duração em vez de papel assumido pelo serviço.

Correção: revogar a chave imediatamente, migrar para papel, e mover o que sobrar
para um cofre de segredos. Trocar depois de vazar é obrigatório; o histórico do
Git guarda o valor antigo para sempre.

## 18. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 1 e 3. Os dois cobram a mesma habilidade por ângulos
diferentes, que é ligar decisão técnica a consequência de custo.

**O que estudar em seguida, dentro da trilha**

O próximo módulo do bloco é infraestrutura como código, e ele responde à
pergunta que este deixa aberta: como esse ambiente nasce sem ninguém clicar em
console. Depois vêm processamento distribuído e Kubernetes, que tratam do
compute em escala.

Vale reler o módulo de particionamento e performance com a seção 11 desta
apostila na cabeça. O mesmo conteúdo lido depois de entender a cobrança por dado
escaneado tem outro peso.

**O que aprofundar por conta**

A calculadora de preço do seu provedor, com números do seu projeto. Uma hora
nela ensina mais sobre arquitetura de custo do que qualquer texto, inclusive
este.

**O que não perseguir agora**

Certificação. Ela cobra amplitude de catálogo, e você precisa de profundidade em
poucos serviços. Se for buscar uma, faça depois do capstone da trilha, não
antes.

## 19. Glossário

| Termo | Significado |
|---|---|
| Classe de armazenamento | Faixa de preço e desempenho de um objeto no object storage |
| Compromisso de uso | Desconto concedido em troca de compromisso de consumo por prazo |
| Disponibilidade | Probabilidade de conseguir acessar o recurso num dado momento |
| Duração mínima | Prazo pelo qual a classe cobra, mesmo que o objeto seja apagado antes |
| Durabilidade | Probabilidade de o objeto continuar existindo |
| Elasticidade | Capacidade de aumentar e reduzir recurso conforme a carga |
| Endpoint privado | Acesso a um serviço sem passar pela internet pública |
| IaaS | Modelo em que o provedor entrega infraestrutura e você opera o resto |
| IAM | Serviço que define quem pode fazer o quê sobre qual recurso |
| Lakehouse | Arquitetura que une o armazenamento do lake à garantia do warehouse |
| Menor privilégio | Conceder apenas o acesso estritamente necessário |
| PaaS | Modelo em que o provedor opera a plataforma e você cuida da aplicação |
| Região | Área geográfica isolada, com várias zonas de disponibilidade |
| Responsabilidade compartilhada | Divisão de segurança entre provedor e cliente |
| Serverless | Modelo em que você entrega código e não gerencia servidor |
| Tamanho mínimo faturável | Tamanho pelo qual a classe cobra, mesmo em objeto menor |
| VPC | Rede virtual isolada onde seus recursos vivem |
| Zona de disponibilidade | Local isolado dentro de uma região |

## Referências

Documentação oficial, consultada em 2026-07-31:

- Classes de armazenamento do Amazon S3: https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- Modelo de responsabilidade compartilhada da AWS: https://aws.amazon.com/compliance/shared-responsibility-model/
- Infraestrutura global da AWS: https://aws.amazon.com/about-aws/global-infrastructure/
- Regiões e zonas de disponibilidade: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
- Preço do Amazon Athena: https://aws.amazon.com/athena/pricing/
- Preço do Google BigQuery: https://cloud.google.com/bigquery/pricing
- Referência da AWS CLI: https://docs.aws.amazon.com/cli/latest/reference/

Dados de mercado, consultados em 2026-07-31:

- Participação de mercado de nuvem no primeiro trimestre de 2026, com atribuição à Synergy Research Group: https://www.cloudzero.com/blog/cloud-service-providers/

## Fontes verificadas (2026-07-31)

- A AWS declara 39 regiões lançadas e 123 zonas de disponibilidade, com cada
  região tendo pelo menos três zonas independentes e fisicamente separadas.
  https://aws.amazon.com/about-aws/global-infrastructure/
- Cada região é isolada das demais e os recursos não são replicados
  automaticamente entre regiões.
  https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html
- No modelo de responsabilidade compartilhada, a AWS responde pela infraestrutura
  que roda os serviços, incluindo hardware, software, rede, instalações, sistema
  operacional do hospedeiro e camada de virtualização; o cliente responde pelo
  sistema operacional convidado, aplicação, configuração de security group,
  gestão e criptografia dos dados e permissões de IAM.
  https://aws.amazon.com/compliance/shared-responsibility-model/
- Todas as classes do S3 citadas na seção 6 são projetadas para durabilidade de
  99,999999999 por cento, exceto a Reduced Redundancy Storage, projetada para
  99,99 por cento e não recomendada pela própria AWS.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- Disponibilidade projetada, zonas, duração mínima e tamanho mínimo faturável de
  cada classe são os da tabela comparativa da documentação: Standard 99,99 por
  cento sem mínimos; Standard-IA 99,9 por cento, 30 dias e 128 KB; One Zone-IA
  99,5 por cento em uma zona, 30 dias e 128 KB; Glacier Instant Retrieval 99,9
  por cento, 90 dias e 128 KB; Glacier Flexible Retrieval 90 dias; Glacier Deep
  Archive 180 dias.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- Objetos com menos de 128 KB não são monitorados pelo Intelligent-Tiering e
  ficam sempre na camada de acesso frequente.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- A página de preço do Athena afirma que comprimir o arquivo e convertê-lo para
  um formato colunar como o Parquet permite ler apenas a coluna relevante,
  reduzindo o valor pago, e usa 5 dólares por terabyte como taxa ilustrativa do
  exemplo de cálculo. O preço por região não foi conferido nesta data e por isso
  não é afirmado aqui. https://aws.amazon.com/athena/pricing/
- Participação de mercado no primeiro trimestre de 2026, atribuída à Synergy
  Research Group: AWS 28 por cento, Microsoft Azure 21 por cento e Google Cloud
  14 por cento, num mercado de 129 bilhões de dólares no trimestre. Este é um
  número de pesquisa de mercado, não de documentação de fornecedor.
  https://www.cloudzero.com/blog/cloud-service-providers/
- Os blocos de SQL, a política em JSON e os comandos da AWS CLI desta apostila
  foram verificados em nível 2 por `scripts/verificar_blocos.py`, com sqlglot
  30.14.0 nos dialetos hive e trino e AWS CLI 2.25.5 em modo esqueleto e em modo
  de ensaio, sem credencial e sem chamada de rede. As sete checagens passaram e o
  script saiu com código 0 em 2026-07-31. Nenhum recurso de nuvem foi criado, e
  nenhuma query foi executada.
