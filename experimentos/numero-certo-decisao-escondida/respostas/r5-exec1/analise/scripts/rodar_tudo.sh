#!/usr/bin/env bash
# Refaz a analise inteira e todos os entregaveis, do arquivo bruto ao deck.
# Rodar a partir da raiz do projeto.
set -euo pipefail

SKILLS=.claude/skills
ARQ="BASE DE PACING_v2.csv.xls"

python3 "$SKILLS/analise-de-dados/scripts/perfilar.py" "$ARQ" --saida analise

rm -f analise/numeros.json
for s in 01_escopo 02_sobreposicao 03_denominadores 04_pacing 05_alternativas \
         06_series 07_destaques 08_dashboard 09_powerbi 10_apresentacao; do
  echo "== $s"
  python3 "analise/scripts/$s.py" > /dev/null
done

python3 "$SKILLS/documento-de-insights/scripts/md_para_docx.py" \
  entregas/insights.md entregas/insights.docx --pdf > /dev/null

echo "== conferencia"
python3 "$SKILLS/dashboard-html/scripts/validar_dashboard.py" entregas/dashboard.html
python3 "$SKILLS/apresentacao-de-resultados/scripts/validar_pptx.py" \
  entregas/apresentacao.pptx --render entregas/preview | grep -E "PROBLEMA|ok:"
for f in entregas/resposta.md entregas/insights.md entregas/insights.docx \
         entregas/dashboard.html entregas/apresentacao.pptx \
         entregas/powerbi/modelo.md analise/decisoes.md; do
  python3 "$SKILLS/analise-de-dados/scripts/conferir_numeros.py" "$f"
done
