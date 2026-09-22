# Pacing das campanhas — Jun/Jul 2024

**Resposta curta: o dinheiro foi entregue quase integralmente (101%), a mídia bruta veio acima do plano (122% de impressões), mas o clique ficou abaixo. E um ponto que provavelmente importa mais que o pacing: metade do gasto do período não está nesse plano.**

## Os números

O plano tem 45 linhas → **44 flights** (duas são duplicata, explico abaixo), **42 com verba orçada**.

| Métrica | Planejado | Realizado | Pacing |
|---|---:|---:|---:|
| Investimento | R$ 1.033.625 | R$ 1.047.334 | **101,3%** |
| Impressões | 137,1 M | 167,4 M | **122,1%** |
| Cliques | 626.766 | 297.275 | **47,4%** |

O 47% de cliques é enganoso: **um único flight** (Freeshop / Meta / Não Sócios) responde por 330.858 dos 626.766 cliques planejados — o plano assumiu CTR de 1,0% e a entrega real foi 0,08%. É premissa de plano irreal, não queda de performance. **Sem esse flight, cliques fecham em 92%.**

## Onde entregou e onde não entregou

**32 dos 42 flights fecharam entre 95% e 105% de investimento.** A execução financeira é disciplinada. Os desvios estão concentrados:

| Situação | Flights | Verba |
|---|---:|---:|
| Abaixo de 95% | 8 | R$ 166.741 planejados → **R$ 67.439 não entregues** |
| Acima de 105% | 2 | **R$ 71.255 gastos a mais** |

Por veículo, o problema é um só:

| Veículo | Pac. Investimento | Pac. Impressões | Pac. Cliques |
|---|---:|---:|---:|
| Meta Ads (29 flights) | 107% | 135% | 48% |
| Youtube Ads (9) | 98% | 83% | 107% |
| **Tiktok Ads (4)** | **48%** | **24%** | **13%** |

**TikTok é o buraco.** R$ 99 mil orçados, R$ 47 mil entregues, e a mídia caiu ainda mais que a verba — ou seja, além de não gastar, o CPM ficou pior que o previsto.

Os casos individuais que puxam os extremos:

- **Inauguracao / TikTok (19–31/07, R$ 24.797) — 0% entregue.** Não existe nenhuma entrega com esse nome de campanha em todo o arquivo. Porém "Uberlandia" rodou no TikTok a partir de 17/07 (R$ 22.004 em julho), **sem constar no plano**. A hipótese forte é que é o mesmo flight, cadastrado com outro nome — vale confirmar com quem operou antes de contar como não-entrega.
- **Impulsionamentos / TikTok / junho — 49%** (R$ 46 mil → R$ 22,3 mil). Esse é subentrega real.
- **Freeshop / Meta / Sócios / Regular — 300%** (R$ 20.900 → R$ 62.700). Uma única linha de campanha, sem sinal de erro de atribuição: ou o plano foi subdimensionado, ou houve remanejamento de verba não registrado.
- **Maceio / Meta / julho — 195%** (R$ 30.888 → R$ 60.343). Mesmo padrão.
- **Joao Pessoa / Youtube / Sócios — 38%.**

## Três coisas do arquivo que você precisa saber

1. **Metade do gasto do período está fora do plano.** Entre 28/05 e 31/07/2024 foram gastos R$ 2.117.850, dos quais só R$ 1.047.334 batem com algum flight. Os outros **R$ 1.070.516** rodaram em 35 pares campanha/veículo sem linha de Planejado — os maiores são Material Didatico (R$ 313 mil no Meta + R$ 144 mil de Influ), Members Mark (R$ 181 mil somados os 3 veículos) e Fds4/Fds5. Pela sua regra eles ficam fora do pacing, e ficaram. Mas isso significa que **esse plano governa ~49% do investimento do próprio período que ele cobre.**

2. **Freeshop / Trade está duplicado no plano:** duas linhas idênticas de R$ 5.000, mesma campanha, veículo, público e modalidade, janelas sobrepostas (18/06–30/06 e 18/06–08/07). Tratei como um grupo só: R$ 10.000 orçados contra R$ 5.000 entregues = 50%. Se for erro de digitação e o correto for R$ 5.000, esse flight na verdade fechou em 100% — e o gap total de subentrega cai de R$ 67 mil para R$ 62 mil.

3. **Dois flights foram planejados sem verba** (Joao Pessoa / Youtube / Não Sócios e Joao Pessoa - Não Pulavel / Youtube): investimento em branco e zero impressões no plano, mas **R$ 9.916 efetivamente entregues**. Não dá para calcular pacing deles; ficaram fora dos totais acima.

## Como calculei

Atribuí cada dia de Realizado ao flight pela chave **Campanha + Veículo + Público + Modalidade**, com a data caindo dentro da janela. Precisei de Público e Modalidade porque três combinações campanha/veículo têm flights sobrepostos no tempo (Freeshop no Meta, Joao Pessoa no Meta e no Youtube) — sem isso a mesma entrega seria contada duas vezes. Onde não há sobreposição, a chave mais fina dá exatamente o mesmo resultado que Campanha + Veículo puro, então ela não muda a regra que você descreveu, só desempata.

Tratei a janela como **inclusiva nos dois extremos**. A coluna `Soma de Dias_Veiculacao` sugere o contrário (é fim menos início), mas testei: com fim inclusivo, 32 dos 42 flights fecham em 95–105% de investimento; com fim exclusivo, só 16, e o realizado total cai R$ 158 mil. A entrega do último dia existe e pertence ao flight.

O detalhamento flight a flight está em `pacing_por_flight.csv`, e o script em `pacing.py`, no mesmo diretório.

## O que eu levaria para a reunião

Operacionalmente, o time entregou: 76% dos flights fecharam no alvo de verba e a mídia veio acima do contratado. Os dois pontos a resolver não são de execução de mídia, são de processo — **a metade do investimento que roda fora do plano**, e o **TikTok**, que é o único veículo com subentrega estrutural. E antes de reportar o "Inauguracao TikTok = 0%", vale checar se não é o Uberlandia TikTok com nome diferente; se for, o número muda de 0% para ~89%.
