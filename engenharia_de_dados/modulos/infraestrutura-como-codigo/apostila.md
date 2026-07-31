---
title: "Apostila, infraestrutura como codigo para plataforma de dados"
date: 2026-07-31
type: apostila
status: draft
project: zambotto-mentoria
tags: [engenharia_de_dados, terraform]
---

# Apostila, infraestrutura como código para plataforma de dados

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

## Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. O problema do ambiente artesanal](#3-o-problema-do-ambiente-artesanal)
- [4. Os três princípios](#4-os-três-princípios)
- [5. O ecossistema, e o que cada ferramenta resolve](#5-o-ecossistema-e-o-que-cada-ferramenta-resolve)
- [6. Os blocos da linguagem](#6-os-blocos-da-linguagem)
- [7. State, o coração e o ponto de falha](#7-state-o-coração-e-o-ponto-de-falha)
- [8. Módulos e composição](#8-módulos-e-composição)
- [9. for_each e count, e por que a escolha importa](#9-for_each-e-count-e-por-que-a-escolha-importa)
- [10. Ambientes e raio de impacto](#10-ambientes-e-raio-de-impacto)
- [11. Segredo nunca entra no código](#11-segredo-nunca-entra-no-código)
- [12. Testes e a pirâmide que existe de verdade](#12-testes-e-a-pirâmide-que-existe-de-verdade)
- [13. O fluxo que tira o apply do terminal](#13-o-fluxo-que-tira-o-apply-do-terminal)
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

**Leitura linear.** As seções 3 e 4 explicam por que a prática existe. Da 6 à 11
cada seção trata de uma decisão concreta. A 12 e a 13 são sobre operar, e são as
que mais separam quem escreveu Terraform uma vez de quem mantém uma plataforma.

**Revisão pontual.** State na 7, `for_each` na 9, segredo na 11, diagnóstico na
18.

**Pré-requisitos.** O módulo de cloud para dados. Este material assume que você
já sabe o que é bucket, classe de armazenamento, IAM e região. Aqui a pergunta é
como isso nasce sem ninguém clicar.

**O teto deste módulo é o nível 2 da escada de verificação, e isso é decisão.**
`terraform plan` e `terraform apply` mudam infraestrutura de verdade e custam
dinheiro de verdade. Eles são do operador humano ou do pipeline, e não entram em
laboratório de estudo. O que o laboratório prova está declarado no `lab.json`, e
o que ele não prova também.

**Versões.** Verificado com Terraform v1.15.8, TFLint v0.64.0 e provider
`hashicorp/aws` 6.57.1, em 2026-07-31.

## 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Explicar** por que ambiente criado no console é dívida, em termos de risco e
   de tempo, sem recorrer a "é boa prática".
2. **Ler** um arquivo em HCL e dizer o que cada bloco faz.
3. **Escrever** um módulo com contrato claro: poucas variáveis, saídas úteis e
   validação declarada.
4. **Escolher** entre `for_each` e `count`, e prever o que acontece ao acrescentar
   um item no meio.
5. **Explicar** o que o state guarda, por que ele é sensível e o que o torna
   seguro.
6. **Ler** um plano de mudança e identificar o que vai ser destruído.
7. **Descrever** o fluxo em que ninguém aplica infraestrutura do próprio
   terminal, e por que isso não é burocracia.

## 2. Contexto de negócio

A startup fictícia de marketing e e-commerce decidiu levar a plataforma para a
nuvem, e alguém fez isso pelo console. Funcionou.

Três meses depois, o problema apareceu de três formas ao mesmo tempo:

1. Pediram um ambiente de homologação igual ao de produção, e ninguém sabe o que
   exatamente existe em produção.
2. A fatura tem um bucket que ninguém reconhece, e o console não diz quem criou
   nem por quê.
3. A pessoa que montou o ambiente saiu, e o conhecimento saiu com ela.

Nenhum dos três é problema de nuvem. Os três são problema de **procedência**: não
existe registro de qual decisão criou cada recurso.

A pergunta deste módulo é: **como transformar o ambiente em artefato revisável,
reproduzível e auditável, sem que a criação de infraestrutura dependa da memória
de alguém.**

O que este módulo acrescenta ao projeto:

| Aspecto | Console | Código versionado |
|---|---|---|
| Recriar o ambiente | de memória, com divergência | do repositório, igual |
| Saber quem mudou o quê | log de auditoria da nuvem, sem o porquê | histórico do Git, com a justificativa |
| Revisão antes da mudança | conversa, quando acontece | pull request, sempre |
| Diferença entre ambientes | descoberta ao quebrar | visível no diff |

## 3. O problema do ambiente artesanal

### 3.1 O que o clique custa

**O que é**

Criar recurso pelo console é rápido e não deixa rastro de intenção. O resultado é
um ambiente que existe e que ninguém consegue descrever.

**O equívoco comum**

Achar que o problema é a criação. O problema é a **segunda** criação. O console
resolve bem a primeira vez, e falha quando alguém precisa de um ambiente igual,
ou de entender por que dois ambientes diferem.

**Como inspecionar**

O teste é uma pergunta: se este ambiente for perdido hoje, quanto tempo até
existir um idêntico? Se a resposta envolve alguém lembrando de algo, o ambiente é
artesanal.

### 3.2 O repositório como descrição do ambiente

Quando o ambiente é código, o repositório para de ser documentação e passa a ser
a descrição real. A diferença é que documentação envelhece em silêncio, e código
que divergiu do real aparece na próxima execução.

Esse "aparecer" tem nome, e é o assunto da seção 7.

## 4. Os três princípios

**Declarativo**

Você descreve o resultado, não o caminho. Não existe "crie o bucket, depois ligue
o versionamento": existe um bucket com versionamento ligado, e a ferramenta
descobre a ordem.

**Idempotente**

Aplicar duas vezes o mesmo código não cria duas vezes o mesmo recurso. A segunda
execução compara e não faz nada. Isso é o que permite que o código seja executado
com segurança por um pipeline.

**Imutável**

Mudança relevante substitui o recurso em vez de alterar o que está vivo. É o
mesmo princípio do Pod do módulo de Kubernetes, e a consequência prática é a
mesma: você precisa saber quais mudanças provocam substituição.

**A consequência que junta os três**

Ambiente descartável deixa de ser risco e vira estratégia. Se recriar é
confiável, testar em ambiente separado passa a ser barato.

**O equívoco comum**

Ler "imutável" como garantia de segurança. Substituir um bucket significa perder
o conteúdo dele. O princípio descreve o comportamento da ferramenta, e não
promete que ele é inofensivo.

## 5. O ecossistema, e o que cada ferramenta resolve

**O que é**

Provisionar e configurar são camadas diferentes, e confundir as duas é a origem
de muita escolha errada.

| Ferramenta | Camada | Escopo |
|---|---|---|
| Terraform | provisionamento | multi-provedor, em linguagem própria |
| OpenTofu | provisionamento | fork do Terraform, sob licença MPL 2.0 |
| CloudFormation | provisionamento | um provedor só, integração profunda |
| Pulumi e CDK | provisionamento | em linguagem de programação de uso geral |
| Ansible | configuração | dentro da máquina, depois de ela existir |
| Crossplane | provisionamento | pela API do Kubernetes |

**Sobre a divisão do ecossistema**

O Terraform mudou de licença em 2023 e deixou de ser software livre no sentido
estrito. O OpenTofu nasceu como fork em resposta, e está sob a Mozilla Public
License 2.0.

A base de linguagem e de providers é comum, então migrar costuma ser direto. Como
os dois projetos evoluem em paralelo, a paridade não é permanente, e isso deve
entrar na decisão de quem começa um projeto novo hoje.

Esta apostila usa o Terraform porque é o que aparece com mais frequência em vaga
e em código existente. Quase tudo aqui vale para os dois.

**O que não conferi, e por isso não afirmo**

O deck da aula cita a data da aquisição da HashiCorp pela IBM, a versão exata em
que a licença mudou e o status do OpenTofu numa fundação. Não confirmei esses três
pontos em fonte oficial na data desta apostila, então eles não aparecem aqui como
fato. Se você for citá-los, confira antes.

## 6. Os blocos da linguagem

**O que é**

Poucos blocos cobrem a maior parte do código. O resto é composição.

| Bloco | Papel |
|---|---|
| `terraform` | Versão exigida, providers e backend |
| `provider` | Região e opções do alvo |
| `resource` | Recurso gerenciado, criado e destruído pela ferramenta |
| `data` | Consulta de algo que já existe, sem assumir a gestão |
| `variable` | Entrada parametrizada, com tipo e validação |
| `output` | Valor exportado, para outro módulo ou para o operador |
| `locals` | Expressão nomeada, para não repetir cálculo |

**Como funciona na prática**

O bloco `terraform` do módulo do laboratório fixa duas coisas que evitam surpresa:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8 e provider aws 6.57.1, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
```

A restrição `~> 6.0` permite atualização dentro da linha 6 e recusa a 7. Sem
isso, o lançamento de um provider novo muda a sua infraestrutura sem nenhum
commit no seu repositório.

**A diferença entre `resource` e `data`**

`resource` é o que você passa a gerenciar: a ferramenta cria e, se você remover
do código, ela destrói. `data` é leitura de algo que continua sendo de outra
pessoa. Confundir os dois é como confundir `ref` com `source` no dbt, e o efeito
é igualmente concreto: você assume a gestão de algo que não é seu.

**Validação como parte do contrato**

O módulo do laboratório recusa um valor errado antes de qualquer chamada de API:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
variable "dias_para_acesso_infrequente" {
  type    = number
  default = 90

  validation {
    condition     = var.dias_para_acesso_infrequente >= 30
    error_message = "A duracao minima da classe de acesso infrequente e de 30 dias."
  }
}
```

Aquele 30 não é opinião. É a duração mínima cobrada pela classe de acesso
infrequente, do módulo de cloud para dados. O bloco `validation` transforma
conhecimento de custo em erro que a ferramenta emite.

**Atenção a um limite real, que o laboratório mostra.** Esse `validation` **não**
é avaliado pelo `terraform validate`. Ele roda no `plan`. No Lab 6 você põe o
valor 10 ali, roda o `validate`, e recebe `Success`. A rede de proteção existe, e
não é essa ferramenta que a aciona.

## 7. State, o coração e o ponto de falha

### 7.1 O que o state é

**O que é**

O state é o mapa entre o seu código e os recursos reais. Ele guarda o
identificador de cada recurso e os atributos conhecidos da última execução.

Sem state, a ferramenta não sabe se o bucket declarado no código é aquele que
existe na nuvem, ou se deve criar outro.

**Como funciona na prática**

A comparação que a ferramenta faz é de três pontas: o código diz o desejado, o
state diz o que ela criou, e a nuvem diz o que existe agora. O plano é a
diferença entre os três.

**O equívoco comum**

Tratar o state como arquivo temporário. Perder o state não apaga a
infraestrutura: apaga o conhecimento de que ela é sua. O próximo plano propõe
criar tudo de novo, e o que existe fica órfão.

### 7.2 Backend remoto e trava

**O que é**

State em arquivo local não sobrevive à segunda pessoa do time. Backend remoto
guarda o state num lugar compartilhado e trava a execução concorrente.

A trava é o que impede dois `apply` simultâneos de corromperem o mapa. Sem ela, a
segunda execução escreve por cima do que a primeira ainda estava fazendo.

**Como funciona na prática**

No laboratório o bloco `backend` está comentado, e o comentário explica por quê:
o bucket de state precisa existir **antes** do código que o usa, então ele não
pode ser provisionado pelo mesmo código. Criar esse recurso à mão, uma única vez,
é uma das poucas exceções legítimas ao princípio deste módulo.

### 7.3 O state guarda segredo em texto claro

**O que é**

Este é o ponto que mais gera incidente. A documentação da ferramenta é explícita:
ao desenvolver localmente, o state é um arquivo em texto plano, e ele inclui
qualquer valor secreto definido na configuração.

As recomendações oficiais são quatro: guardar o state remotamente, criptografá-lo
em repouso, restringir quem acessa, e manter log de auditoria de acesso.

**O equívoco comum**

Marcar uma saída como sensível e considerar o assunto resolvido. Isso esconde o
valor da tela, não do arquivo. Quem lê o state lê o valor.

**Como inspecionar**

O `.gitignore` do laboratório ignora `*.tfstate` e `terraform.tfvars`. Se algum
dia um desses arquivos aparecer num diff, o commit não deve ser feito, e o
segredo que estava nele precisa ser rotacionado.

### 7.4 Drift

**O que é**

Drift é a divergência entre o que o código descreve e o que existe na nuvem,
criada por mudança manual.

O plano revela drift, e é essa a maior utilidade rotineira dele. Um plano que
propõe mudança sem que ninguém tenha mudado código significa que alguém mexeu no
console.

O conserto não é aplicar por cima sem pensar. As opções corretas estão no
runbook do operador: `import` para trazer ao código algo que existe fora dele,
`moved` para renomear sem destruir. Aplicar por cima é a terceira opção, e às
vezes a mudança manual era um conserto de emergência que ninguém documentou.

## 8. Módulos e composição

**O que é**

Módulo é uma pasta com código reutilizável. É a unidade que evita copiar a mesma
infraestrutura em cada ambiente.

O contrato de um módulo são três arquivos: `main.tf` com os recursos,
`variables.tf` com as entradas e `outputs.tf` com as saídas.

**Como funciona na prática**

O módulo `camada-do-lake` do laboratório provisiona uma camada completa do data
lake: o bucket, o versionamento, a criptografia, o bloqueio de acesso público, a
política de ciclo de vida e o banco no catálogo.

Repare em duas escolhas que vêm direto do módulo de cloud para dados:

O bloqueio de acesso público é aplicado no nível do bucket, e não por permissão
individual. Fechar ali significa que uma configuração errada depois não consegue
abrir por acidente.

A política de ciclo de vida inclui uma regra que quase todo projeto esquece:

<!-- verificacao: nivel 2, terraform validate com provider aws 6.57.1, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
```

Envio interrompido no meio deixa pedaços que não aparecem na listagem e são
cobrados. É a linha mais barata do arquivo e a mais frequentemente ausente.

**A regra de ouro**

Módulo bom expõe poucas variáveis e esconde a complexidade. O `camada-do-lake`
expõe seis, e três têm valor padrão. Quem usa não precisa saber que existem seis
recursos lá dentro.

**Versionamento de módulo remoto**

Módulo de registro remoto precisa de versão fixa. Apontar para a branch
principal é aceitar que a sua infraestrutura mude quando outra pessoa fizer merge.

## 9. for_each e count, e por que a escolha importa

**O que é**

Os dois criam vários recursos a partir de uma declaração. A diferença está em
como cada instância é identificada.

`count` identifica por índice numérico. `for_each` identifica por chave de um
mapa ou conjunto.

**Como funciona na prática**

O ambiente do laboratório instancia o módulo uma vez por camada:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
module "camada" {
  source   = "../../modulos/camada-do-lake"
  for_each = var.camadas

  nome_da_camada = each.key
  ambiente       = var.ambiente
}
```

**O equívoco comum, e ele é caro**

Usar `count` com lista para recurso nomeado. Suponha as camadas
`["bronze", "silver", "gold"]`, criadas com `count`. Elas viram os índices 0, 1 e
2. Agora acrescente `landing` no início da lista.

Com `count`, o índice 0 deixa de ser bronze e passa a ser landing, o 1 deixa de
ser silver e passa a ser bronze, e assim por diante. Do ponto de vista da
ferramenta, **todos** os recursos mudaram de identidade, e o plano propõe
destruir e recriar todos eles. Num data lake, isso é perder o conteúdo.

Com `for_each`, a chave é o nome. Acrescentar `landing` cria uma instância nova e
não toca nas outras.

A regra prática: `count` para ligar e desligar um recurso com condicional,
`for_each` para tudo que tem nome.

**Como inspecionar**

O plano mostra a diferença de forma inequívoca, com `-/+` nas instâncias que vão
ser recriadas. É a razão pela qual a seção 13 insiste em ler o plano.

## 10. Ambientes e raio de impacto

**O que é**

Separar dev, homologação e produção é decisão de arquitetura, porque ela define
o quanto um erro alcança.

| Abordagem | Como funciona | Quando serve |
|---|---|---|
| Workspaces | Vários states no mesmo código | Experimento, ambiente descartável |
| Pastas por ambiente | State e variáveis isolados por pasta | O caminho mais comum em empresa |
| Ferramenta de orquestração | Reduz repetição e ordena stacks | Muitos ambientes ou muitas stacks |

O laboratório usa pastas. `ambientes/dev/` tem o próprio `main.tf` e o próprio
backend, e um erro ali não alcança outra pasta.

**Raio de impacto**

Quebrar o state por domínio, por exemplo rede, dados e aplicação, limita o dano
de um erro e deixa o plano rápido. State único gigante tem dois problemas: o
plano demora, e um erro alcança tudo.

**Sobre Terraform Stacks**

O deck da aula apresenta Stacks como modelo oficial para orquestrar várias
configurações. A documentação oficial descreve Stacks como uma camada da
plataforma gerenciada HCP Terraform, e afirma que não está disponível na edição
comunitária. Não encontrei confirmação da afirmação de disponibilidade geral no
CLI principal, então este material não a repete.

## 11. Segredo nunca entra no código

**O que é**

Boa parte dos vazamentos de credencial nasce em repositório de infraestrutura, e
por um motivo simples: é o repositório que fala com tudo.

Três regras cobrem quase todos os casos:

1. **Nada de valor de segredo em arquivo versionado.** Nem em `tfvars`, nem em
   valor padrão de variável, nem em comentário.
2. **O segredo vem de um cofre.** A configuração busca o valor em tempo de
   execução, em vez de carregá-lo.
3. **A identidade não é uma chave.** No pipeline, o provider assume um papel. Não
   existe chave para vazar.

**Como funciona na prática**

O bloco `provider` do laboratório não tem nenhuma credencial:

<!-- verificacao: nivel 2, terraform validate com provider aws 6.57.1, scripts/verificar_iac.py, 2026-07-31 -->

```hcl
provider "aws" {
  region = var.regiao

  default_tags {
    tags = local.etiquetas_do_ambiente
  }
}
```

O `default_tags` merece atenção por outro motivo. Ele aplica as etiquetas a todo
recurso do provider, e etiqueta é o que transforma "a fatura subiu" em "a fatura
subiu por causa deste time". É a contrapartida prática da seção de custo do
módulo de cloud para dados.

**O equívoco comum**

Confiar que apagar o commit resolve. O histórico do Git guarda o valor antigo. Um
segredo que apareceu num commit precisa ser rotacionado, não apagado.

## 12. Testes e a pirâmide que existe de verdade

**O que é**

Infraestrutura tem pirâmide de testes, e a base dela é barata.

| Camada | O que verifica | Custo |
|---|---|---|
| `fmt` | Formatação | instantâneo |
| `validate` | Sintaxe e schema do provider | segundos |
| Linter | Regras de boa prática | segundos |
| Plano revisado | O que vai acontecer de verdade | minutos, e precisa de credencial |
| Teste com infraestrutura efêmera | Comportamento real | minutos ou horas, e custa dinheiro |
| Política como código | O que a revisão humana deixaria passar | integra ao pipeline |

**Como funciona na prática**

As três primeiras camadas são o que este módulo executa, e é o que o
`scripts/verificar_iac.py` faz num comando:

<!-- verificacao: nivel 3, execucao real do proprio script, codigo 0 com 6 checagens, 2026-07-31 -->

```
OK    terraform fmt, recursivo: codigo 0
OK    terraform init sem backend, ambientes/dev: codigo 0
OK    terraform validate, ambientes/dev: codigo 0
OK    terraform init sem backend, modulos/camada-do-lake: codigo 0
OK    terraform validate, modulos/camada-do-lake: codigo 0
OK    tflint, recursivo: codigo 0
6 checagem(ns), todas em nivel 2
```

**Por que o `init` é necessário, e por que ele é seguro aqui**

O `validate` sozinho confere sintaxe. Para conferir se um recurso aceita
determinado argumento, ele precisa do schema, que vem do provider. Sem `init`, o
Lab 5 passaria: trocar `status` por `statuss` num bloco só é detectado com o
provider baixado.

O `init` do laboratório roda com `-backend=false`. Ele baixa o provider do
registro público e não configura backend, não lê state e não fala com conta de
nuvem.

**Onde este módulo para, e por quê**

As três camadas de baixo da pirâmide são o teto desta trilha. `plan` e `apply`
são proibidos pelo guardrail do workspace, porque mudam infraestrutura real e
custam dinheiro real.

Isso é declarado no `lab.json` do módulo, com o motivo escrito, e o próprio script
recusa qualquer subcomando destrutivo por construção. Se alguém editar o arquivo e
acrescentar `plan`, a checagem falha em vez de executar.

**O que o gate não pega**

O Lab 6 existe para mostrar isso, e é o laboratório mais honesto do módulo. Um
valor que viola o bloco `validation` da própria variável passa pelo `validate` sem
erro, porque essa checagem acontece no `plan`.

Saber onde a rede de proteção termina vale tanto quanto saber que ela existe. Um
gate verde não significa que a infraestrutura está correta; significa que ela está
sintaticamente válida e bem formatada.

## 13. O fluxo que tira o apply do terminal

**O que é**

O valor real da prática aparece quando ninguém aplica infraestrutura do próprio
terminal.

1. Você abre um pull request com a mudança de código.
2. O pipeline roda o gate de formatação, sintaxe e linter.
3. O pipeline roda o plano e publica o resultado no pull request.
4. Alguém revisa o código **e** o plano.
5. Depois do merge, o pipeline aplica.

**Como ler um plano**

| Símbolo | Significado |
|---|---|
| `+` | será criado |
| `~` | será alterado no lugar |
| `-/+` | será **destruído e recriado** |
| `-` | será destruído |

As duas últimas linhas são as que exigem atenção. Num bucket de data lake, `-/+`
significa perder o conteúdo, e a causa costuma ser a mudança de um atributo que o
provider trata como imutável, como o nome do bucket.

A regra é curta: **destroy inesperado no plano é aviso, nunca detalhe.** Se você
não sabe explicar por que aquele recurso está sendo recriado, não aprove.

**O equívoco comum**

Tratar o fluxo por pull request como burocracia. Sem ele não existe revisão, não
existe rastreio de quem mudou o quê e por quê, e não existe trava contra dois
`apply` simultâneos. Os três aparecem no primeiro incidente.

## 14. Laboratório

O laboratório valida código de infraestrutura sem tocar nenhuma nuvem. Não
precisa de conta, não precisa de credencial e não custa nada.

Verificado com Terraform v1.15.8, TFLint v0.64.0 e provider `hashicorp/aws`
6.57.1. Os runbooks em `infrastructure/runbooks/` trazem o passo a passo.

### Lab 0: Conferir as ferramentas

Pré-condição: Terraform 1.9 ou superior e TFLint 0.60 ou superior.

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure
terraform version
tflint --version
```

### Lab 1: Rodar o gate completo

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo
python3 scripts/verificar_iac.py
```

Saída esperada: seis linhas começando com `OK` e a linha final
`6 checagem(ns), todas em nivel 2`.

### Lab 2: Rodar cada passo à mão

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure
terraform fmt -check -recursive
cd ambientes/dev
terraform init -backend=false -input=false
terraform validate
```

Saída esperada: o `fmt` não imprime nada, e o `validate` responde
`Success! The configuration is valid.`

### Lab 3: Quebrar a formatação

Acrescente espaços antes de um sinal de igual em
`modulos/camada-do-lake/main.tf` e rode o `fmt -check -recursive`.

Saída esperada: o caminho do arquivo impresso, com código de saída 3.

```
modulos/camada-do-lake/main.tf
```

Conserte com `terraform fmt -recursive`.

### Lab 4: Quebrar uma referência

Troque `var.ambiente` por `var.ambient` em `ambientes/dev/main.tf` e rode o
`validate` na pasta do ambiente.

Saída esperada:

```
Error: Reference to undeclared input variable

  on main.tf line 53, in module "camada":
  53:   ambiente          = var.ambient

An input variable with the name "ambient" has not been declared. Did you mean
"ambiente"?
```

Desfaça a mudança.

### Lab 5: Quebrar contra o schema do provider

Troque `status` por `statuss` dentro do bloco `versioning_configuration` em
`modulos/camada-do-lake/main.tf` e rode o `validate` na pasta do módulo.

Saída esperada:

```
Error: Missing required argument

  on main.tf line 34, in resource "aws_s3_bucket_versioning" "camada":
  34:   versioning_configuration {

The argument "status" is required, but no definition was found.
```

Este é o laboratório que justifica o `init`. Sem o provider baixado, a ferramenta
não sabe quais argumentos o recurso aceita, e o erro passaria. Desfaça a mudança.

### Lab 6: Ver o que o gate não pega

Mude o default de `dias_para_acesso_infrequente` para 10 em
`modulos/camada-do-lake/variables.tf` e rode o `validate`.

Saída observada:

```
Success! The configuration is valid.
```

O valor viola o bloco `validation` da própria variável, que exige no mínimo 30
dias, e o `validate` aprova. Validação de variável é avaliada no `plan`, que está
fora do escopo deste módulo por regra do workspace.

Este é o laboratório mais importante da lista, porque ele mede a rede de
proteção em vez de confiar nela. Desfaça a mudança e rode o gate outra vez.

### O que este laboratório não faz

Não roda `plan`, não roda `apply` e não roda `destroy`. Não cria recurso, não
consulta recurso existente e não usa credencial. O `lab.json` declara o teto de
nível 2 com o motivo escrito, e o script recusa subcomando destrutivo por
construção.

## 15. Exercícios e entregáveis

**Exercício 1: for_each contra count**

Objetivo: entender o custo de identificar recurso por índice.

Contexto: as três camadas do laboratório.

Entregável: descreva por escrito o que aconteceria ao acrescentar uma camada
`landing` no **início** da lista, nos dois casos, e diga por que um deles é
aceitável e o outro não. Não é necessário rodar plano; a explicação é o
entregável.

**Exercício 2: uma camada nova**

Objetivo: usar o módulo sem alterá-lo.

Contexto: o time pediu uma camada `landing` com esfriamento agressivo, porque o
dado ali é descartado depois de processado.

Entregável: a camada acrescentada em `ambientes/dev/variables.tf`, com os prazos
escolhidos e justificados, e o gate de validação passando.

**Exercício 3: o módulo que falta**

Objetivo: escrever um módulo com contrato claro.

Contexto: além dos buckets, a plataforma precisa de um papel de acesso somente
leitura ao prefixo curado, para a ferramenta de BI. Você já escreveu essa
política no módulo de cloud para dados.

Entregável: um módulo novo com `main.tf`, `variables.tf` e `outputs.tf`,
consumindo as saídas do módulo de camada, e o gate passando. Exponha no máximo
quatro variáveis.

**Exercício 4: ler um plano**

Objetivo: identificar destruição antes de ela acontecer.

Contexto: procure um plano de Terraform público, num artigo ou numa
documentação, ou peça um ao mentor.

Entregável: a lista dos recursos que seriam destruídos ou recriados, a
justificativa de cada um, e a decisão de aprovar ou recusar, com o motivo.

## 16. Mini-desafio com solução

**Enunciado**

O time quer que a política de ciclo de vida de produção seja diferente da de
desenvolvimento: em produção o dado bruto precisa ficar cinco anos, e o custo
importa mais. Em desenvolvimento o dado pode ser apagado em trinta dias.

Além disso, alguém quer poder impedir a destruição acidental dos buckets de
produção, sem duplicar o módulo.

Proponha uma solução e diga o que ela custa.

**Dicas**

- O módulo já recebe os prazos como variável, e o ambiente já é uma pasta.
- Existe um meta-argumento que impede a destruição de um recurso.
- Duplicar módulo por ambiente é a solução óbvia, e é a que o enunciado proíbe.

**Gabarito comentado**

Uma pasta `ambientes/prod/` com os próprios valores. O módulo não muda: ele já
recebe os prazos por variável, e é exatamente para isso que a variável existe.
Duplicar o módulo criaria duas definições da mesma camada, e elas divergiriam na
primeira correção aplicada em apenas uma.

Para os cinco anos de retenção, uma regra de expiração além das transições, com o
prazo em produção e um prazo curto em desenvolvimento. Vale conferir a duração
mínima da classe de destino antes de escolher o prazo, porque objeto apagado
antes dela é cobrado por ela.

Para a proteção contra destruição, o meta-argumento `lifecycle` com
`prevent_destroy`. Aqui está a parte que o enunciado esconde: no Terraform esse
valor precisa ser conhecido no momento da análise, e não aceita variável. Tentar
produz este erro, que foi observado de verdade:

<!-- verificacao: nivel 2, terraform validate com Terraform v1.15.8, saida real, 2026-07-31 -->

```
Error: Variables not allowed

  on main.tf line 20, in resource "aws_s3_bucket" "teste":
  20:     prevent_destroy = var.proteger

Variables may not be used here.
```

Então a proteção não pode ser ligada por ambiente com a mesma abordagem das
outras diferenças. O deck da aula menciona que o OpenTofu passou a aceitar
`prevent_destroy` dinâmico por variável; não confirmei isso em fonte oficial
nesta data, e se você depender disso, confira na versão que for usar.

As saídas honestas são três, e escolher entre elas é o exercício:

1. Ligar `prevent_destroy` para todos os ambientes. Simples, e transforma cada
   remoção legítima em duas etapas, inclusive em desenvolvimento.
2. Aceitar a duplicação apenas desse bloco, com um recurso condicional. Resolve e
   acrescenta um caminho de código.
3. Não usar `prevent_destroy` e proteger por permissão: negar a exclusão do bucket
   de produção na política de IAM, fora do Terraform. É a única que protege
   também contra quem age pelo console.

A terceira é a que eu defenderia, e a razão é a do módulo de cloud para dados:
identidade é a camada que vale em todos os caminhos, e o Terraform é apenas um
deles.

**Interpretação**

A resposta fraca duplica o módulo. A resposta boa usa a variável que já existe e
percebe que o `prevent_destroy` não segue o mesmo padrão das outras diferenças.
Quem chegou à terceira alternativa entendeu que a proteção mais forte não está na
ferramenta de provisionamento.

## 17. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Por que IaC existe | Diz que é boa prática | Explica procedência e reprodutibilidade | Usa o teste da segunda criação para avaliar um ambiente real |
| Blocos da linguagem | Copia de exemplo | Sabe o papel de cada bloco | Distingue `resource` de `data` e explica a consequência |
| State | Trata como arquivo temporário | Explica o mapa e a trava | Trata o state como dado sensível e sabe o que fazer se ele vazar |
| Módulo | Copia código entre ambientes | Escreve módulo com contrato | Módulo com poucas variáveis, validação e saídas úteis |
| for_each e count | Usa os dois sem critério | Escolhe `for_each` para o que tem nome | Explica o efeito de inserir item no meio de uma lista |
| Segredo | Deixa valor em tfvars | Usa cofre e papel assumido | Sabe que apagar o commit não resolve |
| Ler o plano | Aprova sem ler | Identifica criação e alteração | Recusa plano com destruição que não sabe explicar |
| Honestidade sobre o gate | Trata gate verde como garantia | Sabe o que cada ferramenta cobre | Sabe onde a proteção termina, como no Lab 6 |

## 18. Erros comuns e como corrigir

**O `fmt -check` falha no pipeline e ninguém sabe por quê**

Sintoma: o pipeline recusa a mudança e imprime apenas um caminho de arquivo.

Causa: o arquivo não está no formato canônico. O código de saída é 3, não 1.

Correção: `terraform fmt -recursive` e commitar. Vale ligar isso num gancho de
pré-commit, porque é a falha mais boba de descobrir no pipeline.

**O `validate` aprova e o `plan` falha**

Sintoma: o gate passa e o plano do pipeline quebra.

Causa: são checagens diferentes. O `validate` confere sintaxe e schema; o `plan`
avalia expressão, valida variável e consulta a nuvem.

Correção: entender que o gate é a primeira porta, não a última. O Lab 6 mostra
exatamente um caso em que o `validate` aprova o que o `plan` recusaria.

**O `validate` reclama de provider não inicializado**

Sintoma: o comando pede `terraform init` antes de qualquer outra coisa.

Causa: sem `init`, não existe schema de provider para conferir.

Correção: `terraform init -backend=false`. A opção importa: sem ela, a ferramenta
tenta configurar o backend declarado, e num projeto real isso significa falar com
o bucket de state.

**O plano quer recriar tudo depois de uma mudança pequena**

Sintoma: uma inserção na lista de camadas produz destruição em massa.

Causa: `count` com lista. Os recursos são identificados por índice, e inserir no
meio muda a identidade de todos os seguintes.

Correção: `for_each` com mapa ou conjunto. Migrar exige o bloco `moved`, ou o
recurso é destruído no processo.

**O nome do bucket já existe**

Sintoma: a criação falha dizendo que o nome está em uso.

Causa: nome de bucket é único no mundo inteiro, não na sua conta.

Correção: prefixo próprio no nome. É por isso que o laboratório tem a variável
`prefixo_do_bucket`, com um valor de exemplo que precisa ser trocado.

**O state foi perdido**

Sintoma: o plano propõe criar tudo de novo, e a infraestrutura já existe.

Causa: state local apagado, ou backend trocado sem migração.

Correção: `import` recurso por recurso, o que é lento e chato. A prevenção é
backend remoto desde o primeiro dia, e é por isso que ele aparece no runbook do
operador.

**Alguém mexeu no console**

Sintoma: o plano propõe mudança sem que ninguém tenha alterado código.

Causa: drift.

Correção: entender **o que** foi mudado antes de decidir. `import` para trazer ao
código, `moved` para renomear sem destruir, ou aplicar por cima. A terceira
opção reescreve a mudança manual, e às vezes ela era um conserto de emergência.

## 19. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 1 e 2. O primeiro é conceitual e o segundo prova que você
entendeu o contrato do módulo.

**O que estudar em seguida, dentro da trilha**

Este é o segundo módulo do bloco de nuvem e escala. Vêm depois processamento
distribuído e Kubernetes. Vale reler o módulo de Kubernetes com este na cabeça: o
manifesto declarativo e a reconciliação são a mesma ideia deste módulo, aplicada
ao cluster em vez da nuvem.

**O que aprofundar por conta**

Rode um `plan` no seu próprio ambiente, com a sua conta e a sua conta de custo. É
a parte que esta trilha não faz por decisão, e é onde se aprende mais. Comece com
um recurso barato e leia o plano inteiro antes de aplicar.

Depois, política como código. É o que bloqueia no pipeline o que a revisão humana
deixaria passar, e ela existe justamente porque revisão humana cansa.

**O que não perseguir agora**

Escrever provider próprio, e migrar tudo para uma ferramenta em linguagem de
programação de uso geral. Os dois são decisões grandes, e nenhuma delas melhora o
seu dia enquanto o fluxo por pull request não existir.

## 20. Glossário

| Termo | Significado |
|---|---|
| Backend | Onde o state é guardado, local ou remoto |
| `count` | Meta-argumento que repete recurso por índice numérico |
| `data` | Bloco que consulta recurso existente, sem assumir a gestão |
| Declarativo | Descrever o resultado, não o passo a passo |
| Drift | Divergência entre o código e o que existe de fato |
| `for_each` | Meta-argumento que repete recurso por chave estável |
| HCL | Linguagem de configuração do Terraform |
| Idempotente | Aplicar duas vezes produz o mesmo resultado que aplicar uma |
| `import` | Trazer para o state um recurso que já existe |
| `lifecycle` | Meta-argumento que altera o comportamento de criação e destruição |
| Lock | Trava que impede duas execuções simultâneas sobre o mesmo state |
| Módulo | Pasta com código reutilizável, com entradas e saídas |
| `moved` | Bloco que renomeia um recurso no código sem destruí-lo |
| Plano | Diferença entre o desejado, o state e o real |
| `prevent_destroy` | Opção que recusa a destruição de um recurso |
| Provider | Plugin que traduz a configuração em chamadas de API |
| Raio de impacto | Quanto da infraestrutura um erro alcança |
| `resource` | Bloco que declara recurso gerenciado pela ferramenta |
| State | Mapa entre o código e os recursos reais |
| `validation` | Bloco que recusa valor inválido de variável, avaliado no plano |

## Referências

Documentação oficial, consultada em 2026-07-31:

- Dado sensível no state: https://developer.hashicorp.com/terraform/language/state/sensitive-data
- Terraform Stacks: https://developer.hashicorp.com/terraform/language/stacks
- Repositório do OpenTofu: https://github.com/opentofu/opentofu
- TFLint: https://github.com/terraform-linters/tflint

Referência do módulo de cloud para dados, para as durações mínimas das classes de
armazenamento citadas nas validações:

- Classes de armazenamento do Amazon S3: https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html

## Fontes verificadas (2026-07-31)

- A documentação oficial afirma que, ao desenvolver localmente, o Terraform
  guarda o state num arquivo em texto plano que inclui qualquer valor secreto
  definido na configuração, e recomenda guardar o state remotamente,
  criptografá-lo em repouso, restringir o acesso e manter log de auditoria.
  https://developer.hashicorp.com/terraform/language/state/sensitive-data
- O Terraform Stacks é descrito pela documentação oficial como uma camada de
  configuração do HCP Terraform, e a mesma página afirma que não está disponível
  para a edição comunitária. A afirmação do deck de que Stacks está em
  disponibilidade geral no CLI principal não foi confirmada nesta data, e por
  isso não é repetida nesta apostila.
  https://developer.hashicorp.com/terraform/language/stacks
- O OpenTofu está sob a Mozilla Public License 2.0.
  https://github.com/opentofu/opentofu
- A duração mínima de 30 dias da classe de acesso infrequente e de 180 dias da
  classe de arquivamento profundo, usadas nos blocos `validation` do módulo, vêm
  da tabela comparativa de classes do S3.
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html
- O código Terraform deste módulo foi verificado em nível 2 com Terraform
  v1.15.8, TFLint v0.64.0 com o conjunto de regras `terraform` 0.15.0 embutido, e
  provider `hashicorp/aws` 6.57.1. As seis checagens do
  `scripts/verificar_iac.py` passaram com código 0 em 2026-07-31. Nenhum recurso
  foi criado, nenhum plano foi gerado e nenhuma credencial foi usada.
- O teto de nível 2 é regra do workspace, não limitação técnica: `terraform plan`
  e `terraform apply` não são executados por esta trilha nem por este script, que
  recusa subcomando destrutivo por construção.
- A saída `Success! The configuration is valid.` para um valor que viola o bloco
  `validation` da variável foi observada de verdade em 2026-07-31, com
  `dias_para_acesso_infrequente` igual a 10. É a origem do Lab 6 e do limite
  declarado no `lab.json`.
- O `prevent_destroy` do bloco `lifecycle` não aceita variável no Terraform
  v1.15.8. O erro `Variables not allowed`, seguido de
  `Unsuitable value: value must be known`, foi obtido em execução real de
  `terraform validate` em 2026-07-31.
- As afirmações do deck sobre a data da aquisição da HashiCorp pela IBM, a versão
  exata da mudança de licença do Terraform, a filiação do OpenTofu a uma fundação
  e o `prevent_destroy` dinâmico do OpenTofu não foram confirmadas em fonte
  oficial nesta data, e por isso não aparecem nesta apostila como fato.
