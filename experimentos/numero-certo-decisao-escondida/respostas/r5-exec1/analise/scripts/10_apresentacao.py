"""Passo 10: gera entregas/apresentacao.pptx, 16:9, um slide por mensagem.

Os graficos sao PNG de matplotlib a 200 dpi, sem titulo dentro da imagem: o
titulo do slide ja carrega a mensagem. Uma cor de destaque so, no dado que o
titulo aponta; o resto em cinza.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from comum import ARQUIVO  # noqa: F401
from numeros import carregar as carregar_livro
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

RAIZ = Path(__file__).resolve().parents[1]
ENTREGAS = RAIZ.parent / "entregas"
FIGS = RAIZ / "figuras"
FIGS.mkdir(parents=True, exist_ok=True)

livro = carregar_livro()
valido = pd.read_csv(RAIZ / "pacing_valido.csv")
porc = pd.read_csv(RAIZ / "pacing_por_campanha.csv")
porv = pd.read_csv(RAIZ / "pacing_por_veiculo.csv")

DESTAQUE = "#2a78d6"
ALERTA = "#d03b3b"
NEUTRO = "#b8b7b1"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"

L, A = Inches(13.333), Inches(7.5)


def n(chave: str) -> float:
    return livro[chave]["valor"]


def _br(v: float, casas: int) -> str:
    return f"{v:,.{casas}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def brl(v: float, casas: int = 2) -> str:
    return "R$ " + _br(v, casas)


def pct(v: float, casas: int = 2) -> str:
    return _br(v, casas) + "%"


def mil(v: float) -> str:
    return _br(v, 0)


plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 13,
        "axes.edgecolor": "#c3c2b7",
        "axes.labelcolor": TINTA2,
        "xtick.color": TINTA2,
        "ytick.color": TINTA2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.facecolor": "white",
    }
)


def salvar(fig, nome: str) -> str:
    caminho = FIGS / f"{nome}.png"
    fig.savefig(caminho, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(caminho)


# ------------------------------------------------------------------ figuras

def fig_metricas() -> str:
    dados = [("Investimento", n("pacing.investimento")), ("Impressões", n("pacing.impressoes")), ("Cliques", n("pacing.cliques"))]
    fig, ax = plt.subplots(figsize=(9.2, 3.6))
    rotulos = [d[0] for d in dados][::-1]
    vals = [d[1] for d in dados][::-1]
    cores = [ALERTA if v < n("faixa.limite_inferior") else NEUTRO for v in vals]
    barras = ax.barh(rotulos, vals, color=cores, height=0.56)
    for b, v in zip(barras, vals):
        ax.text(v + 3, b.get_y() + b.get_height() / 2, pct(v, 1), va="center", fontsize=14, color=TINTA, fontweight="bold")
    ax.axvline(100, color=TINTA, lw=2, ls="--")
    ax.text(100, len(vals) - 0.32, " plano", color=TINTA2, fontsize=12)
    ax.set_xlim(0, 150)
    ax.set_xlabel("pacing, realizado sobre planejado (%)")
    ax.set_yticklabels(rotulos, fontsize=14, color=TINTA)
    return salvar(fig, "metricas")


def fig_veiculo() -> str:
    fig, ax = plt.subplots(figsize=(9.2, 3.9))
    x = range(len(porv))
    lb = 0.38
    ax.bar([i - lb / 2 - 0.01 for i in x], porv["inv_plan"] / 1000, lb, label="Planejado", color=NEUTRO)
    cores = [ALERTA if p < n("faixa.limite_inferior") else DESTAQUE for p in porv["pacing_inv"]]
    ax.bar([i + lb / 2 + 0.01 for i in x], porv["inv_real"] / 1000, lb, label="Realizado", color=cores)
    for i, (_, r) in enumerate(porv.iterrows()):
        ax.text(i, max(r["inv_plan"], r["inv_real"]) / 1000 + 28, pct(r["pacing_inv"], 1), ha="center", fontsize=13,
                color=ALERTA if r["pacing_inv"] < n("faixa.limite_inferior") else TINTA, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(porv["Veiculo"], fontsize=13, color=TINTA)
    ax.set_ylabel("investimento (R$ mil)")
    ax.set_ylim(0, 1000)
    ax.legend(frameon=False, fontsize=12, loc="upper right")
    return salvar(fig, "veiculo")


def fig_campanha() -> str:
    d = porc.sort_values("pacing_inv")
    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    cores = [
        ALERTA if v < n("faixa.limite_inferior") else (DESTAQUE if v > n("faixa.limite_superior") else NEUTRO)
        for v in d["pacing_inv"]
    ]
    ax.barh(d["Campanha"], d["pacing_inv"], color=cores, height=0.7)
    ax.axvline(100, color=TINTA, lw=1.6, ls="--")
    for i, v in enumerate(d["pacing_inv"]):
        ax.text(v + 2.5, i, pct(v, 0), va="center", fontsize=12.5, color=TINTA2)
    ax.set_xlim(0, 152)
    ax.set_xlabel("pacing de investimento (%)", fontsize=14)
    ax.tick_params(axis="y", labelsize=14)
    ax.tick_params(axis="x", labelsize=13)
    return salvar(fig, "campanha")


def fig_funil() -> str:
    """Por que a verba entregue nao virou clique: CPM caiu, CPC subiu."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 3.7))
    for ax, (rot, pl, rl, unid) in zip(
        (a1, a2),
        [("CPM", n("cpm.planejado"), n("cpm.realizado"), "R$ por mil impressões"),
         ("CPC", n("cpc.planejado"), n("cpc.realizado"), "R$ por clique")],
    ):
        cor = NEUTRO if rot == "CPM" else ALERTA
        b = ax.bar(["Planejado", "Realizado"], [pl, rl], color=[NEUTRO, cor], width=0.52)
        for bb, v in zip(b, [pl, rl]):
            ax.text(bb.get_x() + bb.get_width() / 2, v + max(pl, rl) * 0.04, brl(v), ha="center", fontsize=13, color=TINTA, fontweight="bold")
        ax.set_title(f"{rot} — {unid}", fontsize=13, color=TINTA2, pad=12)
        ax.set_ylim(0, max(pl, rl) * 1.28)
        ax.tick_params(axis="x", labelsize=13)
    fig.tight_layout()
    return salvar(fig, "funil")


