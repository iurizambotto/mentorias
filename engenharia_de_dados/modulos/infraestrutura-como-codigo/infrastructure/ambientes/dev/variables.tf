variable "ambiente" {
  description = "Nome do ambiente desta pasta."
  type        = string
  default     = "dev"
}

variable "regiao" {
  description = "Regiao da nuvem. Preco e latencia variam por regiao."
  type        = string
  default     = "us-east-1"
}

variable "prefixo_do_bucket" {
  description = <<-EOT
    Prefixo do nome dos buckets. Nome de bucket e unico no mundo inteiro, logo
    este valor precisa ser trocado antes de qualquer uso real.
  EOT
  type        = string
  default     = "exemplo-plataforma-campanhas"
}

variable "camadas" {
  description = <<-EOT
    Camadas do lake e a politica de esfriamento de cada uma. A camada bronze
    guarda o dado cru e e a que mais se beneficia de arquivamento; a gold e
    consultada com frequencia e nao deveria esfriar rapido.
  EOT
  type = map(object({
    dias_para_acesso_infrequente    = number
    dias_para_arquivamento_profundo = number
  }))

  default = {
    bronze = {
      dias_para_acesso_infrequente    = 30
      dias_para_arquivamento_profundo = 180
    }
    silver = {
      dias_para_acesso_infrequente    = 90
      dias_para_arquivamento_profundo = 365
    }
    gold = {
      dias_para_acesso_infrequente    = 365
      dias_para_arquivamento_profundo = 1095
    }
  }
}
