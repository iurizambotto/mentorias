"""Passo 9. Gera entregas/dashboard.html, um arquivo unico e offline.

Os valores vem de analise/numeros.json e dos CSV dos passos anteriores. Este
script nao recalcula pacing: ele so formata o que o livro ja registrou.

Graficos em SVG escrito aqui, com as cores em variaveis CSS, para que o tema
escuro nao seja uma inversao automatica de uma imagem de cor fixa.
"""

from __future__ import annotations

import html
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

LIVRO = Path("analise/numeros.json")
SAIDA = Path("entregas/dashboard.html")
FONTE = "BASE DE PACING_v2.csv.xls"


def livro() -> dict[str, dict]:
    return json.loads(LIVRO.read_text(encoding="utf-8"))


def num(chave: str) -> float:
    return livro()[chave]["valor"]


def br(valor: float, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def reais(valor: float) -> str:
    return f"R$ {br(valor)}"


@dataclass(frozen=True)
class Barra:
    rotulo: str
    valor: float
    texto: str
    detalhe: str
    destaque: bool = False


def barras_pacing(barras: list[Barra], ref: float = 100.0, altura_barra: int = 44) -> str:
    """Barras horizontais de pacing, com linha de referencia no plano.

    Uma serie so, entao sem legenda: o titulo do bloco nomeia a medida. Cada
    barra e rotulada direto, que e o que dispensa ler a cor.
    """
    largura, margem_esq, margem_dir = 760, 168, 74
    topo, gap = 16, 14
    escala_max = max([b.valor for b in barras] + [ref]) * 1.12
    area = largura - margem_esq - margem_dir
    altura = topo + len(barras) * (altura_barra + gap)
    x_ref = margem_esq + area * (ref / escala_max)

    partes = [
        f'<svg viewBox="0 0 {largura} {altura}" role="img" class="gr" '
        f'preserveAspectRatio="xMinYMin meet">'
    ]
    partes.append(
        f'<line x1="{x_ref:.1f}" y1="4" x2="{x_ref:.1f}" y2="{altura - 8}" class="ref"/>'
        f'<text x="{x_ref:.1f}" y="{altura - 0}" class="rotulo-ref" text-anchor="middle">'
        f"plano = {br(ref, 0)}%</text>"
    )
    for i, b in enumerate(barras):
        y = topo + i * (altura_barra + gap)
        w = max(area * (b.valor / escala_max), 1.5)
        # Uma cor de destaque so, no dado que o titulo do bloco aponta. Cor por
        # faixa de valor seria semantica errada aqui: entregar mais impressoes
        # que o plano e resultado bom, e pintar de alerta diria o contrario.
        classe = "barra-destaque" if b.destaque else "barra"
        partes.append(
            f'<g class="mark"><title>{html.escape(b.rotulo)}: {html.escape(b.texto)}. '
            f"{html.escape(b.detalhe)}</title>"
            f'<text x="{margem_esq - 12}" y="{y + altura_barra / 2 + 5}" '
            f'class="rotulo-cat" text-anchor="end">{html.escape(b.rotulo)}</text>'
            f'<rect x="{margem_esq}" y="{y}" width="{w:.1f}" height="{altura_barra}" '
            f'rx="4" class="{classe}"/>'
            f'<text x="{margem_esq + w + 10:.1f}" y="{y + altura_barra / 2 + 5}" '
            f'class="valor">{html.escape(b.texto)}</text></g>'
        )
    partes.append("</svg>")
    return "".join(partes)


def barras_duplas(linhas: list[tuple[str, float, float, str]]) -> str:
    """Planejado contra realizado, duas series, barras agrupadas.

    Duas series exigem legenda; as duas tambem sao rotuladas direto, entao a
    identidade nunca depende so da cor.
    """
    largura, margem_esq, margem_dir = 760, 168, 96
    alt, gap_serie, gap_grupo = 19, 3, 20
    topo = 10
    maximo = max(max(p, r) for _, p, r, _ in linhas) * 1.14
    area = largura - margem_esq - margem_dir
    altura = topo + len(linhas) * (alt * 2 + gap_serie + gap_grupo)

    partes = [
        f'<svg viewBox="0 0 {largura} {altura}" role="img" class="gr" '
        f'preserveAspectRatio="xMinYMin meet">'
    ]
    for i, (nome, plano, real, detalhe) in enumerate(linhas):
        y = topo + i * (alt * 2 + gap_serie + gap_grupo)
        wp = max(area * (plano / maximo), 1.5)
        wr = max(area * (real / maximo), 1.5)
        partes.append(
            f'<text x="{margem_esq - 12}" y="{y + alt + 4}" class="rotulo-cat" '
            f'text-anchor="end">{html.escape(nome)}</text>'
            f'<g class="mark"><title>{html.escape(nome)} planejado: {reais(plano)}</title>'
            f'<rect x="{margem_esq}" y="{y}" width="{wp:.1f}" height="{alt}" rx="4" '
            f'class="serie-plano"/>'
            f'<text x="{margem_esq + wp + 8:.1f}" y="{y + alt - 4}" class="valor-min">'
            f"{html.escape(br(plano, 0))}</text></g>"
            f'<g class="mark"><title>{html.escape(nome)} realizado: {reais(real)}. '
            f"{html.escape(detalhe)}</title>"
            f'<rect x="{margem_esq}" y="{y + alt + gap_serie}" width="{wr:.1f}" height="{alt}" '
            f'rx="4" class="serie-real"/>'
            f'<text x="{margem_esq + wr + 8:.1f}" y="{y + alt * 2 + gap_serie - 4}" '
            f'class="valor-min">{html.escape(br(real, 0))}</text></g>'
        )
    partes.append("</svg>")
    return "".join(partes)


def tabela(pares: pd.DataFrame) -> str:
    """Detalhe no grao em que o pacing e valido: campanha x veiculo.

    Nao no grao de flight. Onde o plano se sobrepoe, o realizado do flight
    isolado carrega a entrega inteira do par contra um orcamento parcial, e
    produz pacing de milhares por cento, que e artefato da sobreposicao e nao
    resultado. O detalhe por flight vai no pacote do Power BI, com a coluna
    que marca a disputa.
    """
    cabecalho = [
        "Campanha", "Veículo", "Flights", "Início", "Término", "Planejado R$",
        "Realizado R$", "Pacing R$", "Pacing impressões", "Dias entregues",
    ]
    linhas = []
    for _, f in pares.iterrows():
        def pct(valor: float) -> str:
            return "sem denominador" if pd.isna(valor) else f"{br(valor * 100, 1)}%"

        linhas.append(
            "<tr>"
            + "".join(
                f"<td>{html.escape(str(c))}</td>"
                for c in (
                    f["Campanha"],
                    f["Veiculo"],
                    int(f["flights"]),
                    str(f["inicio"])[:10],
                    str(f["termino"])[:10],
                    br(f["plan_investimento"]) if f["investimento_nulo"] == 0 else "não orçado",
                    br(f["real_investimento"]),
                    pct(f["pacing_investimento"]),
                    pct(f["pacing_impressoes"]),
                    int(f["dias_entregues"]),
                )
            )
            + "</tr>"
        )
    return (
        "<table id='tabela'><thead><tr>"
        + "".join(
            f"<th tabindex='0' role='button' data-col='{i}'>{html.escape(c)}</th>"
            for i, c in enumerate(cabecalho)
        )
        + "</tr></thead><tbody>"
        + "".join(linhas)
        + "</tbody></table>"
    )


CSS = """
:root{color-scheme:light dark}
.viz-root{
  --plano:#f9f9f7; --superficie:#fcfcfb; --borda:#e4e3df;
  --ink:#0b0b0b; --ink2:#52514e; --ink3:#77766f;
  --serie-real:#2a78d6; --serie-plano:#eb6834;
  --critico:#d03b3b; --grade:#d9d8d3;
}
@media (prefers-color-scheme:dark){
  .viz-root{
    --plano:#0d0d0d; --superficie:#1a1a19; --borda:#33332f;
    --ink:#ffffff; --ink2:#c3c2b7; --ink3:#9b9a90;
    --serie-real:#3987e5; --serie-plano:#d95926;
    --critico:#d03b3b; --grade:#3a3a36;
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--plano);color:var(--ink);
  font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:28px 20px 64px}
h1{font-size:30px;line-height:1.22;margin:0 0 6px;letter-spacing:-.01em}
h2{font-size:20px;margin:40px 0 6px;letter-spacing:-.005em}
.sub{color:var(--ink2);margin:0 0 4px;font-size:17px}
.fonte{color:var(--ink3);font-size:13px;margin:6px 0 0}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0 8px}
.kpi{background:var(--superficie);border:1px solid var(--borda);border-radius:10px;padding:16px}
.kpi .rot{font-size:13px;color:var(--ink2);text-transform:uppercase;letter-spacing:.06em}
.kpi .val{font-size:29px;font-weight:650;margin:8px 0 2px;letter-spacing:-.02em}
.kpi .cmp{font-size:14px;color:var(--ink2)}
.kpi .base{font-size:12px;color:var(--ink3);margin-top:8px}
.card{background:var(--superficie);border:1px solid var(--borda);border-radius:10px;
  padding:18px 18px 12px;margin-top:12px;overflow-x:auto}
.gr{width:100%;height:auto;display:block}
.barra{fill:var(--serie-real)} .barra-destaque{fill:var(--critico)}
.serie-real{fill:var(--serie-real)} .serie-plano{fill:var(--serie-plano)}
.mark:hover rect{stroke:var(--superficie);stroke-width:2px}
.ref{stroke:var(--ink3);stroke-width:2;stroke-dasharray:5 4}
.rotulo-cat{fill:var(--ink2);font-size:14px}
.rotulo-ref{fill:var(--ink3);font-size:12px}
.valor{fill:var(--ink);font-size:15px;font-weight:600}
.valor-min{fill:var(--ink2);font-size:12px}
.leg{display:flex;gap:18px;align-items:center;margin:2px 0 12px;font-size:14px;color:var(--ink2)}
.sw{width:12px;height:12px;border-radius:3px;display:inline-block;margin-right:6px;
  vertical-align:-1px}
.imp{font-size:15px;color:var(--ink2);margin:10px 0 0}
input[type=search]{width:100%;padding:11px 13px;font-size:15px;border-radius:8px;
  border:1px solid var(--borda);background:var(--superficie);color:var(--ink);margin:12px 0 0}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin-top:10px}
th,td{padding:8px 9px;border-bottom:1px solid var(--borda);text-align:left;white-space:nowrap}
th{cursor:pointer;color:var(--ink2);font-size:12px;text-transform:uppercase;
  letter-spacing:.05em;position:sticky;top:0;background:var(--superficie)}
th:hover,th:focus{color:var(--ink)}
td:nth-child(n+5):nth-child(-n+8){text-align:right;font-variant-numeric:tabular-nums}
.nota{background:var(--superficie);border:1px solid var(--borda);border-left:3px solid var(--ink3);
  border-radius:8px;padding:14px 16px;margin-top:12px;font-size:15px;color:var(--ink2)}
.nota strong{color:var(--ink)}
footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--borda);
  color:var(--ink3);font-size:13px}
code{font-size:12.5px}
@media (max-width:700px){
  .kpis{grid-template-columns:1fr}
  h1{font-size:24px}
  .wrap{padding:18px 14px 48px}
}
"""

JS = """
(function(){
  var busca=document.getElementById('busca'), tab=document.getElementById('tabela');
  var corpo=tab.tBodies[0], linhas=Array.prototype.slice.call(corpo.rows), ordem={};
  busca.addEventListener('input',function(){
    var q=busca.value.toLowerCase();
    linhas.forEach(function(l){
      l.style.display = l.textContent.toLowerCase().indexOf(q)>-1 ? '' : 'none';
    });
  });
  function limpar(t){
    var n=parseFloat(t.replace(/[^0-9,.-]/g,'').replace(/\\./g,'').replace(',','.'));
    return isNaN(n)?null:n;
  }
  function ordenar(i){
    var asc = ordem[i] = !ordem[i];
    linhas.sort(function(a,b){
      var x=a.cells[i].textContent.trim(), y=b.cells[i].textContent.trim();
      var nx=limpar(x), ny=limpar(y);
      if(nx!==null&&ny!==null) return asc?nx-ny:ny-nx;
      return asc?x.localeCompare(y,'pt-BR'):y.localeCompare(x,'pt-BR');
    });
    linhas.forEach(function(l){corpo.appendChild(l)});
  }
  Array.prototype.forEach.call(tab.tHead.rows[0].cells,function(th){
    th.addEventListener('click',function(){ordenar(+th.dataset.col)});
    th.addEventListener('keydown',function(e){
      if(e.key==='Enter'||e.key===' '){e.preventDefault();ordenar(+th.dataset.col);}
    });
  });
})();
"""


def construir() -> str:
    L = livro()
    campanha = pd.read_csv("analise/pacing_campanha.csv")
    veiculo = pd.read_csv("analise/pacing_veiculo.csv")
    pares = pd.read_csv("analise/pacing_campanha_veiculo.csv").sort_values(
        "plan_investimento", ascending=False
    )

    kpis = [
        (
            "Pacing de investimento",
            f"{br(num('total.pacing_investimento'), 2)}%",
            f"{reais(num('total.real_investimento'))} entregues contra "
            f"{reais(num('total.plan_investimento'))} planejados",
            f"{int(num('linhas.realizado_no_plano'))} dias de entrega dentro do plano",
        ),
        (
            "Pacing de impressões",
            f"{br(num('total.pacing_impressoes'), 2)}%",
            f"{br(num('total.gap_impressoes'), 0)} impressões acima do plano",
            f"{int(num('linhas.realizado_no_plano'))} dias de entrega dentro do plano",
        ),
        (
            "Pacing de cliques",
            f"{br(num('total.pacing_cliques'), 2)}%",
            f"{br(num('cliques.pacing_sem_maior_flight'), 2)}% sem o flight de CTR atípico",
            f"{int(num('linhas.realizado_no_plano'))} dias de entrega dentro do plano",
        ),
        (
            "Plano sem entrega",
            reais(num("flight.investimento_sem_entrega")),
            f"{int(num('flight.sem_entrega_na_janela'))} flight do plano sem nenhum dia entregue",
            f"{int(num('linhas.planejado'))} flights planejados",
        ),
    ]
    blocos_kpi = "".join(
        f'<div class="kpi"><div class="rot">{html.escape(r)}</div>'
        f'<div class="val">{html.escape(v)}</div>'
        f'<div class="cmp">{html.escape(c)}</div>'
        f'<div class="base">{html.escape(b)}</div></div>'
        for r, v, c, b in kpis
    )

    g_metrica = barras_pacing(
        [
            Barra("Investimento", num("total.pacing_investimento"),
                  f"{br(num('total.pacing_investimento'), 2)}%",
                  f"{reais(num('total.real_investimento'))} de {reais(num('total.plan_investimento'))}"),
            Barra("Impressões", num("total.pacing_impressoes"),
                  f"{br(num('total.pacing_impressoes'), 2)}%",
                  f"{br(num('total.real_impressoes'), 0)} de {br(num('total.plan_impressoes'), 0)}"),
            Barra("Cliques", num("total.pacing_cliques"),
                  f"{br(num('total.pacing_cliques'), 2)}%",
                  "denominador derivado de premissa de CTR, não é meta contratada"),
        ]
    )

    g_veiculo = barras_pacing(
        [
            Barra(
                linha["Veiculo"],
                linha["pacing_investimento"] * 100,
                f"{br(linha['pacing_investimento'] * 100, 2)}%",
                f"{reais(linha['real_investimento'])} de {reais(linha['plan_investimento'])}, "
                f"{int(linha['dias_entregues'])} dias",
                destaque=linha["Veiculo"] == "Tiktok Ads",
            )
            for _, linha in veiculo.sort_values("pacing_investimento").iterrows()
        ]
    )

    top = campanha.nlargest(10, "plan_investimento")
    g_campanha = barras_duplas(
        [
            (
                linha["Campanha"],
                float(linha["plan_investimento"]),
                float(linha["real_investimento"]),
                "sem pacing: nada orçado"
                if pd.isna(linha["pacing_investimento"])
                else f"pacing {br(linha['pacing_investimento'] * 100, 1)}%",
            )
            for _, linha in top.iterrows()
        ]
    )

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pacing de campanhas — planejado contra realizado</title>
<style>{CSS}</style>
</head>
<body class="viz-root">
<div class="wrap">

<h1>O dinheiro planejado foi entregue quase na régua, e rendeu mais mídia do que o plano previa</h1>
<p class="sub">A pergunta: entregamos o que tinha sido planejado? Em dinheiro sim, com pacing de
{br(num('total.pacing_investimento'), 2)}%. A mesma verba comprou
{br(num('total.excedente_impressoes_pct'), 2)}% mais impressões do que o plano previa. O único
desvio material é o Tiktok Ads.</p>
<p class="fonte">Base: {html.escape(FONTE)}. Plano de {int(num('linhas.planejado'))} flights,
{int(num('linhas.realizado'))} dias de entrega registrados, dos quais
{int(num('linhas.realizado_no_plano'))} caem dentro de alguma janela contratada.</p>

<div class="kpis">{blocos_kpi}</div>

<h2>Em dinheiro o plano fechou no ponto, e a entrega de mídia superou o previsto</h2>
<div class="card">{g_metrica}</div>
<p class="imp">O pacing de cliques de {br(num('total.pacing_cliques'), 2)}% não é déficit de
entrega. O plano deriva cliques de uma premissa de CTR por flight que vai de
{br(num('ctr.plano_minimo'), 2)}% a {br(num('ctr.plano_maximo'), 2)}%. Um único flight concentra
{br(num('cliques.concentracao_maior_flight_pct'), 2)}% dos cliques planejados; sem ele o pacing é
{br(num('cliques.pacing_sem_maior_flight'), 2)}%.</p>

<h2>O Tiktok Ads entregou menos da metade do que foi planejado</h2>
<div class="card">{g_veiculo}</div>
<p class="imp">Tiktok Ads ficou em {br(num('veiculo.tiktok.pacing_investimento'), 2)}% do
investimento e {br(num('veiculo.tiktok.pacing_impressoes'), 2)}% das impressões. Metade da
diferença vem de um flight só, a campanha Inauguracao, com
{reais(num('camp.inauguracao.plan_investimento'))} planejados e nenhum dia de entrega. Meta Ads
ficou em {br(num('veiculo.meta.pacing_investimento'), 2)}% e Youtube Ads em
{br(num('veiculo.youtube.pacing_investimento'), 2)}%.</p>

<h2>Campanha a campanha, o desvio de verba é pequeno fora das inaugurações</h2>
<div class="card">
<div class="leg"><span><span class="sw" style="background:var(--serie-plano)"></span>Planejado</span>
<span><span class="sw" style="background:var(--serie-real)"></span>Realizado na janela</span>
<span>valores em R$</span></div>
{g_campanha}
</div>
<p class="imp">Das {int(num('campanha.com_pacing_investimento'))} campanhas com pacing calculável,
{int(num('campanha.dentro_80_120'))} ficaram entre {br(num('faixa.limite_inferior_pct'), 0)}% e
{br(num('faixa.limite_superior_pct'), 0)}% do orçado, {int(num('campanha.abaixo_80'))} abaixo e
{int(num('campanha.acima_120'))} acima. O resultado agregado não está escondendo extremos que se
anulam.</p>

<h2>Detalhe por campanha e veículo</h2>
<p class="imp">Este é o nível em que o pacing é válido. Filtre por campanha, veículo ou data.
Clique no cabeçalho para ordenar.</p>
<input type="search" id="busca" placeholder="Filtrar por campanha, veículo ou data"
 aria-label="Filtrar a tabela de campanhas">
<div class="card">{tabela(pares)}</div>

<div class="nota">
<p><strong>Como ler este painel.</strong> Pacing é o que foi entregue dividido pelo que foi
planejado. Só conta a entrega da mesma campanha, no mesmo veículo, com data dentro da janela
daquele flight. Onde o plano tem flights sobrepostos, a mesma entrega é reivindicada por mais de
um flight; ela é contada <strong>uma vez só</strong>. São
{int(num('sobreposicao.entregas_em_mais_de_um_flight'))} dias de entrega nessa situação, um deles
disputado por {int(num('sobreposicao.max_flights_por_entrega'))} flights. Sem essa correção o
painel mostraria {br(num('alt.sem_dedup_pacing_impressoes'), 2)}% de impressões em vez de
{br(num('total.pacing_impressoes'), 2)}%. Por isso a tabela abre por campanha e veículo, e não
por flight: onde as janelas se cruzam, a entrega de um dia não pertence a um flight específico,
e um pacing por flight ali seria artefato da sobreposição, não resultado. A coluna Flights mostra
quantos flights foram somados em cada linha.</p>
<p><strong>O que ele não mostra.</strong> Campanha sem linha de planejado fica fora do pacing:
são {int(num('fora.campanhas_sem_plano_distintas'))} campanhas e
{reais(num('fora.campanha_sem_plano_investimento'))}. No total,
{br(num('total.share_fora_do_plano_pct'), 2)}% do investimento realizado no arquivo não pertence
a este plano. Um par campanha e veículo não tem pacing porque nada foi orçado contra ele, e
aparece na tabela como sem denominador; ele nunca é mostrado como 0%. O painel também não mostra
pacing por flight isolado onde as janelas se cruzam, porque o dado diário não diz a qual flight
pertence.</p>
</div>

<footer>
Dados de {html.escape(FONTE)}, entregas de 2023-01-03 a 2024-08-09, plano de 2024-05-28 a
2024-07-31. Gerado por <code>analise/scripts/08_dashboard.py</code> a partir de
<code>analise/numeros.json</code>, que por sua vez vem de <code>01_escopo.py</code>,
<code>02_sobreposicao.py</code>, <code>03_pacing.py</code>, <code>04_alternativas.py</code>,
<code>05_cortes.py</code>, <code>06_cliques.py</code> e <code>07_citados.py</code>.
Nenhum recurso é carregado da rede: o arquivo abre offline e por anexo de email.
</footer>
</div>
<script>{JS}</script>
</body>
</html>
"""


if __name__ == "__main__":
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(construir(), encoding="utf-8")
    print(f"dashboard: {SAIDA} ({SAIDA.stat().st_size / 1024:.0f} kB)")
