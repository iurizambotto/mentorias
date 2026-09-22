"""Passo 8: gera entregas/dashboard.html, um arquivo unico e offline.

Os indicadores saem do livro de numeros; nada e recalculado aqui. Os graficos
sao SVG escrito no proprio script, sem biblioteca e sem recurso de rede, para
que o arquivo abra como anexo de email daqui a anos.

Paleta: instancia de referencia da skill dataviz (slots categoricos 1 e 2,
cinzas de eixo e grade, cores de status), com passo proprio para tema escuro.
"""

from __future__ import annotations

import html
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import ARQUIVO  # noqa: F401
from numeros import carregar as carregar_livro

RAIZ = Path(__file__).resolve().parents[1]
SAIDA = RAIZ.parent / "entregas" / "dashboard.html"

livro = carregar_livro()


def n(chave: str) -> float:
    return livro[chave]["valor"]


def brl(v: float, casas: int = 2) -> str:
    txt = f"{v:,.{casas}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return f"R$ {txt}"


def num(v: float, casas: int = 0) -> str:
    return f"{v:,.{casas}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def pct(v: float, casas: int = 2) -> str:
    return f"{num(v, casas)}%"


def esc(s: str) -> str:
    return html.escape(str(s))


def slug(texto: str) -> str:
    sem = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "-" for c in sem.lower()).strip("-")


valido = pd.read_csv(RAIZ / "pacing_valido.csv")
porc = pd.read_csv(RAIZ / "pacing_por_campanha.csv")
porv = pd.read_csv(RAIZ / "pacing_por_veiculo.csv")
diaria = pd.read_csv(RAIZ / "serie_diaria.csv", parse_dates=["Data"])

# ---------------------------------------------------------------- graficos

EIXO = "var(--axis)"
GRADE = "var(--grid)"
TINTA = "var(--ink-muted)"


def faixa_status(p: float) -> str:
    if p < n("faixa.limite_inferior"):
        return "critical"
    if p > n("faixa.limite_superior"):
        return "warning"
    return "good"


def barras_pacing(dados: list[tuple[str, float]], largura: int = 640, alt_barra: int = 44) -> str:
    """Barras horizontais de pacing com linha de referencia em 100%."""
    esq, dir_, topo = 150, 70, 18
    alt = topo + len(dados) * alt_barra + 34
    plot = largura - esq - dir_
    teto = max(140.0, max(v for _, v in dados) * 1.08)
    x = lambda v: esq + v / teto * plot  # noqa: E731

    p = [f'<svg viewBox="0 0 {largura} {alt}" role="img" width="100%" height="{alt}">']
    for marca in (0, 50, 100):
        if marca <= teto:
            p.append(f'<line x1="{x(marca):.1f}" y1="{topo}" x2="{x(marca):.1f}" y2="{topo + len(dados) * alt_barra}" stroke="{GRADE}" stroke-width="1"/>')
            p.append(f'<text x="{x(marca):.1f}" y="{alt - 12}" fill="{TINTA}" font-size="11" text-anchor="middle">{marca}%</text>')
    for i, (rotulo, valor) in enumerate(dados):
        y = topo + i * alt_barra + 8
        h = alt_barra - 20
        cor = f"var(--status-{faixa_status(valor)})"
        p.append(f'<rect x="{esq}" y="{y}" width="{max(2.0, x(valor) - esq):.1f}" height="{h}" rx="4" fill="{cor}"/>')
        p.append(f'<text x="{esq - 10}" y="{y + h / 2 + 4:.1f}" fill="var(--ink-1)" font-size="12.5" text-anchor="end">{esc(rotulo)}</text>')
        p.append(f'<text x="{x(valor) + 8:.1f}" y="{y + h / 2 + 4:.1f}" fill="var(--ink-2)" font-size="12.5" font-weight="600">{pct(valor, 1)}</text>')
    # Linha de 100% por cima das barras, que e a leitura principal.
    p.append(f'<line x1="{x(100):.1f}" y1="{topo - 6}" x2="{x(100):.1f}" y2="{topo + len(dados) * alt_barra + 2}" stroke="var(--ink-1)" stroke-width="2" stroke-dasharray="5 4"/>')
    p.append(f'<text x="{x(100):.1f}" y="{topo - 10}" fill="var(--ink-2)" font-size="11" text-anchor="middle">plano</text>')
    p.append("</svg>")
    return "".join(p)


