"""Passo 8: gera entregas/dashboard.html, um arquivo unico e offline.

Nenhum recurso de rede. Graficos em SVG escrito aqui. Todos os numeros vem do
livro em analise/numeros.json; este script nao recalcula nada.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from numeros import carregar as carregar_livro

SAIDA = Path("entregas/dashboard.html")
DETALHE = Path("analise/blocos_detalhe.csv")

# paleta de referencia da skill dataviz, slots 1 a 3, validada nos dois modos
SERIES = ["var(--series-1)", "var(--series-2)", "var(--series-3)"]


def pct(valor: float, casas: int = 2) -> str:
    return f"{valor * 100:,.{casas}f}".replace(",", " ").replace(".", ",") + "%"


def num(valor: float, casas: int = 0) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def reais(valor: float) -> str:
    return "R$ " + num(valor, 2)


def barras_horizontais(
    itens: list[tuple[str, float]], *, largura: int = 760, altura_barra: int = 26,
    referencia: float = 1.0, maximo: float | None = None, cor: str = SERIES[0],
    titulo_eixo: str = "",
) -> str:
    """Barras horizontais com rotulo direto em cada barra e linha de referencia.

    O rotulo direto e obrigatorio: na paleta clara o slot aqua fica abaixo de 3:1
    contra a superficie, e a regra de relevo exige o valor visivel.
    """
    esquerda, direita, topo, base = 250, 70, 28, 34
    maximo = maximo or max(max(v for _, v in itens), referencia) * 1.08
    largura_plot = largura - esquerda - direita
    altura = topo + len(itens) * altura_barra + base
    escala = lambda v: esquerda + (v / maximo) * largura_plot

    partes = [
        f'<svg viewBox="0 0 {largura} {altura}" role="img" width="100%" '
        f'preserveAspectRatio="xMidYMid meet">'
    ]
    for marca in [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]:
        if marca > maximo:
            break
        x = escala(marca)
        partes.append(f'<line x1="{x:.1f}" y1="{topo}" x2="{x:.1f}" y2="{altura - base}" class="grade"/>')
        partes.append(f'<text x="{x:.1f}" y="{altura - base + 16}" class="eixo" text-anchor="middle">{pct(marca, 0)}</text>')

    # os rotulos sao desenhados depois da linha de referencia, senao ela corta o texto
    rotulos: list[str] = []
    for i, (rotulo, valor) in enumerate(itens):
        y = topo + i * altura_barra
        h = altura_barra - 8
        largura_barra = max(escala(valor) - esquerda, 1.5)
        partes.append(
            f'<rect x="{esquerda}" y="{y}" width="{largura_barra:.1f}" height="{h}" '
            f'rx="4" fill="{cor}"><title>{html.escape(rotulo)}: {pct(valor)}</title></rect>'
        )
        rotulos.append(
            f'<text x="{esquerda - 10}" y="{y + h - 5}" class="rotulo" text-anchor="end">{html.escape(rotulo)}</text>'
        )
        rotulos.append(
            f'<text x="{esquerda + largura_barra + 7:.1f}" y="{y + h - 5}" class="valor">{pct(valor, 1)}</text>'
        )

    x_ref = escala(referencia)
    partes.append(f'<line x1="{x_ref:.1f}" y1="{topo - 6}" x2="{x_ref:.1f}" y2="{altura - base}" class="referencia"/>')
    partes.append(f'<text x="{x_ref:.1f}" y="{topo - 12}" class="eixo" text-anchor="middle">meta do plano</text>')
    partes.extend(rotulos)
    if titulo_eixo:
        partes.append(f'<text x="{largura / 2:.0f}" y="{altura - 4}" class="eixo" text-anchor="middle">{html.escape(titulo_eixo)}</text>')
    partes.append("</svg>")
    return "".join(partes)


def barras_agrupadas(
    grupos: list[str], series: list[tuple[str, list[float]]], *,
    largura: int = 760, altura: int = 300, referencia: float = 1.0,
) -> str:
    """Um eixo so. Cada grupo recebe uma barra por serie, com rotulo direto."""
    esquerda, direita, topo, base = 56, 20, 30, 56
    maximo = max(max(v for v in valores) for _, valores in series) * 1.18
    maximo = max(maximo, referencia * 1.15)
    largura_plot = largura - esquerda - direita
    altura_plot = altura - topo - base
    passo = largura_plot / len(grupos)
    largura_barra = min(46, (passo - 18) / len(series))
    escala = lambda v: topo + altura_plot - (v / maximo) * altura_plot

    partes = [f'<svg viewBox="0 0 {largura} {altura}" role="img" width="100%" preserveAspectRatio="xMidYMid meet">']
    for marca in [0, 0.5, 1.0, 1.5, 2.0]:
        if marca > maximo:
            break
        y = escala(marca)
        partes.append(f'<line x1="{esquerda}" y1="{y:.1f}" x2="{largura - direita}" y2="{y:.1f}" class="grade"/>')
        partes.append(f'<text x="{esquerda - 8}" y="{y + 4:.1f}" class="eixo" text-anchor="end">{pct(marca, 0)}</text>')

    y_ref = escala(referencia)
    partes.append(f'<line x1="{esquerda}" y1="{y_ref:.1f}" x2="{largura - direita}" y2="{y_ref:.1f}" class="referencia"/>')

    for g, grupo in enumerate(grupos):
        centro = esquerda + passo * (g + 0.5)
        total = len(series) * largura_barra + (len(series) - 1) * 2  # 2px de respiro entre barras
        x0 = centro - total / 2
        for s, (nome, valores) in enumerate(series):
            valor = valores[g]
            x = x0 + s * (largura_barra + 2)
            y = escala(valor)
            h = max(topo + altura_plot - y, 1.5)
            partes.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{largura_barra:.1f}" height="{h:.1f}" rx="4" '
                f'fill="{SERIES[s]}"><title>{html.escape(grupo)} · {html.escape(nome)}: {pct(valor)}</title></rect>'
            )
            partes.append(
                f'<text x="{x + largura_barra / 2:.1f}" y="{y - 6:.1f}" class="valor" text-anchor="middle">{pct(valor, 0)}</text>'
            )
        partes.append(
            f'<text x="{centro:.1f}" y="{topo + altura_plot + 20:.1f}" class="rotulo" text-anchor="middle">{html.escape(grupo)}</text>'
        )
    partes.append("</svg>")
    return "".join(partes)


def par_planejado_realizado(rotulo: str, planejado: float, realizado: float, formatar) -> str:
    """Duas barras numa escala propria. Duas medidas de grandeza diferente ficam em
    graficos separados, nunca em dois eixos no mesmo grafico."""
    largura, altura = 340, 170
    esquerda, base, topo = 20, 46, 26
    maximo = max(planejado, realizado) * 1.25
    altura_plot = altura - topo - base
    escala = lambda v: topo + altura_plot - (v / maximo) * altura_plot
    partes = [f'<svg viewBox="0 0 {largura} {altura}" role="img" width="100%" preserveAspectRatio="xMidYMid meet">']
    for i, (nome, valor, cor) in enumerate([("planejado", planejado, SERIES[0]), ("realizado", realizado, SERIES[1])]):
        x = esquerda + 60 + i * 130
        y = escala(valor)
        h = max(topo + altura_plot - y, 1.5)
        partes.append(f'<rect x="{x}" y="{y:.1f}" width="72" height="{h:.1f}" rx="4" fill="{cor}">'
                      f'<title>{nome}: {formatar(valor)}</title></rect>')
        partes.append(f'<text x="{x + 36}" y="{y - 7:.1f}" class="valor" text-anchor="middle">{formatar(valor)}</text>')
        partes.append(f'<text x="{x + 36}" y="{topo + altura_plot + 19:.1f}" class="rotulo" text-anchor="middle">{nome}</text>')
    partes.append(f'<text x="{largura / 2:.0f}" y="{altura - 8}" class="eixo" text-anchor="middle">{html.escape(rotulo)}</text>')
    partes.append("</svg>")
    return "".join(partes)


def indicador(valor: str, titulo: str, comparacao: str, base: str, tom: str) -> str:
    return (
        f'<div class="kpi kpi--{tom}"><p class="kpi__titulo">{html.escape(titulo)}</p>'
        f'<p class="kpi__valor">{valor}</p>'
        f'<p class="kpi__comp">{comparacao}</p>'
        f'<p class="kpi__base">{html.escape(base)}</p></div>'
    )


def legenda(nomes: list[str]) -> str:
    itens = "".join(
        f'<span class="leg__item"><span class="leg__marca" style="background:{SERIES[i]}"></span>{html.escape(n)}</span>'
        for i, n in enumerate(nomes)
    )
    return f'<div class="leg">{itens}</div>'


def main() -> int:
    livro = carregar_livro()
    v = {chave: item["valor"] for chave, item in livro.items()}
    detalhe = pd.read_csv(DETALHE)

    kpis = "".join([
        indicador(pct(v["pacing.investimento"]), "Investimento", "entregue sobre o planejado",
                  f'base: {livro["pacing.investimento"]["linhas"]} blocos de plano', "ok"),
        indicador(pct(v["pacing.impressoes"]), "Impressoes", "entregue sobre o planejado",
                  f'base: {livro["pacing.impressoes"]["linhas"]} blocos de plano', "acima"),
        indicador(pct(v["pacing.cliques"]), "Cliques", "entregue sobre o planejado",
                  f'base: {livro["pacing.cliques"]["linhas"]} blocos de plano', "critico"),
        indicador(pct(v["real.share_investimento_no_pacing"]), "Cobertura do plano",
                  "do investimento realizado tem plano",
                  f'base: {livro["real.share_investimento_no_pacing"]["linhas"]} linhas de entrega', "alerta"),
    ])

    g1 = barras_horizontais(
        [("Investimento", v["pacing.investimento"]), ("Impressoes", v["pacing.impressoes"]),
         ("Cliques", v["pacing.cliques"])],
        altura_barra=44, cor=SERIES[0], titulo_eixo="pacing, realizado sobre planejado",
    )

    veiculos = ["Meta Ads", "Youtube Ads", "Tiktok Ads"]
    chaves = ["meta", "youtube", "tiktok"]
    g2 = barras_agrupadas(
        veiculos,
        [("Investimento", [v[f"veiculo.{k}.pacing_investimento"] for k in chaves]),
         ("Impressoes", [v[f"veiculo.{k}.pacing_impressoes"] for k in chaves]),
         ("Cliques", [v[f"veiculo.{k}.pacing_cliques"] for k in chaves])],
    )

    campanhas = (detalhe.dropna(subset=["pacing_impressoes"])
                 .groupby("Campanha")[["plan_Soma de Impressoes", "real_Soma de Impressoes"]].sum())
    campanhas["pacing"] = campanhas["real_Soma de Impressoes"] / campanhas["plan_Soma de Impressoes"]
    g3 = barras_horizontais(
        [(c, float(p)) for c, p in campanhas["pacing"].sort_values().items()],
        cor=SERIES[0], titulo_eixo="pacing de impressoes, realizado sobre planejado",
    )

    g4 = par_planejado_realizado("custo por mil impressoes", v["plan.cpm"], v["real.cpm"], reais)
    g5 = par_planejado_realizado("taxa de clique", v["plan.ctr"], v["real.ctr"], lambda x: pct(x, 2))

    linhas_tabela = []
    for _, r in detalhe.iterrows():
        pacing_imp = "sem meta" if pd.isna(r["pacing_impressoes"]) else pct(r["pacing_impressoes"], 1)
        pacing_cli = "sem meta" if pd.isna(r["pacing_cliques"]) else pct(r["pacing_cliques"], 1)
        pacing_inv = "sem meta" if pd.isna(r["pacing_investimento"]) else pct(r["pacing_investimento"], 1)
        ordenacao = -1 if pd.isna(r["pacing_impressoes"]) else r["pacing_impressoes"]
        linhas_tabela.append(
            f'<tr><td>{html.escape(r["Campanha"])}</td><td>{html.escape(r["Veiculo"])}</td>'
            f'<td class="n">{r["inicio"][:10]}</td><td class="n">{r["termino"][:10]}</td>'
            f'<td class="n" data-v="{r["n_flights"]}">{r["n_flights"]}</td>'
            f'<td class="n" data-v="{r["dias_entrega"]}">{r["dias_entrega"]}</td>'
            f'<td class="n" data-v="{ordenacao}">{pacing_inv}</td>'
            f'<td class="n" data-v="{ordenacao}">{pacing_imp}</td>'
            f'<td class="n" data-v="{ordenacao}">{pacing_cli}</td></tr>'
        )

    html_saida = TEMPLATE.format(
        kpis=kpis, g1=g1, g2=g2, g3=g3, g4=g4, g5=g5,
        legenda_veiculo=legenda(["Investimento", "Impressoes", "Cliques"]),
        legenda_par=legenda(["Planejado", "Realizado"]),
        tabela="".join(linhas_tabela),
        n_blocos=len(detalhe),
        linhas_dentro=num(v["real.linhas_no_pacing"]),
        linhas_fora=num(v["real.linhas_fora"]),
        linhas_total=num(v["real.linhas"]),
        flights=num(v["plan.flights"]),
        multi=num(v["real.linhas_em_multiplos_flights"]),
        inflacao=pct(v["alt.inflacao_sem_dedup_impressoes"], 2),
        sem_dedup=pct(v["alt.pacing_sem_dedup_impressoes"], 2),
        campanhas_sem_plano=num(v["real.campanhas_sem_plano"]),
        invest_fora=reais(v["real.investimento_fora"]),
        cobertura=pct(v["real.share_investimento_no_pacing"]),
        gap_cliques=num(v["gap.cliques"]),
    )
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(html_saida, encoding="utf-8")
    print(f"gravado {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} KB)")
    return 0


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pacing de campanhas | mai-jul 2024</title>
<style>
:root {{
  color-scheme: light;
  --plano: #f9f9f7; --superficie: #fcfcfb; --borda: #e1e0d9;
  --ink: #0b0b0b; --ink2: #52514e; --mudo: #898781; --grade: #e1e0d9; --eixo: #c3c2b7;
  --series-1: #2a78d6; --series-2: #eb6834; --series-3: #1baf7a;
  --bom: #0ca30c; --alerta: #fab219; --critico: #d03b3b;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    color-scheme: dark;
    --plano: #0d0d0d; --superficie: #1a1a19; --borda: #2c2c2a;
    --ink: #ffffff; --ink2: #c3c2b7; --mudo: #898781; --grade: #2c2c2a; --eixo: #383835;
    --series-1: #3987e5; --series-2: #d95926; --series-3: #199e70;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 28px 20px 56px; background: var(--plano); color: var(--ink);
  font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}}
.wrap {{ max-width: 1080px; margin: 0 auto; }}
h1 {{ font-size: 25px; line-height: 1.25; margin: 0 0 6px; letter-spacing: -.015em; }}
.sub {{ color: var(--ink2); margin: 0 0 6px; font-size: 16px; }}
.periodo {{ color: var(--mudo); margin: 0 0 26px; font-size: 13px; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 30px; }}
.kpi {{
  background: var(--superficie); border: 1px solid var(--borda); border-radius: 10px;
  padding: 15px 16px; border-top: 3px solid var(--mudo);
}}
.kpi--ok {{ border-top-color: var(--bom); }}
.kpi--acima {{ border-top-color: var(--series-1); }}
.kpi--alerta {{ border-top-color: var(--alerta); }}
.kpi--critico {{ border-top-color: var(--critico); }}
.kpi__titulo {{ margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: .07em; color: var(--mudo); }}
.kpi__valor {{ margin: 7px 0 3px; font-size: 30px; font-weight: 640; letter-spacing: -.02em; }}
.kpi__comp {{ margin: 0; font-size: 13px; color: var(--ink2); }}
.kpi__base {{ margin: 5px 0 0; font-size: 11.5px; color: var(--mudo); }}
.card {{
  background: var(--superficie); border: 1px solid var(--borda); border-radius: 10px;
  padding: 19px 20px 15px; margin-bottom: 20px;
}}
.card h2 {{ font-size: 17px; margin: 0 0 3px; letter-spacing: -.01em; }}
.card p.nota {{ margin: 0 0 14px; color: var(--ink2); font-size: 13.5px; }}
.dupla {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
.grade {{ stroke: var(--grade); stroke-width: 1; }}
.referencia {{ stroke: var(--ink2); stroke-width: 1.5; stroke-dasharray: 5 3; }}
text {{ font-family: inherit; }}
.eixo {{ font-size: 11px; fill: var(--mudo); }}
.rotulo {{ font-size: 12.5px; fill: var(--ink2); }}
/* halo na cor da superficie para o valor continuar legivel sobre a linha de referencia */
.valor {{
  font-size: 12px; fill: var(--ink); font-weight: 600;
  paint-order: stroke fill; stroke: var(--superficie); stroke-width: 3px; stroke-linejoin: round;
}}
.leg {{ display: flex; flex-wrap: wrap; gap: 16px; margin: 8px 0 2px; font-size: 12.5px; color: var(--ink2); }}
.leg__item {{ display: inline-flex; align-items: center; gap: 6px; }}
.leg__marca {{ width: 11px; height: 11px; border-radius: 3px; display: inline-block; }}
.ferramentas {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }}
input[type=search] {{
  flex: 1 1 240px; padding: 8px 11px; border: 1px solid var(--borda); border-radius: 7px;
  background: var(--plano); color: var(--ink); font: inherit; font-size: 14px;
}}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th, td {{ padding: 7px 9px; text-align: left; border-bottom: 1px solid var(--borda); }}
th {{
  cursor: pointer; user-select: none; font-size: 11.5px; text-transform: uppercase;
  letter-spacing: .05em; color: var(--mudo); white-space: nowrap; position: sticky; top: 0;
  background: var(--superficie);
}}
th:hover {{ color: var(--ink); }}
td.n, th.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
.rolagem {{ max-height: 470px; overflow: auto; border: 1px solid var(--borda); border-radius: 8px; }}
.leitura {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
.leitura ul {{ margin: 6px 0 0; padding-left: 19px; }}
.leitura li {{ margin-bottom: 7px; color: var(--ink2); font-size: 13.5px; }}
footer {{ color: var(--mudo); font-size: 12px; margin-top: 26px; line-height: 1.7; }}
code {{ font-size: 11.5px; background: var(--superficie); padding: 1px 5px; border-radius: 4px; border: 1px solid var(--borda); }}
@media (max-width: 700px) {{
  .kpis, .dupla, .leitura {{ grid-template-columns: 1fr; }}
  h1 {{ font-size: 21px; }}
}}
</style>
</head>
<body>
<div class="wrap">

<h1>Entregamos o que foi planejado?</h1>
<p class="sub">O dinheiro sim, a audiencia veio acima, o clique ficou pela metade.</p>
<p class="periodo">Plano de 2024-05-28 a 2024-07-31 &middot; {flights} flights reunidos em {n_blocos} blocos &middot; {linhas_dentro} linhas de entrega na conta</p>

<div class="kpis">{kpis}</div>

<div class="card">
  <h2>A verba foi cumprida, a audiencia sobrou e o clique faltou</h2>
  <p class="nota">Tres respostas diferentes para a mesma campanha. Faltaram {gap_cliques} cliques que estavam no plano.</p>
  {g1}
</div>

<div class="card">
  <h2>O TikTok ficou abaixo da meta nas tres metricas</h2>
  <p class="nota">Meta Ads trouxe volume sem clique, YouTube trouxe clique sem volume, TikTok nao entregou nenhum dos dois.</p>
  {legenda_veiculo}
  {g2}
</div>

<div class="card">
  <h2>A midia veio mais barata e menos engajada que o plano supunha</h2>
  <p class="nota">Duas medidas de grandezas diferentes, em dois graficos com escalas proprias. O preco menor explica a audiencia extra; a taxa de clique menor explica o clique que faltou.</p>
  {legenda_par}
  <div class="dupla">{g4}{g5}</div>
</div>

<div class="card">
  <h2>Por campanha, o resultado vai de zero a quase o triplo da meta</h2>
  <p class="nota">Inauguracao tinha verba e janela reservadas no TikTok e nao registrou nenhum dia de entrega.</p>
  {g3}
</div>

<div class="card">
  <h2>Detalhe por bloco de plano</h2>
  <p class="nota">Filtre por campanha ou veiculo, clique no cabecalho para ordenar. "Sem meta" marca o bloco cujo plano nao tem valor para dividir.</p>
  <div class="ferramentas">
    <input type="search" id="filtro" placeholder="filtrar por campanha ou veiculo" aria-label="filtrar a tabela">
  </div>
  <div class="rolagem">
  <table id="tab">
    <thead><tr>
      <th>Campanha</th><th>Veiculo</th><th class="n">Inicio</th><th class="n">Termino</th>
      <th class="n">Flights</th><th class="n">Dias</th>
      <th class="n">Investimento</th><th class="n">Impressoes</th><th class="n">Cliques</th>
    </tr></thead>
    <tbody>{tabela}</tbody>
  </table>
  </div>
</div>

<div class="card leitura">
  <div>
    <h2>Como ler este painel</h2>
    <ul>
      <li>Pacing e o realizado dividido pelo planejado. Acima da linha tracejada, a entrega passou da meta.</li>
      <li>So entra na conta a entrega que caiu dentro da janela do flight e no mesmo veiculo.</li>
      <li>O plano tem trechos em que duas ou mais reservas da mesma campanha e veiculo cobrem o mesmo dia. Sao {multi} linhas de entrega nessa situacao, e cada uma conta uma vez so. Sem esse cuidado o pacing de impressoes daria {sem_dedup} em vez do valor mostrado, {inflacao} a mais.</li>
      <li>Cada flight sobreposto nao aparece sozinho: eles viram um bloco unico, porque nao ha como dizer a qual deles um dia dentro da sobreposicao pertence.</li>
    </ul>
  </div>
  <div>
    <h2>O que este painel nao mostra</h2>
    <ul>
      <li>Resultado de negocio. O arquivo tem midia entregue, nao venda nem conversao.</li>
      <li>A operacao inteira. O plano cobre {cobertura} do investimento realizado no arquivo; {campanhas_sem_plano} campanhas rodaram sem plano, somando {invest_fora} fora da conta.</li>
      <li>O motivo da queda de engajamento. Criativo, segmentacao e leilao nao estao no arquivo.</li>
      <li>Pacing de flight isolado nos tres blocos sobrepostos.</li>
    </ul>
  </div>
</div>

<footer>
  Dados: <code>BASE DE PACING_v2.csv.xls</code>, {linhas_total} linhas de entrega diaria e {flights} de plano.
  {linhas_dentro} entram no pacing e {linhas_fora} ficam fora.<br>
  Gerado por <code>analise/scripts/08_dashboard.py</code> a partir de <code>analise/numeros.json</code>.
  Reproducao e decisoes de metodo em <code>analise/decisoes.md</code>.
</footer>

</div>
<script>
(function () {{
  var tab = document.getElementById('tab');
  var corpo = tab.tBodies[0];
  var filtro = document.getElementById('filtro');

  filtro.addEventListener('input', function () {{
    var termo = filtro.value.toLowerCase();
    Array.prototype.forEach.call(corpo.rows, function (linha) {{
      var texto = (linha.cells[0].textContent + ' ' + linha.cells[1].textContent).toLowerCase();
      linha.style.display = texto.indexOf(termo) === -1 ? 'none' : '';
    }});
  }});

  var ordem = {{}};
  Array.prototype.forEach.call(tab.tHead.rows[0].cells, function (cabecalho, i) {{
    cabecalho.addEventListener('click', function () {{
      var asc = !ordem[i];
      ordem = {{}};
      ordem[i] = asc;
      var linhas = Array.prototype.slice.call(corpo.rows);
      linhas.sort(function (a, b) {{
        var ca = a.cells[i], cb = b.cells[i];
        var va = ca.dataset.v, vb = cb.dataset.v;
        if (va !== undefined && vb !== undefined) {{
          return (asc ? 1 : -1) * (parseFloat(va) - parseFloat(vb));
        }}
        return (asc ? 1 : -1) * ca.textContent.localeCompare(cb.textContent, 'pt-BR');
      }});
      linhas.forEach(function (l) {{ corpo.appendChild(l); }});
    }});
  }});
}})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    raise SystemExit(main())
