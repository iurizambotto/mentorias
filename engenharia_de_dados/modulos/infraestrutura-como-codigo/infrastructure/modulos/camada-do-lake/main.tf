terraform {
  required_version = ">= 1.9"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      # Pinned to a major version. A floating constraint turns a provider
      # release into a silent change in your infrastructure.
      version = "~> 6.0"
    }
  }
}

locals {
  nome_do_bucket = "${var.prefixo_do_bucket}-${var.nome_da_camada}-${var.ambiente}"

  etiquetas_completas = merge(var.etiquetas, {
    camada   = var.nome_da_camada
    ambiente = var.ambiente
    gerido   = "terraform"
  })
}

resource "aws_s3_bucket" "camada" {
  bucket = local.nome_do_bucket
  tags   = local.etiquetas_completas
}

# Versioning first. Without it, an overwrite has no undo, and durability of
# eleven nines says nothing about someone replacing the object by mistake.
resource "aws_s3_bucket_versioning" "camada" {
  bucket = aws_s3_bucket.camada.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "camada" {
  bucket = aws_s3_bucket.camada.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# A data lake bucket is never public. Blocking at the bucket level means a wrong
# ACL later cannot open it by accident.
resource "aws_s3_bucket_public_access_block" "camada" {
  bucket = aws_s3_bucket.camada.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "camada" {
  bucket = aws_s3_bucket.camada.id

  # Explicit dependency: the provider requires versioning to be settled before
  # a lifecycle rule that touches noncurrent versions.
  depends_on = [aws_s3_bucket_versioning.camada]

  rule {
    id     = "esfriar-por-idade"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = var.dias_para_acesso_infrequente
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = var.dias_para_arquivamento_profundo
      storage_class = "DEEP_ARCHIVE"
    }

    # Old versions are cost with no reader. They go away on a schedule.
    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    # Multipart leftovers are invisible and billed. This is the cheapest rule
    # in the file and the one most often missing.
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

resource "aws_glue_catalog_database" "camada" {
  name        = "${var.nome_da_camada}_${var.ambiente}"
  description = "Catalogo da camada ${var.nome_da_camada} no ambiente ${var.ambiente}."
}