def barras_agrupadas(cats: list[str], s1: list[float], s2: list[float], nomes: tuple[str, str], largura: int = 640) -> str:
    """Duas series lado a lado, em reais. Gap de 2px entre barras adjacentes."""
    esq, dir_, topo, base = 78, 16, 22, 46
    alt = 300
    plot_l, plot_a = largura - esq - dir_, alt - topo - base
    teto = max(max(s1), max(s2)) * 1.15
    passo = plot_l / len(cats)
    y = lambda v: topo + plot_a - v / teto * plot_a  # noqa: E731

    p = [f'<svg viewBox="0 0 {largura} {alt}" role="img" width="100%" height="{alt}">']
    for k in range(5):
        v = teto * k / 4
        yy = y(v)
        p.append(f'<line x1="{esq}" y1="{yy:.1f}" x2="{largura - dir_}" y2="{yy:.1f}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<text x="{esq - 8}" y="{yy + 4:.1f}" fill="{TINTA}" font-size="11" text-anchor="end">{num(v / 1000)}k</text>')
    lb = min(46.0, passo / 2 - 7)
    for i, cat in enumerate(cats):
        cx = esq + passo * i + passo / 2
        for j, (serie, cor) in enumerate([(s1, "var(--series-1)"), (s2, "var(--series-2)")]):
            bx = cx - lb - 1 + j * (lb + 2)
            p.append(f'<rect x="{bx:.1f}" y="{y(serie[i]):.1f}" width="{lb:.1f}" height="{max(2.0, topo + plot_a - y(serie[i])):.1f}" rx="4" fill="{cor}"/>')
        p.append(f'<text x="{cx:.1f}" y="{topo + plot_a + 18:.1f}" fill="var(--ink-1)" font-size="12" text-anchor="middle">{esc(cat)}</text>')
        p.append(f'<text x="{cx:.1f}" y="{topo + plot_a + 34:.1f}" fill="{TINTA}" font-size="11" text-anchor="middle">{pct(s2[i] / s1[i] * 100, 1)}</text>')
    p.append(f'<line x1="{esq}" y1="{topo + plot_a}" x2="{largura - dir_}" y2="{topo + plot_a}" stroke="{EIXO}" stroke-width="1"/>')
    p.append("</svg>")
    legenda = (
        f'<div class="legenda"><span><i style="background:var(--series-1)"></i>{esc(nomes[0])}</span>'
        f'<span><i style="background:var(--series-2)"></i>{esc(nomes[1])}</span></div>'
    )
    return "".join(p) + legenda


