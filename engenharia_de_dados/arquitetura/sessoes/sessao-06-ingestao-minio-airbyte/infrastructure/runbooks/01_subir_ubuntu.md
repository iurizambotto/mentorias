# Sessão 06 — Subir no Ubuntu

## 1) Subir dependências locais
```bash
docker compose up -d
```

## 2) Instalar `abctl` (se necessário)
```bash
curl -LsfS https://get.airbyte.com | bash -
```

## 3) Instalar Airbyte local (modo enxuto)
```bash
abctl local install --low-resource-mode
```

## 4) Obter credenciais iniciais
```bash
abctl local credentials
```

## 5) Acessos
- Airbyte UI: `http://localhost:8000`
- MinIO Console: `http://localhost:9101`
