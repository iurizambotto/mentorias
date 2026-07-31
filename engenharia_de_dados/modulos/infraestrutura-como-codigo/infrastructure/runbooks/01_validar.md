---
title: "Validar o codigo de infraestrutura"
date: 2026-07-31
type: runbook
status: active
tags:
  - terraform
  - laboratorio
---

# Validar o código de infraestrutura

Todos os caminhos deste runbook são relativos à raiz do repositório clonado.

## 1. Rodar o gate completo

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo
python3 scripts/verificar_iac.py
```

Saída esperada:

```
OK    terraform fmt, recursivo: codigo 0
OK    terraform init sem backend, ambientes/dev: codigo 0
OK    terraform validate, ambientes/dev: codigo 0
OK    terraform init sem backend, modulos/camada-do-lake: codigo 0
OK    terraform validate, modulos/camada-do-lake: codigo 0
OK    tflint, recursivo: codigo 0
6 checagem(ns), todas em nivel 2
```

O script recusa qualquer subcomando destrutivo por construção. Se alguém editar
o arquivo e acrescentar `plan` ou `apply`, a checagem falha em vez de executar.

## 2. Rodar cada passo à mão

Vale fazer uma vez, para entender o que o script faz.

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure
terraform fmt -check -recursive
```

Saída esperada: nada, com código de saída 0. Se algum arquivo estiver
desformatado, o comando imprime o caminho dele e sai com código 3. Para
corrigir:

```bash
terraform fmt -recursive
```

Depois, no ambiente. O caminho é escrito a partir da raiz do repositório, porque
runbook é copiado e colado sem que ninguém confira em que pasta está:

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure/ambientes/dev
terraform init -backend=false -input=false
terraform validate
```

Saída esperada do `validate`:

```
Success! The configuration is valid.
```

O `-backend=false` não é detalhe. Sem ele o Terraform tenta configurar o backend
declarado, e num projeto real isso significa falar com o bucket de state.

## 3. Rodar o TFLint

```bash
cd engenharia_de_dados/modulos/infraestrutura-como-codigo/infrastructure
tflint --recursive
```

Saída esperada: nada, com código de saída 0.

A configuração está em `.tflint.hcl` com o conjunto recomendado de regras. Ela é
mais rigorosa que o `validate`: o `validate` pergunta se o código é válido, e o
TFLint pergunta se ele é bom.

## 4. Quebrar de propósito

Vale ver as ferramentas reclamarem. Faça uma mudança, rode, e desfaça.

**Formatação.** Acrescente espaços extras antes de um sinal de igual em
`modulos/camada-do-lake/main.tf` e rode `terraform fmt -check -recursive`.

Saída esperada: o caminho do arquivo, e código de saída 3.

```
modulos/camada-do-lake/main.tf
```

**Referência inexistente.** Troque `var.ambiente` por `var.ambient` em
`ambientes/dev/main.tf` e rode `terraform validate` na pasta do ambiente.

Saída esperada:

```
Error: Reference to undeclared input variable

  on main.tf line 53, in module "camada":
  53:   ambiente          = var.ambient

An input variable with the name "ambient" has not been declared. Did you mean
"ambiente"?
```

**Erro contra o schema do provider.** Troque `status` por `statuss` dentro do
bloco `versioning_configuration` em `modulos/camada-do-lake/main.tf` e rode
`terraform validate` na pasta do módulo.

Saída esperada:

```
Error: Missing required argument

  on main.tf line 34, in resource "aws_s3_bucket_versioning" "camada":
  34:   versioning_configuration {

The argument "status" is required, but no definition was found.
```

Este terceiro caso é o que justifica o `init`. Sem o provider baixado, o
Terraform não sabe quais argumentos o recurso aceita, e esse erro passaria.

## 4.1 O que essas ferramentas não pegam

Vale fazer um quarto teste, e prestar atenção no resultado.

Mude o default de `dias_para_acesso_infrequente` para 10 em
`modulos/camada-do-lake/variables.tf` e rode `terraform validate`.

Saída observada:

```
Success! The configuration is valid.
```

O valor viola o bloco `validation` da própria variável, que exige no mínimo 30
dias, e o `validate` aprova. O motivo é que validação de variável é avaliada no
`plan`, e o `plan` está fora do escopo deste módulo por regra do workspace.

Isso é o teto do nível 2 aparecendo na prática. O bloco `validation` continua
valendo a pena, porque ele protege no `plan` do operador, mas ele **não** é
exercitado por nada que roda aqui. Desfaça a mudança.

Próximo passo: [02_o_que_fica_para_o_operador.md](02_o_que_fica_para_o_operador.md).