def linha_diaria(datas: list[str], valores: list[float], largura: int = 640) -> str:
    """Serie diaria com camada de hover: crosshair e tooltip."""
    esq, dir_, topo, base = 70, 16, 20, 40
    alt = 280
    plot_l, plot_a = largura - esq - dir_, alt - topo - base
    teto = max(valores) * 1.12
    x = lambda i: esq + (plot_l * i / max(1, len(datas) - 1))  # noqa: E731
    y = lambda v: topo + plot_a - v / teto * plot_a  # noqa: E731

    p = [f'<svg viewBox="0 0 {largura} {alt}" role="img" width="100%" height="{alt}" class="svg-hover" data-plot="{esq},{topo},{plot_l},{plot_a}">']
    for k in range(5):
        v = teto * k / 4
        yy = y(v)
        p.append(f'<line x1="{esq}" y1="{yy:.1f}" x2="{largura - dir_}" y2="{yy:.1f}" stroke="{GRADE}" stroke-width="1"/>')
        p.append(f'<text x="{esq - 8}" y="{yy + 4:.1f}" fill="{TINTA}" font-size="11" text-anchor="end">{num(v / 1000)}k</text>')
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(valores))
    p.append(f'<polyline points="{pts}" fill="none" stroke="var(--series-1)" stroke-width="2" stroke-linejoin="round"/>')
    passo_rot = max(1, len(datas) // 8)
    for i, d in enumerate(datas):
        if i % passo_rot == 0:
            p.append(f'<text x="{x(i):.1f}" y="{topo + plot_a + 18:.1f}" fill="{TINTA}" font-size="10.5" text-anchor="middle">{d[8:10]}/{d[5:7]}</text>')
    p.append(f'<line x1="{esq}" y1="{topo + plot_a}" x2="{largura - dir_}" y2="{topo + plot_a}" stroke="{EIXO}" stroke-width="1"/>')
    p.append(f'<line class="crosshair" x1="0" y1="{topo}" x2="0" y2="{topo + plot_a}" stroke="var(--ink-muted)" stroke-width="1" stroke-dasharray="3 3" opacity="0"/>')
    p.append('<circle class="foco" r="5" fill="var(--series-1)" stroke="var(--surface-1)" stroke-width="2" opacity="0"/>')
    p.append("</svg>")
    return "".join(p)


pac = [
    ("Investimento", n("pacing.investimento")),
    ("Impressoes", n("pacing.impressoes")),
    ("Cliques", n("pacing.cliques")),
]
graf_metricas = barras_pacing([(r.replace("Impressoes", "Impressões"), v) for r, v in pac], alt_barra=52)

graf_veiculo = barras_agrupadas(
    list(porv["Veiculo"]),
    list(porv["inv_plan"]),
    list(porv["inv_real"]),
    ("Planejado", "Realizado"),
)

graf_campanha = barras_pacing([(r["Campanha"], r["pacing_inv"]) for _, r in porc.iterrows()], alt_barra=30)

graf_diario = linha_diaria(
    [d.strftime("%Y-%m-%d") for d in diaria["Data"]],
    list(diaria["Soma de Investimento"]),
)

tooltip_dados = [
    {"d": d.strftime("%d/%m/%Y"), "v": brl(v)}
    for d, v in zip(diaria["Data"], diaria["Soma de Investimento"])
]

tabela = [
    {
        "campanha": r["Campanha"],
        "veiculo": r["Veiculo"],
        "inv_plan": brl(r["inv_plan"]),
        "inv_real": brl(r["inv_real"]),
        "pac_inv": pct(r["pacing_inv"], 1),
        "pac_imp": pct(r["pacing_imp"], 1),
        "pac_cli": pct(r["pacing_cli"], 1),
        "ord_inv": r["pacing_inv"],
        "ord_imp": r["pacing_imp"],
        "ord_cli": r["pacing_cli"],
        "ord_plan": r["inv_plan"],
        "ord_real": r["inv_real"],
        "status": faixa_status(r["pacing_inv"]),
    }
    for _, r in valido.iterrows()
]

# ---------------------------------------------------------------- html

INDICADORES = [
    ("Pacing de investimento", pct(n("pacing.investimento")), f"{brl(n('real.investimento'))} de {brl(n('plan.investimento'))} planejados", "good"),
    ("Pacing de impressões", pct(n("pacing.impressoes")), f"{num(n('excedente.impressoes_abs'))} impressões acima do plano", "good"),
    ("Pacing de cliques", pct(n("pacing.cliques")), f"faltaram {num(n('cliques.deficit'))} cliques", "critical"),
    ("Cobertura do plano", pct(n("cobertura.share_realizado_no_plano")), f"{pct(n('cobertura.share_realizado_fora'))} do gasto não tem plano nesta base", "warning"),
]

tiles = "".join(
    f'<div class="tile"><div class="tile-rot">{esc(r)}</div>'
    f'<div class="tile-val st-{s}">{esc(v)}</div>'
    f'<div class="tile-sub">{esc(sub)}</div></div>'
    for r, v, sub, s in INDICADORES
)

HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pacing de campanhas — planejado contra realizado</title>
<style>
:root {{
  color-scheme: light;
  --plane: #f9f9f7; --surface-1: #fcfcfb;
  --ink-1: #0b0b0b; --ink-2: #52514e; --ink-muted: #898781;
  --grid: #e1e0d9; --axis: #c3c2b7; --ring: rgba(11,11,11,0.10);
  --series-1: #2a78d6; --series-2: #eb6834;
  --status-good: #0ca30c; --status-warning: #fab219; --status-critical: #d03b3b;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    color-scheme: dark;
    --plane: #0d0d0d; --surface-1: #1a1a19;
    --ink-1: #ffffff; --ink-2: #c3c2b7; --ink-muted: #898781;
    --grid: #2c2c2a; --axis: #383835; --ring: rgba(255,255,255,0.10);
    --series-1: #3987e5; --series-2: #d95926;
  }}
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; padding: 28px 20px 56px;
  background: var(--plane); color: var(--ink-1);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  font-size: 15px; line-height: 1.55;
}}
.wrap {{ max-width: 1120px; margin: 0 auto; }}
h1 {{ font-size: 26px; line-height: 1.25; margin: 0 0 6px; letter-spacing: -0.01em; }}
.resposta {{ font-size: 17px; color: var(--ink-2); margin: 0 0 26px; max-width: 74ch; }}
h2 {{ font-size: 17px; margin: 0 0 4px; letter-spacing: -0.005em; }}
.sub {{ font-size: 13px; color: var(--ink-muted); margin: 0 0 14px; }}
.card {{
  background: var(--surface-1); border: 1px solid var(--ring);
  border-radius: 12px; padding: 18px 20px; margin-bottom: 18px;
}}
.grade {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 22px; }}
.grade2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
.tile {{ background: var(--surface-1); border: 1px solid var(--ring); border-radius: 12px; padding: 15px 16px; }}
.tile-rot {{ font-size: 12.5px; color: var(--ink-2); text-transform: uppercase; letter-spacing: .04em; }}
.tile-val {{ font-size: 32px; font-weight: 650; margin: 5px 0 3px; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }}
.tile-sub {{ font-size: 12.5px; color: var(--ink-muted); }}
.st-good {{ color: var(--status-good); }}
.st-warning {{ color: var(--ink-1); }}
.st-critical {{ color: var(--status-critical); }}
.legenda {{ display: flex; gap: 18px; font-size: 12.5px; color: var(--ink-2); margin-top: 6px; }}
.legenda i {{ display: inline-block; width: 11px; height: 11px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; }}
.pill {{ display: inline-flex; align-items: center; gap: 5px; font-size: 12px; padding: 1px 8px; border-radius: 999px; border: 1px solid var(--ring); }}
.pill.good {{ color: var(--status-good); }}
.pill.warning {{ color: var(--ink-1); }}
.pill.critical {{ color: var(--status-critical); }}
table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; font-variant-numeric: tabular-nums; }}
th, td {{ text-align: right; padding: 7px 9px; border-bottom: 1px solid var(--grid); white-space: nowrap; }}
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) {{ text-align: left; }}
th {{ cursor: pointer; user-select: none; color: var(--ink-2); font-weight: 600; font-size: 12.5px; }}
th:hover {{ color: var(--ink-1); }}
.filtro {{
  width: 100%; max-width: 340px; padding: 8px 11px; margin-bottom: 12px;
  border: 1px solid var(--ring); border-radius: 8px;
  background: var(--plane); color: var(--ink-1); font-size: 14px; font-family: inherit;
}}
.tabela-scroll {{ overflow-x: auto; }}
.nota {{ font-size: 13.5px; color: var(--ink-2); }}
.nota li {{ margin-bottom: 5px; }}
footer {{ font-size: 12.5px; color: var(--ink-muted); margin-top: 26px; border-top: 1px solid var(--grid); padding-top: 14px; }}
code {{ font-size: 12px; background: var(--surface-1); border: 1px solid var(--ring); border-radius: 4px; padding: 1px 5px; }}
#tip {{
  position: fixed; pointer-events: none; opacity: 0; transition: opacity .1s;
  background: var(--surface-1); border: 1px solid var(--ring); border-radius: 8px;
  padding: 7px 10px; font-size: 12.5px; box-shadow: 0 4px 14px rgba(0,0,0,.14); z-index: 9;
}}
@media (max-width: 700px) {{
  .grade, .grade2 {{ grid-template-columns: 1fr; }}
  h1 {{ font-size: 22px; }}
}}
</style>
</head>
<body>
<div class="wrap">

