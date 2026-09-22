---
name: dashboard-html
description: Constrói um dashboard de resultados em um único arquivo HTML autocontido, que abre offline e por anexo de email, com indicadores, gráficos em SVG embutido e tabela filtrável, mais um pacote de dados pronto para montar o mesmo painel no Power BI. Usar quando o pedido incluir dashboard, painel, visualização interativa, Power BI ou BI a partir de uma análise feita com a skill analise-de-dados.
---

# Dashboard em HTML autocontido

Pré-requisito: `analise/numeros.json` existe. O dashboard mostra números do livro, não
recalcula por conta própria.

## Regras do arquivo

- Um arquivo só: `entregas/dashboard.html`.
- Nenhum recurso carregado da rede. Sem CDN, sem fonte externa, sem `fetch`. Gráficos em SVG
  gerado no próprio script, com matplotlib (`savefig` em formato `svg` para um buffer e o texto
  embutido no HTML) ou SVG escrito à mão.
- `<html lang="pt-BR">`, `<title>` com o nome do painel, `<meta name="viewport">`.
- Funciona em tela de celular: grade que vira coluna única abaixo de 700 px.
- Respeita tema claro e escuro com `prefers-color-scheme`, cores em variáveis CSS.
- Gere o HTML por um script em `analise/scripts/`, nunca à mão, para que dê para regenerar.

## Conteúdo, de cima para baixo

1. A pergunta, e a resposta em uma frase.
2. De três a cinco indicadores, cada um com o valor, a comparação (contra a meta, contra o
   orçamento ou contra o período anterior) e a base de linhas.
3. Um gráfico por insight, com título que diz a conclusão.
4. Uma tabela de detalhe com filtro por texto e ordenação por coluna, em JavaScript puro.
5. "Como ler este painel" e "O que ele não mostra", em poucas linhas.
6. Rodapé com a data dos dados e os scripts que geraram tudo.

## Pacote para Power BI

Na mesma entrega, crie `entregas/powerbi/` com:

- As tabelas já limpas em CSV UTF-8, uma por grão (fatos separados de dimensões).
- `modelo.md` com os relacionamentos, a cardinalidade de cada um e as medidas em DAX que
  reproduzem os indicadores do dashboard, cada uma com o valor esperado vindo do livro.

Declare no `modelo.md` que as medidas não foram executadas no Power BI Desktop: o valor
esperado ao lado de cada uma é o que permite a quem montar o painel conferir.

## Validar

```bash
python3 .claude/skills/dashboard-html/scripts/validar_dashboard.py entregas/dashboard.html
python3 .claude/skills/analise-de-dados/scripts/conferir_numeros.py entregas/dashboard.html
```

O conferidor lê o texto visível e ignora o interior dos gráficos. Os números dos indicadores
e das frases precisam ter lastro.
