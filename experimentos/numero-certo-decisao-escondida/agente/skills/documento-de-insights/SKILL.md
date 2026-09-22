---
name: documento-de-insights
description: Produz o documento de insights de uma análise de dados em DOCX e PDF, escrito para quem decide e não para quem analisa, com cada número conferido contra o livro de números da análise. Usar quando o pedido incluir relatório, documento, Word, PDF, resumo executivo ou insights de uma análise já feita com a skill analise-de-dados.
---

# Documento de insights

Pré-requisito: `analise/numeros.json` e `analise/decisoes.md` existem. Se não existem, rode
antes a skill `analise-de-dados`. Este documento não calcula nada, ele comunica o que já foi
calculado.

## Para quem

Para uma pessoa que conhece o negócio melhor que você e não vai abrir o dado. Ela precisa
saber o que aconteceu, quanto isso vale, o quanto confiar e o que fazer a seguir.

## Estrutura

Escreva em `entregas/insights.md`, nesta ordem:

1. `# Título` que é a conclusão, não o tema. "As vendas cresceram e a margem caiu" em vez de
   "Análise de vendas".
2. `## Resumo` com três itens no máximo, cada um com um número.
3. `## Insights`, um `###` por insight. Cada um tem: a afirmação em uma frase, a evidência com
   o número e a base de linhas, o que isso significa para o negócio e o grau de confiança
   (alto, médio, baixo) com o motivo.
4. `## O que esta análise não responde`, com as leituras alternativas da pergunta e o que ficou
   fora do universo comparado.
5. `## Decisões de método`, as decisões de `decisoes.md` que mais movem o resultado, com o
   valor de cada alternativa.
6. `## Qualidade da base`, problemas encontrados no perfil que o leitor precisa conhecer.
7. `## Próximos passos`, ações e perguntas para quem conhece o negócio responder.
8. `## Como reproduzir`, a lista dos scripts em ordem.

Sem jargão técnico no corpo. "Deduplicação" vira "a mesma venda não foi contada duas vezes".
Jargão só na seção de reprodução.

## Gerar e conferir

```bash
python3 .claude/skills/documento-de-insights/scripts/md_para_docx.py entregas/insights.md entregas/insights.docx --pdf
python3 .claude/skills/analise-de-dados/scripts/conferir_numeros.py entregas/insights.docx
```

O conversor aceita títulos `#` a `###`, parágrafos, listas `-` e `1.`, tabelas com `|`,
citação `>` e `**negrito**`. Nada além disso: formatação fora desse conjunto some.

O documento só está pronto quando o conferidor sai sem número sem lastro.