<h1>Pacing de campanhas: entregamos o que foi planejado?</h1>
<p class="resposta">Entregamos a verba e as impressões, mas não os cliques. O investimento fechou
em {pct(n("pacing.investimento"))} do plano e as impressões em {pct(n("pacing.impressoes"))},
enquanto os cliques pararam em {pct(n("pacing.cliques"))}.</p>

<div class="grade">{tiles}</div>

<div class="card">
  <h2>O plano foi cumprido em verba e em impressão, e não em clique</h2>
  <p class="sub">Pacing por métrica, sobre {num(n("pacing.pares_no_agregado"))} pares de campanha e veículo
  e {num(n("linhas.realizado_dentro"))} linhas de entrega diária. A linha tracejada é o plano.</p>
  {graf_metricas}
</div>

<div class="grade2">
  <div class="card">
    <h2>Tiktok entregou menos da metade da verba planejada</h2>
    <p class="sub">Investimento planejado e realizado por veículo, em milhares de reais. O número
    abaixo de cada veículo é o pacing.</p>
    {graf_veiculo}
  </div>
  <div class="card">
    <h2>A entrega se concentra em junho e julho de 2024</h2>
    <p class="sub">Investimento realizado por dia, dentro das janelas contratadas, em milhares de
    reais. Passe o cursor para ver o dia.</p>
    {graf_diario}
  </div>