def fig_cobertura() -> str:
    dentro = n("real.investimento")
    fora = n("valor.realizado_fora")
    fig, ax = plt.subplots(figsize=(9.2, 2.3))
    ax.barh([""], [dentro / 1e6], color=DESTAQUE, height=0.5, label="Dentro do plano")
    ax.barh([""], [fora / 1e6], left=[dentro / 1e6 + 0.04], color=NEUTRO, height=0.5, label="Sem plano nesta base")
    # A fatia dentro do plano e estreita demais para caber o rotulo dentro dela.
    ax.annotate(
        pct(n("cobertura.share_realizado_no_plano"), 1),
        xy=(dentro / 1e6, 0.16), xytext=(dentro / 1e6 + 1.1, 0.46),
        color=DESTAQUE, fontsize=13, fontweight="bold", va="center",
        arrowprops=dict(arrowstyle="-", color=DESTAQUE, lw=1.2),
    )
    ax.text(dentro / 1e6 + fora / 1e6 / 2, 0, pct(n("cobertura.share_realizado_fora"), 1), ha="center", va="center", color=TINTA, fontsize=13, fontweight="bold")
    ax.set_ylim(-0.45, 0.62)
    ax.set_xlabel("investimento realizado (R$ milhões)")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, fontsize=12, ncol=2, loc="lower center", bbox_to_anchor=(0.5, -0.92))
    return salvar(fig, "cobertura")


def fig_dedup() -> str:
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    vals = [n("alt.pacing_sem_veiculo"), n("alt.pacing_sem_dedup"), n("alt.pacing_sem_janela")]
    rot = ["Ignorando\no veículo", "Sem deduplicar\na entrega", "Ignorando\na janela"]
    ax.bar(["Conta\nentregue"] + rot, [n("pacing.investimento")] + vals, color=[DESTAQUE] + [NEUTRO] * 3, width=0.55)
    for i, v in enumerate([n("pacing.investimento")] + vals):
        ax.text(i, v + 9, pct(v, 1), ha="center", fontsize=13, color=TINTA, fontweight="bold")
    ax.axhline(100, color=TINTA2, lw=1.2, ls="--")
    ax.set_ylabel("pacing de investimento (%)")
    ax.set_ylim(0, 420)
    ax.tick_params(axis="x", labelsize=12)
    return salvar(fig, "dedup")


figuras = {
    "metricas": fig_metricas(),
    "veiculo": fig_veiculo(),
    "campanha": fig_campanha(),
    "funil": fig_funil(),
    "cobertura": fig_cobertura(),
    "dedup": fig_dedup(),
}

