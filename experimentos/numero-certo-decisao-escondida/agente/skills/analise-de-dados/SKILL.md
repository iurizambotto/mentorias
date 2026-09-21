---
name: analise-de-dados
description: Método de análise de dados para qualquer arquivo tabular (CSV, Excel, JSON, Parquet), com perfil que não confia na extensão, detecção de grão e de tabelas misturadas, livro de números que dá lastro a cada valor citado e registro das decisões que mudam o resultado. Usar sempre que o pedido for analisar, explorar, auditar ou responder uma pergunta de negócio a partir de um arquivo de dados, antes de qualquer documento, dashboard ou apresentação.
---

# Análise de dados com lastro

Uma análise vale pelo número que sobrevive à conferência. Este método existe para que todo
número dito tenha um script que o reproduz e toda escolha que muda um número esteja escrita.

## Estrutura de pastas

```
analise/
├── perfil.md, perfil.json     saída do passo 1
├── scripts/NN_nome.py         um script por pergunta, numerado na ordem em que roda
├── numeros.json               livro de números, preenchido pelos scripts
└── decisoes.md                toda escolha que muda um número, com o impacto medido
entregas/                      só o que vai para o leitor
```

## Passo 1. Perfil, sem confiar no nome do arquivo

```bash
python3 .claude/skills/analise-de-dados/scripts/perfilar.py <arquivo> --saida analise
```

Leia `analise/perfil.md` inteiro antes de escrever qualquer código de análise. Ele responde:
qual é o formato real, se há BOM, quais colunas ficam nulas juntas e qual coluna explica isso,
quais textos significam nulo, quais valores são artefato de float e quais categorias são
variantes umas das outras.

## Passo 2. Entender o grão

Antes de somar qualquer coisa, escreva em `analise/decisoes.md` o que uma linha representa.
Se o perfil mostrar colunas nulas juntas explicadas por outra coluna, o arquivo empilha duas
tabelas com grão diferente. Trate cada uma separadamente e descubra como elas se relacionam.

## Passo 3. Responder com scripts, nunca de cabeça

Cada número que pode aparecer na resposta sai de um script em `analise/scripts/` e é
registrado no livro:

```python
import sys

sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")
from numeros import registrar

registrar(
    "vendas.total",
    total,
    "Total vendido no trimestre",
    linhas=len(recorte),
    script=__file__,
    decisoes=["devoluções descontadas"],
)
```

`registrar` recusa NaN e infinito. Se recusar, existe divisão por zero ou nulo no caminho, e
isso é achado, não obstáculo.

Contagens também são números. Se a resposta vai dizer "12 lojas", o 12 vai para o livro.

## Passo 4. Checagens obrigatórias

Faça cada uma e registre o resultado no livro ou em `decisoes.md`:

1. **Linhas antes e depois de todo join.** Se aumentou, uma linha casou com mais de uma.
2. **Dupla contagem.** Uma linha de um lado pode cair em dois recortes do outro? Decida, e
   meça a resposta com e sem a deduplicação.
3. **Mesmo universo.** Os dois lados de uma comparação cobrem o mesmo período e a mesma
   população? Quanto ficou de fora de cada lado, em linhas e em valor?
4. **Reconciliação.** A soma das partes bate com o total?
5. **Denominadores.** Algum é zero, nulo ou ausente?

## Passo 5. Declarar decisões

Toda escolha que muda um número registrado vai para `analise/decisoes.md` nesta forma:

| Decisão | Alternativa | Resultado escolhido | Resultado da alternativa | Por quê |
|---|---|---|---|---|

Rode as duas versões. Uma decisão sem o valor da alternativa não está declarada, está
escondida. Diferença pequena não dispensa o registro: é justamente a que passa sem ninguém ver.

## Passo 6. Conferir antes de responder

Todo texto que sai para o leitor, inclusive a resposta no chat, passa pelo conferidor:

```bash
python3 .claude/skills/analise-de-dados/scripts/numeros.py listar
python3 .claude/skills/analise-de-dados/scripts/conferir_numeros.py entregas/resposta.md
```

Número sem lastro tem dois destinos possíveis: entra no livro com o script que o calcula, ou
sai do texto. Arredondar à mão para caber não é um terceiro destino.

## A resposta

1. Primeiro a resposta direta à pergunta, em uma frase.
2. Depois os números que a sustentam, com a contagem de linhas de cada lado.
3. Depois o que esta análise **não** responde. Se a pergunta tem mais de uma leitura, responda
   a mais provável e diga qual foi a outra.
4. Por último, as decisões de `decisoes.md` que mais movem o resultado.