</div>

<div class="card">
  <h2>A média esconde os extremos: campanhas de 0% a 134%</h2>
  <p class="sub">Pacing de investimento por campanha. Verde entre {num(n("faixa.limite_inferior"))}% e
  {num(n("faixa.limite_superior"))}%, amarelo acima, vermelho abaixo. O rótulo ao lado da barra traz o valor.</p>
  {graf_campanha}
</div>

<div class="card">
  <h2>Detalhe por campanha e veículo</h2>
  <p class="sub">{num(n("pacing.pares_no_agregado"))} pares com denominador válido. Filtre por texto ou
  clique no cabeçalho para ordenar.</p>
  <input class="filtro" id="filtro" type="text" placeholder="Filtrar por campanha ou veículo" aria-label="Filtrar tabela">
  <div class="tabela-scroll">
  <table id="tb">
    <thead><tr>
      <th data-k="campanha">Campanha</th>
      <th data-k="veiculo">Veículo</th>
      <th data-k="ord_plan">Investimento planejado</th>
      <th data-k="ord_real">Investimento realizado</th>
      <th data-k="ord_inv">Pacing investimento</th>
      <th data-k="ord_imp">Pacing impressões</th>
      <th data-k="ord_cli">Pacing cliques</th>
    </tr></thead>
    <tbody></tbody>
  </table>
  </div>
</div>

<div class="grade2">
  <div class="card nota">
    <h2>Como ler este painel</h2>
    <ul>
      <li>Pacing é o realizado dividido pelo planejado. Acima de 100% entregou mais do que o orçado.</li>
      <li>Uma entrega diária só entra na conta se for da mesma campanha, no mesmo veículo, e em data
      dentro da janela contratada.</li>
      <li>Quando o plano tem janelas sobrepostas, a mesma entrega conta uma vez só. Sem isso, o
      pacing de investimento apareceria como {pct(n("alt.pacing_sem_dedup"))}.</li>
    </ul>
  </div>
  <div class="card nota">
    <h2>O que ele não mostra</h2>
    <ul>
      <li>A operação inteira. O plano cobre {pct(n("cobertura.share_realizado_no_plano"))} do investimento
      realizado no arquivo; o resto é campanha sem plano nesta base.</li>
      <li>O par <code>Joao Pessoa - Não Pulavel / Youtube Ads</code>, que ficou fora porque o plano
      tem investimento em branco e zero impressões, apesar de ter entregue {brl(n("zero.realizado_sem_denominador"))}.</li>
      <li>Pacing de um flight isolado dentro dos grupos com janela sobreposta.</li>
      <li>Resultado de negócio. O arquivo tem entrega de mídia, não tem venda nem receita.</li>
    </ul>
  </div>
</div>

