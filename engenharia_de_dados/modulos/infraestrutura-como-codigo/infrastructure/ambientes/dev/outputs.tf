output "buckets_por_camada" {
  description = "Nome do bucket de cada camada, para uso em runbook e em politica."
  value       = { for nome, mod in module.camada : nome => mod.nome_do_bucket }
}

output "bancos_do_catalogo" {
  description = "Banco do catalogo por camada, para configurar a engine de query."
  value       = { for nome, mod in module.camada : nome => mod.banco_do_catalogo }
}

output "arns_dos_buckets" {
  description = "ARN por camada, usado ao escrever politica de menor privilegio."
  value       = { for nome, mod in module.camada : nome => mod.arn_do_bucket }
}