# ------------------------------------------------------------------ deck

prs = Presentation()
prs.slide_width, prs.slide_height = L, A
VAZIO = prs.slide_layouts[6]
SO_TITULO = prs.slide_layouts[5]  # tem placeholder de titulo, que o validador exige


def slide(com_titulo: bool = True):
    s = prs.slides.add_slide(SO_TITULO if com_titulo else VAZIO)
    # O layout "So titulo" traz um rodape de data e numero que nao usamos.
    for forma in list(s.shapes):
        if forma.is_placeholder and forma != s.shapes.title:
            forma._element.getparent().remove(forma._element)
    return s


def caixa(s, x, y, w, h, texto, tam, *, negrito=False, cor=TINTA, espaco=6, alinha=None):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, linha in enumerate(texto if isinstance(texto, list) else [texto]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(espaco)
        if alinha is not None:
            p.alignment = alinha
        r = p.add_run()
        r.text = linha
        r.font.size = Pt(tam)
        r.font.bold = negrito
        r.font.color.rgb = RGBColor.from_string(cor.lstrip("#").upper())
        r.font.name = "Calibri"
    return tb


def titulo(s, texto, sub=None):
    ph = s.shapes.title
    ph.left, ph.top, ph.width, ph.height = Inches(0.62), Inches(0.42), Inches(12.1), Inches(1.15)
    ph.text_frame.word_wrap = True
    p = ph.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    r.text = texto
    r.font.size = Pt(30)
    r.font.bold = True
    r.font.color.rgb = RGBColor.from_string(TINTA.lstrip("#").upper())
    r.font.name = "Calibri"
    if sub:
        caixa(s, 0.62, 1.62, 12.1, 0.6, sub, 16, cor=TINTA2)


def figura(s, chave, topo, largura_max, reserva=0.0):
    """Encaixa a figura entre o subtitulo e o espaco reservado ao rodape do slide.

    Escala pela dimensao que estourar primeiro e centraliza na horizontal, para
    que nenhuma imagem invada a caixa de texto de baixo.
    """
    pic = s.shapes.add_picture(figuras[chave], Inches(0), Inches(topo), width=Inches(largura_max))
    disponivel = A - Inches(topo) - Inches(reserva)
    if pic.height > disponivel:
        fator = disponivel / pic.height
        pic.height = int(pic.height * fator)
        pic.width = int(pic.width * fator)
    pic.left = int((L - pic.width) / 2)
    return pic


def notas(s, texto):
    s.notes_slide.notes_text_frame.text = texto


# 1. Capa
s = slide(com_titulo=False)
caixa(s, 0.9, 2.35, 11.6, 1.9, "Entregamos a verba e as impressões, mas menos da metade dos cliques", 40, negrito=True)
caixa(s, 0.9, 4.25, 11.6, 0.9, "Pacing de campanhas · plano de 28/05/2024 a 31/07/2024", 19, cor=TINTA2)
caixa(s, 0.9, 5.05, 11.6, 0.6, "Reunião de resultados", 16, cor=TINTA2)
notas(s, "O deck responde uma pergunta: entregamos o que foi planejado? A resposta curta e sim para "
         "verba e impressao, nao para clique.")

# 2. A pergunta
s = slide()
titulo(s, "A pergunta")
caixa(s, 0.9, 2.5, 11.4, 2.2, "“A gente entregou o que tinha planejado?”", 34, negrito=True, cor=DESTAQUE)
caixa(s, 0.9, 4.3, 11.4, 2.0, [
    "Pacing é o realizado dividido pelo planejado.",
    "Só conta a entrega da mesma campanha, no mesmo veículo, dentro da janela contratada.",
], 18, cor=TINTA2, espaco=10)
notas(s, "Campanha sem linha de planejado fica fora da conta. Entrega fora da janela do flight nao "
         "pertence aquele plano.")

# 3. A resposta
s = slide()
titulo(s, "A verba foi entregue. O clique, não.")
for i, (rot, val, sub, cor) in enumerate([
    ("Pacing de investimento", pct(n("pacing.investimento")), f"{brl(n('real.investimento'))}\nde {brl(n('plan.investimento'))}", TINTA),
    ("Pacing de impressões", pct(n("pacing.impressoes")), f"{mil(n('excedente.impressoes_abs'))}\nacima do plano", TINTA),
    ("Pacing de cliques", pct(n("pacing.cliques")), f"faltaram\n{mil(n('cliques.deficit'))} cliques", ALERTA),
]):
    x = 0.75 + i * 4.15
    caixa(s, x, 2.6, 3.8, 0.5, rot, 15, cor=TINTA2)
    caixa(s, x, 3.05, 3.8, 1.3, val, 50, negrito=True, cor=cor)
    caixa(s, x, 4.5, 3.8, 1.4, sub.split("\n"), 15, cor=TINTA2, espaco=2)
caixa(s, 0.75, 6.1, 11.9, 0.8,
      f"Base: {mil(n('linhas.planejado'))} linhas de plano e {mil(n('linhas.realizado_dentro'))} linhas de entrega diária dentro das janelas.",
      15, cor=TINTA2)
notas(s, "A mediana de pacing de investimento por par e 99,9999%, ou seja, o acerto na verba nao e "
         "efeito de media: e caso a caso.")

# 4. Insight: metricas
s = slide()
titulo(s, "O plano foi cumprido em verba e em impressão, e furou em clique",
       f"Pacing por métrica, sobre {mil(n('pacing.pares_no_agregado'))} pares de campanha e veículo")
figura(s, "metricas", 2.45, 10.2, reserva=0.5)
notas(s, f"Investimento {pct(n('pacing.investimento'))}, impressoes {pct(n('pacing.impressoes'))}, "
         f"cliques {pct(n('pacing.cliques'))}. Olhar so o investimento daria esta campanha como entregue.")

# 5. Insight: CPM x CPC
s = slide()
titulo(s, "Compramos mídia mais barata que não converteu em clique",
       f"CTR caiu de {pct(n('ctr.planejado'), 4)} previstos para {pct(n('ctr.realizado'), 4)} realizados")
figura(s, "funil", 2.45, 9.6, reserva=1.15)
caixa(s, 0.8, 6.45, 11.8, 0.7,
      f"O clique saiu {_br(n('cpc.razao'), 2)} vezes mais caro que o orçado.", 17, negrito=True)
notas(s, "CPM abaixo do planejado significa compra eficiente de alcance. CPC acima significa que o "
         "alcance comprado era menos clicavel. Investigar mudanca de criativo, publico ou formato.")

# 6. Insight: veiculo
s = slide()
titulo(s, "Tiktok entregou menos da metade da verba planejada",
       "Investimento planejado e realizado por veículo; o número acima das barras é o pacing")
figura(s, "veiculo", 2.45, 10.0, reserva=1.15)
caixa(s, 0.8, 6.5, 11.8, 0.7,
      f"A campanha Inauguracao no Tiktok tinha {brl(n('campanha.inauguracao.plan_inv'))} e não teve nenhuma entrega na janela.",
      16, negrito=True, cor=ALERTA)
notas(s, "Meta e Youtube ficaram na faixa. O furo do Tiktok e concentrado e da para rastrear.")

# 7. Insight: campanha
s = slide()
titulo(s, "A média de 100% esconde campanhas de 0% a 134%",
       f"{mil(n('pacing.pares_na_faixa'))} pares na faixa de {mil(n('faixa.limite_inferior'))}% a {mil(n('faixa.limite_superior'))}%, "
       f"{mil(n('pacing.pares_abaixo_90'))} abaixo e {mil(n('pacing.pares_acima_110'))} acima")
figura(s, "campanha", 2.35, 11.4, reserva=0.3)
notas(s, f"Somando so os pares abaixo de {mil(n('faixa.limite_inferior'))}%, ficaram "
         f"{brl(n('pacing.verba_nao_entregue'))} de verba planejada sem virar entrega.")

# 8. Insight: cobertura
s = slide()
titulo(s, f"Este pacing descreve {pct(n('cobertura.share_realizado_no_plano'), 1)} do que foi gasto",
       f"{mil(n('arquivo.campanhas_sem_plano'))} das {mil(n('arquivo.campanhas'))} campanhas do arquivo não têm linha de plano")
figura(s, "cobertura", 2.6, 10.0, reserva=2.2)
caixa(s, 0.8, 5.55, 11.8, 1.4, [
    f"{brl(n('valor.realizado_fora'))} de entrega não pertencem a nenhum flight deste plano.",
    "O número de pacing é confiável para o que cobre. Ele não é a leitura da operação inteira.",
], 17, negrito=True, espaco=8)
notas(s, "Motivos de ficar fora: campanha sem plano, veiculo nao planejado para a campanha, e data "
         "fora da janela. A pergunta que fica e de negocio: essas campanhas tinham plano em outro lugar?")

# 9. Qualidade da base e o que nao respondemos
s = slide()
titulo(s, "O que achamos na base, e o que este número não responde")
caixa(s, 0.8, 2.25, 5.75, 0.5, "Achados na base", 19, negrito=True, cor=DESTAQUE)
caixa(s, 0.8, 2.85, 5.75, 3.6, [
    f"• {mil(n('zero.flights_denominador_invalido'))} flights com plano em branco",
    f"• Um deles entregou {brl(n('zero.realizado_sem_denominador'))}",
    f"• {mil(n('sobreposicao.grupos'))} pares com janela sobreposta",
    "• Extensão .xls, conteúdo CSV",
], 17, cor=TINTA2, espaco=14)
caixa(s, 7.0, 2.25, 5.5, 0.5, "Não responde", 19, negrito=True, cor=DESTAQUE)
caixa(s, 7.0, 2.85, 5.5, 3.6, [
    "• Se o plano estava bem feito",
    f"• Por que {pct(n('cobertura.share_realizado_fora'), 1)} não tem plano",
    "• Pacing de flight sobreposto",
    "• Venda e receita",
], 17, cor=TINTA2, espaco=14)
notas(s, "Estes pontos precisam aparecer na reuniao. O de janela sobreposta e o que mais muda numero.")

# 10. Decisoes de metodo
s = slide()
titulo(s, f"Três decisões de método mudam o resultado em até {_br(n('alt.maior_distorcao_razao'), 1)} vezes",
       "Cada alternativa foi calculada, não estimada")
figura(s, "dedup", 2.45, 8.5, reserva=1.4)
caixa(s, 0.8, 6.3, 11.9, 0.9,
      f"Sem deduplicar a entrega que cai em vários flights, o realizado ganharia {brl(n('dupla.investimento_inflado'))} que não existem.",
      16, negrito=True)
notas(s, f"{mil(n('join.linhas_multiplas'))} linhas de realizado caem em mais de um flight, uma delas "
         f"em {mil(n('join.max_flights_por_linha'))}. A regra usada: cada linha conta uma vez so.")

# 11. Proximos passos
s = slide()
titulo(s, "Próximos passos")
caixa(s, 0.85, 2.2, 11.7, 4.6, [
    f"1.  Decidir a verba do Tiktok: {pct(n('veiculo.tiktok_ads.pacing_inv'), 1)} de pacing, uma campanha zerada.",
    "2.  Revisar a meta de cliques. O CTR orçado não se sustentou.",
    f"3.  Trazer o plano das {mil(n('arquivo.campanhas_sem_plano'))} campanhas que rodaram sem ele.",
    f"4.  Corrigir os {mil(n('zero.flights_denominador_invalido'))} flights vazios e a janela sobreposta, na origem.",
    "5.  Acompanhar pacing de cliques, não só o de investimento.",
], 19, espaco=18)
notas(s, "Itens 1 e 2 sao decisao de midia. Itens 3 e 4 sao correcao de processo na origem do dado.")

# 12. Apendice
s = slide()
titulo(s, "Apêndice: como reproduzir")
caixa(s, 0.85, 2.15, 11.7, 4.4, [
    "Cada número tem lastro em analise/numeros.json.",
    "",
    "01_escopo.py  ·  dentro ou fora do plano",
    "02_sobreposicao.py  ·  flights sobrepostos, dupla contagem",
    "03_denominadores.py  ·  denominador nulo ou zerado",
    "04_pacing.py  ·  pacing por par, campanha e veículo",
    "05_alternativas.py  ·  alternativas e reconciliação",
    "06_series.py  ·  série, CPM, CPC, CTR, gasto fora",
    "07_destaques.py  ·  destaques por campanha",
    "",
    "Método: analise/decisoes.md  ·  Perfil: analise/perfil.md",
], 15.5, cor=TINTA2, espaco=5)
notas(s, "O conferidor conferir_numeros.py recusa qualquer numero do deck que nao tenha lastro no livro.")

ENTREGAS.mkdir(parents=True, exist_ok=True)
saida = ENTREGAS / "apresentacao.pptx"
prs.save(saida)
print(f"deck: {saida} ({len(prs.slides.__iter__.__self__._sldIdLst)} slides)")