<footer>
Dados de <strong>2024-05-28</strong> a <strong>2024-07-31</strong>, janela do plano. Arquivo de
origem <code>BASE DE PACING_v2.csv.xls</code>, que apesar da extensão é um CSV.
Gerado por <code>analise/scripts/08_dashboard.py</code>, a partir de
<code>analise/numeros.json</code>. O detalhe da tabela vem de
<code>analise/pacing_valido.csv</code>, produzido por <code>analise/scripts/04_pacing.py</code>.
Pipeline completo em <code>analise/scripts/</code>, de <code>01_escopo.py</code> a
<code>07_destaques.py</code>; decisões de método em <code>analise/decisoes.md</code>.
</footer>

</div>
<div id="tip" role="status"></div>
<script>
const LINHAS = {json.dumps(tabela, ensure_ascii=False)};
const SERIE = {json.dumps(tooltip_dados, ensure_ascii=False)};

const corpo = document.querySelector('#tb tbody');
let ordem = {{k: 'ord_inv', asc: true}};

function desenhar() {{
  const q = document.getElementById('filtro').value.toLowerCase().trim();
  const vis = LINHAS.filter(l =>
    !q || l.campanha.toLowerCase().includes(q) || l.veiculo.toLowerCase().includes(q));
  vis.sort((a, b) => {{
    const x = a[ordem.k], y = b[ordem.k];
    const c = typeof x === 'number' ? x - y : String(x).localeCompare(String(y), 'pt-BR');
    return ordem.asc ? c : -c;
  }});
  corpo.innerHTML = vis.map(l => `<tr>
    <td>${{l.campanha}}</td><td>${{l.veiculo}}</td>
    <td>${{l.inv_plan}}</td><td>${{l.inv_real}}</td>
    <td><span class="pill ${{l.status}}">${{l.pac_inv}}</span></td>
    <td>${{l.pac_imp}}</td><td>${{l.pac_cli}}</td></tr>`).join('')
    || '<tr><td colspan="7">Nenhuma linha para esse filtro.</td></tr>';
}}

document.getElementById('filtro').addEventListener('input', desenhar);
document.querySelectorAll('#tb th').forEach(th => th.addEventListener('click', () => {{
  const k = th.dataset.k;
  ordem = {{k, asc: ordem.k === k ? !ordem.asc : true}};
  desenhar();
}}));
desenhar();

// Crosshair e tooltip da serie diaria.
const tip = document.getElementById('tip');
document.querySelectorAll('.svg-hover').forEach(svg => {{
  const [ex, ty, pl, pa] = svg.dataset.plot.split(',').map(Number);
  const cross = svg.querySelector('.crosshair');
  const foco = svg.querySelector('.foco');
  const pts = svg.querySelector('polyline').getAttribute('points').split(' ')
    .map(p => p.split(',').map(Number));

  svg.addEventListener('pointermove', ev => {{
    const cx = svg.getBoundingClientRect();
    const vb = svg.viewBox.baseVal;
    const ux = (ev.clientX - cx.left) / cx.width * vb.width;
    let i = Math.round((ux - ex) / pl * (pts.length - 1));
    i = Math.max(0, Math.min(pts.length - 1, i));
    cross.setAttribute('x1', pts[i][0]); cross.setAttribute('x2', pts[i][0]);
    cross.setAttribute('opacity', '1');
    foco.setAttribute('cx', pts[i][0]); foco.setAttribute('cy', pts[i][1]);
    foco.setAttribute('opacity', '1');
    tip.innerHTML = `<strong>${{SERIE[i].d}}</strong><br>${{SERIE[i].v}}`;
    tip.style.opacity = '1';
    tip.style.left = Math.min(window.innerWidth - 170, ev.clientX + 14) + 'px';
    tip.style.top = (ev.clientY - 46) + 'px';
  }});
  svg.addEventListener('pointerleave', () => {{
    cross.setAttribute('opacity', '0');
    foco.setAttribute('opacity', '0');
    tip.style.opacity = '0';
  }});
}});
</script>
</body>
</html>
"""

SAIDA.parent.mkdir(parents=True, exist_ok=True)
SAIDA.write_text(HTML, encoding="utf-8")
print(f"dashboard: {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} kB)")
