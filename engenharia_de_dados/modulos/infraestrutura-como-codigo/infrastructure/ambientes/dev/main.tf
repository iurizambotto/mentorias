terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # O backend remoto fica comentado de proposito. Ele exige um bucket e uma
  # tabela de trava que existem antes do Terraform, e este laboratorio nao
  # provisiona nada em nuvem. Descomentar e trocar os nomes e a primeira coisa
  # que um projeto real faz, porque state em arquivo local nao sobrevive a
  # segunda pessoa do time.
  #
  # backend "s3" {
  #   bucket       = "SEU-BUCKET-DE-STATE"
  #   key          = "datalake/dev/terraform.tfstate"
  #   region       = "us-east-1"
  #   encrypt      = true
  #   use_lockfile = true
  # }
}

provider "aws" {
  region = var.regiao

  # Sem credencial nenhuma neste arquivo. O provider resolve a identidade pelo
  # ambiente, e num pipeline isso e um papel assumido, nao uma chave.
  default_tags {
    tags = local.etiquetas_do_ambiente
  }
}

locals {
  etiquetas_do_ambiente = {
    projeto  = "plataforma-de-campanhas"
    ambiente = var.ambiente
    time     = "dados"
  }
}

# for_each em vez de tres blocos iguais. A chave do mapa e o nome da camada, e
# ela e estavel: acrescentar uma camada nova nao renumera as existentes, que e
# exatamente o que aconteceria com count.
module "camada" {
  source = "../../modulos/camada-do-lake"

  for_each = var.camadas

  nome_da_camada    = each.key
  ambiente          = var.ambiente
  prefixo_do_bucket = var.prefixo_do_bucket
  etiquetas         = local.etiquetas_do_ambiente

  dias_para_acesso_infrequente    = each.value.dias_para_acesso_infrequente
  dias_para_arquivamento_profundo = each.value.dias_para_arquivamento_profundo
}
