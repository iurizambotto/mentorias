output "nome_do_bucket" {
  description = "Nome do bucket criado para a camada."
  value       = aws_s3_bucket.camada.id
}

output "arn_do_bucket" {
  description = "ARN do bucket, usado por politica de IAM de quem le a camada."
  value       = aws_s3_bucket.camada.arn
}

output "banco_do_catalogo" {
  description = "Nome do banco no catalogo, usado pela engine de query."
  value       = aws_glue_catalog_database.camada.name
}
