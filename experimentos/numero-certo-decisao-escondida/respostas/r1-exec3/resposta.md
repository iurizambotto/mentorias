Analisei o `BASE DE PACING_v2.csv.xls` (16.809 linhas). Antes do resultado, um ponto que muda a leitura da pergunta:

## O plano cobre só um pedaço da operação

- **45 linhas são `Planejado`**, todas em **jun–jul/2024**, 19 campanhas, **R$ 1,03 mi**.
- **16.764 linhas são `Realizado`**, diárias, de **jan/2023 a 09/ago/2024**, R$ 17,1 mi.
- Dentro da própria janela jun–jul/24 foram gastos **R$ 1,89 mi** — ou seja, **46% do dinheiro do período (R$ 864 mil) não tem nenhuma linha de plano nesta base** (Material Didático R$ 313k, Material Didático Influ R$ 144k, os YouTubes de Members Mark/Parceiros ~R$ 63k cada, Fds4, Resgate de Cupom...).

Então "entregamos o que planejamos?" só é respondível para jun–jul/24 e para ~54% da verba do período. Todo o resto abaixo é sobre esse recorte, casando plano × realizado por campanha + veículo + objetivo + público + modalidade dentro da janela de flight.

## Resposta curta: sim em verba, sim em impressão, não em cliques

| Métrica | Planejado | Realizado | Pacing |
|---|---|---|---|
| Investimento | R$ 1.028.625 | R$ 1.047.334 | **102%** |
| Impressões | 135,9 mi | 167,4 mi | **123%** |
| Cliques | 624.894 | 297.275 | **48%** |

- **Verba: entrega quase cirúrgica.** 33 das 44 linhas ficaram entre 95% e 105% do budget. Dinheiro planejado foi dinheiro gasto.
- **Impressão: entregou acima porque o meio ficou mais barato.** CPM planejado R$ 7,57 → realizado **R$ 6,26** (17% mais barato).
- **Cliques: o 48% é falso alarme.** A linha Freeshop/Meta/não-sócios foi planejada com CTR de 1%, enquanto todo o resto do plano usa 0,2%–0,25%. Ela sozinha é 53% da meta de cliques e entregou 8%. **Tirando essa linha, cliques ficam em 92%** — dentro do aceitável. O problema é premissa de planejamento, não entrega.

## O que realmente não foi entregue

1. **`Inauguracao` / TikTok (19–31/jul): R$ 24,8 mil planejados, R$ 0 entregues.** Único caso de entrega zerada. Mas no mesmo TikTok em jul aparece **`Uberlandia` gastando R$ 22 mil (17/jul a 09/ago) sem nenhuma linha de plano**. Muito provavelmente é o mesmo dinheiro, lançado com nome diferente no realizado. **Vale confirmar com o time antes de reportar como não-entrega.**
2. **`Impulsionamentos`: 82% da verba (R$ 30 mil não gastos).** Essa é a subentrega real. O buraco está no TikTok/Video Views de junho: 49% da verba, 27% das impressões, rodou **19 dos 29 dias** previstos. A linha de julho também parou em 20 de 30 dias.
3. **TikTok como um todo entregou 48% da verba planejada** (24% das impressões). Excluindo a linha `Inauguracao`, vai para 64%; se o gasto de Uberlândia for mesmo ela, ~93%. Meta ficou em 108% e YouTube em 107%.

## Estouros (compensam o total em 102%)

- **`Freeshop`: 133% da verba, R$ 42 mil acima.** A linha sócios/regular gastou R$ 62,7 mil contra R$ 20,9 mil planejados (3x) — mesmo `campaign_name`, entrega proporcional, então foi remanejamento de verba, não erro de base.
- **`Maceio`: 134%,** R$ 29 mil a mais concentrados no Meta de julho (R$ 60,3k vs R$ 30,9k).
- **R$ 9,9 mil rodaram sem plano** em `Joao Pessoa`/YouTube e `Joao Pessoa - Não Pulável` (as duas linhas existem no plano com impressão 0 e investimento em branco).

## Onde o planejamento errou mais que a execução

Só **7 das 44 linhas** ficaram dentro de ±10% em impressões — 14 abaixo de 90% e **21 acima de 110%**. Com a verba batendo em 100%, isso significa que o problema é a **calibragem de CPM/CTR do plano**, não o pacing da mídia. E o erro é sistemático por veículo: **18 das 29 linhas de Meta estouraram +10%** (Fortaleza 352%, Maceió jun 519%, Uberlândia 290%), enquanto **7 das 11 linhas de YouTube entregaram ≤100%** (Feira de Santana 64%, João Pessoa sócios 19%). O CPM de Meta está superestimado e o de YouTube subestimado no plano.

## Dois defeitos na base, para corrigir antes do próximo ciclo

- **Linha de plano duplicada:** Freeshop/Trade/sócios aparece duas vezes com os mesmos R$ 5 mil e 1,25 mi de impressões, com janelas sobrepostas (18–30/jun e 18/06–08/07). Infla o plano. Já removi da consolidação acima.
- **`campaign_name` só existe no realizado** (vazio nas 45 linhas de plano). O casamento plano×realizado depende de o campo `Campanha` ser escrito igual dos dois lados — que é exatamente o que quebrou no caso `Inauguracao`/`Uberlandia`.

Deixei a tabela linha a linha em `/tmp/pacing_linha.csv` se quiser conferir campanha por campanha.
