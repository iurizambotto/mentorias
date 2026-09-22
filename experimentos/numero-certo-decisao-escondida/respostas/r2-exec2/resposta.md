Analisei o arquivo. Resposta curta: **na parte que estava planejada, a verba foi entregue quase integralmente (101,8%) e a mídia foi entregue acima do previsto em impressões (123%). O "buraco" aparente em cliques (47,6%) é quase todo erro de planejamento, não falha de entrega.**

Mas tem uma ressalva importante antes dos números.

## O arquivo não é uma base de plano vs. realizado

São 16.809 linhas, mas só **45 são "Planejado"** — as outras 16.764 são "Realizado".

| | Cobertura |
|---|---|
| Realizado total na base | R$ 17.075.125 (jan/23 a ago/24) |
| Coberto por alguma linha de plano | R$ 1.047.334 — **6,1%** |
| Período com plano | só jun e jul/2024 (19 campanhas) |

Mesmo dentro de mai–jul/24, o plano cobre só **49%** do que foi gasto (R$ 1,05 mi de R$ 2,12 mi). O resto rodou sem linha planejada — os maiores são Material Didático (R$ 313 mil), Material Didático Influ (R$ 144 mil) e Members Mark (R$ 181 mil somando três veículos).

Então "entregamos o que planejamos?" só dá pra responder para ~6% do investimento da base. Para o resto, não existe plano no arquivo para comparar.

## Na fatia planejada, a entrega foi boa

Comparei cada linha de plano com a soma do realizado da mesma campanha/veículo/público dentro da janela início→término:

| Métrica | Planejado | Realizado | % |
|---|---|---|---|
| Investimento | R$ 1.028.625 | R$ 1.047.334 | **101,8%** |
| Impressões | 135,9 mi | 167,4 mi | **123,2%** |
| Cliques | 624.894 | 297.275 | **47,6%** |

**Disciplina de verba foi alta:** 33 das 42 linhas ficaram dentro de ±5% do orçado.

**O gap de cliques é falso.** 93% dele vem de *uma* linha: Freeshop / Meta / Não Sócios, que planejou 330.858 cliques sobre 33,1 mi de impressões — exatamente **1,00% de CTR**. Todo o resto do plano para prospecção no Meta usa 0,05% a 0,30%, e o realizado dessa linha foi 0,08%, em linha com os pares. Foi premissa errada na planilha. **Tirando essa linha, cliques ficam em 92% do planejado.**

## Os 5 pontos que merecem atenção

1. **"Inauguracao" / TikTok — R$ 24.798 planejados, R$ 0 entregues.** Único plano com entrega zero. Mas provavelmente é rótulo: Uberlândia/TikTok gastou R$ 28.158 entre 17/07 e 09/08 **sem nenhuma linha de plano**. Quase certamente é a mesma compra registrada com outro nome. Vale confirmar antes de reportar como não-entrega.
2. **Maceió / Meta / jul — 195% da verba** (R$ 30.888 → R$ 60.343). Dobrou o orçamento.
3. **Freeshop / Meta / Sócios — 300% da verba** (R$ 20.900 → R$ 62.700). Verifiquei o dia a dia: é gasto real crescente, não duplicação. Orçamento triplicado em voo.
4. **Impulsionamentos / TikTok — 49% em jun e 80% em jul.** Única subentrega consistente de verba, nos dois meses. Junto com João Pessoa/YouTube/Sócios (38%), é o que de fato ficou pra trás.
5. **Cidades no Meta compraram muito mais impressão que o previsto** — Maceió 519%, Fortaleza 352%, Uberlândia 290%, Feira de Santana 214% — com a verba certa. Ou seja, o CPM planejado estava muito acima do real. Não é problema de entrega, é premissa de custo desatualizada.

## Problemas de dados que encontrei

- **Freeshop/Meta/Trade tem duas linhas de plano sobrepostas** (18/06→30/06 e 18/06→08/07), ambas com R$ 5.000 e valores idênticos. O realizado no período é exatamente R$ 5.000. Tratei como **uma** inserção com voo estendido; se somar as duas, a entrega dessa linha cai artificialmente para 50%.
- **Duas linhas de plano sem investimento** (João Pessoa/YouTube/Não Sócios e João Pessoa - Não Pulável/YouTube), com zero planejado mas R$ 3.967 e R$ 5.949 entregues. Ficaram fora do cálculo de %.
- `Modalidade` tem **56 valores distintos** com forte inconsistência de nomenclatura ("Regular Janeiro Fds2 Sulsudeste", "Veraotradesp" etc.). Não afetou esta análise porque os 19 casos planejados usam só 4 categorias limpas, mas inviabiliza cortes por modalidade na base cheia.

---

Em resumo: **onde havia plano, o time entregou** — verba no alvo, mídia acima. As exceções reais são Impulsionamentos/TikTok (subentrega) e Maceió/Freeshop (estouro de verba). O problema maior não é performance, é que **94% do investimento da base não tem plano registrado** para ser cobrado.

Se quiser, exporto a tabela linha a linha das 44 comparações em CSV, ou monto um gráfico de pacing por campanha.
