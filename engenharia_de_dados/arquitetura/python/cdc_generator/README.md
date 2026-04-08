# cdc_generator

Projeto Python da trilha de Aurelius para geração de dados sintéticos por domínio e simulação de eventos CDC.

## Estrutura
- `config/`: configurações por domínio em YAML.
- `scripts/`: CLIs de geração e build de artefatos.
- `src/`: biblioteca Python (`zambotto_mentoria`).
- `tests/`: testes automatizados.
- `data/`: datasets de exemplo e saídas geradas.

## Execução (exemplo)
```bash
uv run -p .venv python docs/mentees/aurelius/python/cdc_generator/scripts/generate_domain_data.py \
  --config docs/mentees/aurelius/python/cdc_generator/config/domains/marketing.yaml \
  --output docs/mentees/aurelius/python/cdc_generator/data \
  --formats csv
```
