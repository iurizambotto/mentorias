---
title: "Experimento: o número certo e a decisão escondida"
date: 2026-09-21
type: experimento
status: publicado
tags: [analise-de-dados, inteligencia-artificial, claude-code, experimento]
---

# Experimento: o número certo e a decisão escondida

Material do artigo "Análise de dados com IA: o número certo não basta". Aqui estão os prompts e o
agente de análise usados no experimento, exatamente como rodaram.

## O que foi feito

Uma base de pacing de mídia paga, com planejado e realizado de campanhas em três plataformas, foi
analisada 15 vezes pelo Claude Code, com o modelo Claude Opus 5. A pergunta de negócio foi sempre a
mesma: entregamos o que planejamos?

Foram cinco rodadas, três execuções cada, e cada rodada acrescentou uma camada ao prompt anterior.
Cada execução começou numa sessão nova, num diretório descartável que continha só o arquivo de
dados, sem hooks, servidores MCP nem skills globais. Um único arquivo de instrução global do
ambiente escapou do isolamento, uma referência a um utilitário de terminal sem relação com
análise, e o modelo foi abri-lo em 10 das 15 sessões sem efeito sobre as respostas.

| Rodada | Camada acrescentada | Pacing encontrado nas três execuções |
|---|---|---|
| 1 | Nenhuma | 101,3%, 101,3%, 101,8% |
| 2 | Dicionário de dados | 101,3%, 101,8%, 101,3% |
| 3 | Regra de negócio | 101,3%, 101,3%, 100,8% |
| 4 | Instruções de desconfiança | 100,8%, 101,3%, 100,8% |
| 5 | Agente de análise e pedido de entregáveis | 101,3% e 100,8%, 100,8%, 100,8% |

A escada de contexto não mudou o número. Mudou o que a resposta declara: na rodada 1, duas das três
respostas não dizem como trataram os flights sobrepostos, decisão da qual o número depende; da
rodada 3 em diante, todas dizem. A diferença entre 101,3% e 100,8% vem de uma segunda leitura
legítima, que tira da conta o flight sem verba orçada, e só quem montou o plano desempata.

## Estrutura

```
numero-certo-decisao-escondida/
├── prompts/    o texto literal de cada rodada, com a hipótese registrada antes de rodar
├── dados/      a base de pacing usada nas 15 execuções
├── respostas/  o que cada execução produziu, uma pasta por rodada e execução
└── agente/
    ├── skills/  as quatro skills usadas na rodada 5
    └── tests/   testes dos scripts das skills
```

`respostas/` tem uma pasta por rodada e execução (`r3-exec1`, `r5-exec2`, e assim por diante) com
o que aquela sessão gerou: script e CSV nas rodadas 3 e 4, e o pacote completo de entregáveis
(`entregas/`) e do rastro de análise (`analise/`) na rodada 5. As rodadas 1 e 2 não produzem
arquivo, só resposta em texto, e essa resposta não está publicada aqui: ela vive só na
transcrição de sessão do Claude Code, e publicar a transcrição bruta arrisca levar junto coisa que
não é a resposta, como saída de ferramenta ou raciocínio intermediário sem curadoria.

## O agente de análise

Quatro skills genéricas. Nenhuma conhece o dataset do experimento: não há nelas termo, coluna ou
conclusão da base de mídia. O contexto do negócio vem só do prompt.

| Skill | O que faz |
|---|---|
| `analise-de-dados` | Perfil que não confia na extensão do arquivo, detecção de tabelas misturadas, checagens de contagem dupla e de universo comparado, livro de números e registro de decisões |
| `documento-de-insights` | Documento para quem decide, em DOCX e PDF |
| `dashboard-html` | Dashboard num único HTML que abre sem internet, mais os dados prontos para o Power BI |
| `apresentacao-de-resultados` | Apresentação PPTX com validação mecânica e renderização em imagem para revisão |

Duas regras sustentam o método. Todo número que aparece em qualquer entregável precisa estar no
livro de números, registrado pelo script que o calculou, e o `conferir_numeros.py` reprova o que
não estiver. Toda escolha que muda um número vai para o registro de decisões, com o resultado da
alternativa ao lado.

Na rodada 5, o conferidor leu 865 números nos nove entregáveis das três execuções, e os 865
tinham lastro.

As skills publicadas aqui são as mesmas que rodaram: o hash SHA-256 da pasta `agente/skills`,
calculado sobre caminho e conteúdo de cada arquivo em ordem, é
`bde95b01fd17d264d070d925` nos primeiros 24 caracteres, igual ao registrado no manifesto do run.

## Como usar o agente no seu projeto

As skills de projeto do Claude Code ficam em `.claude/skills/` na raiz do projeto. Copie as quatro
pastas de `agente/skills/` para lá e peça a análise normalmente: o Claude carrega cada skill quando
o pedido combina com a descrição dela.

Os scripts usam Python 3.11 ou mais recente, com `pandas`, `matplotlib`, `python-pptx`,
`python-docx` e `openpyxl`. A conversão para PDF e a renderização dos slides usam o LibreOffice e o
`pdftoppm` quando estão instalados, e são puladas com aviso quando não estão.

Para rodar os testes, a partir desta pasta:

```bash
cd agente
python -m pytest -q
```

## Como cada sessão foi executada

```bash
claude -p "<prompt da rodada>" \
  --model claude-opus-5 \
  --setting-sources project --strict-mcp-config \
  --allowedTools "Bash Read Glob Grep Write Edit Skill" \
  --output-format stream-json --verbose
```

Com a entrada padrão fechada, porque o modo não interativo acrescenta ao prompt o que chega por ela.

## O que não está aqui

- O script que orquestrou as 15 sessões não está publicado.
- A resposta em texto das rodadas 1 e 2, e a narrativa das rodadas 3 e 4, não estão publicadas:
  só o que essas rodadas geraram como arquivo está em `respostas/`.
