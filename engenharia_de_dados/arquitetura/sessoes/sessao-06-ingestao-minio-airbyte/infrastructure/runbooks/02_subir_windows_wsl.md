# Sessão 06 — Subir no Windows + Docker Desktop + WSL

## 1) Executar compose no WSL
```bash
cd ~/zambotto_new/projects/zambotto-mentoria/docs/mentees/aurelius/sessions/sessao-06-ingestao-minio-airbyte/infrastructure
docker compose up -d
```

## 2) Instalar `abctl` no WSL
```bash
curl -LsfS https://get.airbyte.com | bash -
```

## 3) Instalar Airbyte local
```bash
abctl local install --low-resource-mode
```

## 4) Recuperar credenciais
```bash
abctl local credentials
```

## 5) Acesso no navegador do Windows
- Airbyte: `http://localhost:8000`
- MinIO Console: `http://localhost:9101`
