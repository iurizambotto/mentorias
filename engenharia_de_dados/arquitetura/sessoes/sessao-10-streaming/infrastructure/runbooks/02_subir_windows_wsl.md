# Sessão 10 — Subir no Windows + Docker Desktop + WSL

## 1) Abrir terminal WSL na pasta da sessão
```bash
cd ~/zambotto_new/projects/zambotto-mentoria/docs/mentees/aurelius/sessions/sessao-10-streaming/infrastructure
```

## 2) Preparar diretórios do Airflow
```bash
mkdir -p airflow/dags airflow/logs
```

## 3) Subir stack completa
```bash
docker compose up -d
```

## 4) Validar
```bash
docker compose ps
```

## 5) Se houver pressão de memória
1. Encerrar stack: `docker compose down`
2. Ajustar `.wslconfig` (memória/swap)
3. Reiniciar WSL e Docker Desktop
