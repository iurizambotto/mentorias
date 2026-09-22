---
name: apresentacao-de-resultados
description: Monta a apresentação de resultados de uma análise de dados em PPTX 16:9, com um slide por mensagem, gráficos gerados a partir da análise, validação mecânica e renderização em imagem para revisão visual antes da entrega. Usar quando o pedido incluir apresentação, deck, slides, PowerPoint ou PPT de resultados de uma análise feita com a skill analise-de-dados.
---

# Apresentação de resultados

Pré-requisito: `analise/numeros.json` existe. Os slides comunicam números do livro.

## O deck

Entre 8 e 12 slides, 16:9 (13,333 por 7,5 polegadas), nesta ordem:

1. Capa: o título é a conclusão principal.
2. A pergunta de negócio, nas palavras de quem perguntou.
3. A resposta em uma frase e até três indicadores grandes.
4. De três a cinco slides de insight. **O título de cada um é a mensagem**, não o tema: "A região
   Sul vendeu metade da meta" em vez de "Desempenho por região". Um gráfico e uma frase de
   implicação por slide.
5. O que a análise não responde, e a qualidade da base.
6. Decisões de método que mudam o resultado, com o valor de cada alternativa.
7. Próximos passos.
8. Apêndice: como reproduzir.

## Forma

- Título com 28 pt ou mais, corpo com 16 pt ou mais, nada abaixo de 12 pt.
- No máximo 40 palavras de corpo por slide. O resto vai para as notas do apresentador.
- Gráficos em PNG gerados com matplotlib a 200 dpi, sem título dentro da imagem, porque o
  título do slide já diz a mensagem. Rótulos de eixo legíveis e valores anotados quando forem
  poucos.
- Uma cor de destaque só, usada no dado que o título aponta. O resto em cinza.
- Construa o deck com `python-pptx` por um script em `analise/scripts/`, para poder regenerar.
- Não deixe placeholder vazio. Se o layout traz um que não vai usar, remova.

## Validar e olhar

```bash
python3 .claude/skills/apresentacao-de-resultados/scripts/validar_pptx.py entregas/apresentacao.pptx --render entregas/preview
python3 .claude/skills/analise-de-dados/scripts/conferir_numeros.py entregas/apresentacao.pptx
```

O validador aponta fonte pequena, forma fora do slide, placeholder vazio e excesso de texto.
Depois, **abra cada PNG de `entregas/preview/` e olhe**. Texto que transborda da caixa,
sobreposição e gráfico ilegível só aparecem na imagem. Corrija e renderize de novo até não
haver o que corrigir.
