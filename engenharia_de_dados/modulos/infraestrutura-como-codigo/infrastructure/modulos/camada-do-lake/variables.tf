variable "nome_da_camada" {
  description = "Camada do lake que este modulo provisiona, por exemplo bronze."
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9_]*$", var.nome_da_camada))
    error_message = "O nome da camada aceita apenas minusculas, digitos e sublinhado."
  }
}

variable "ambiente" {
  description = "Ambiente alvo, usado no nome do bucket e do banco do catalogo."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.ambiente)
    error_message = "O ambiente precisa ser dev, staging ou prod."
  }
}

variable "prefixo_do_bucket" {
  description = "Prefixo global do nome do bucket. Nome de bucket e unico no mundo."
  type        = string
}

variable "dias_para_acesso_infrequente" {
  description = <<-EOT
    Idade em dias para transicionar o objeto para acesso infrequente. O minimo
    de 30 nao e escolha de estilo: a classe cobra 30 dias mesmo que o objeto
    seja apagado antes.
  EOT
  type        = number
  default     = 90

  validation {
    condition     = var.dias_para_acesso_infrequente >= 30
    error_message = "A duracao minima da classe de acesso infrequente e de 30 dias."
  }
}

variable "dias_para_arquivamento_profundo" {
  description = <<-EOT
    Idade em dias para transicionar o objeto para arquivamento profundo. O
    minimo de 180 vem da duracao minima cobrada por essa classe.
  EOT
  type        = number
  default     = 365

  validation {
    condition     = var.dias_para_arquivamento_profundo >= 180
    error_message = "A duracao minima da classe de arquivamento profundo e de 180 dias."
  }
}

variable "etiquetas" {
  description = "Etiquetas aplicadas a todo recurso, para atribuir custo por time."
  type        = map(string)
  default     = {}
}
