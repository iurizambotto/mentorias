"""Passo 12. Monta entregas/apresentacao.pptx, 16:9, um slide por mensagem.

Os graficos saem em PNG a 200 dpi, sem titulo dentro da imagem, porque o
titulo do slide ja carrega a mensagem. Uma cor de destaque por grafico, no
dado que o titulo aponta; o resto em cinza.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402
from pptx.enum.text import PP_ALIGN  # noqa: E402
from pptx.util import Emu, Inches, Pt  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))

LIVRO = Path("analise/numeros.json")
SAIDA = Path("entregas/apresentacao.pptx")
FIGURAS = Path("analise/figuras")

AZUL = "#2a78d6"
VERMELHO = "#d03b3b"
LARANJA = "#eb6834"
CINZA = "#b8b7b0"
CINZA_ESCURO = "#52514e"
TINTA = RGBColor(0x0B, 0x0B, 0x0B)
TINTA2 = RGBColor(0x52, 0x51, 0x4E)
DESTAQUE = RGBColor(0x2A, 0x78, 0xD6)

L: dict[str, dict] = json.loads(LIVRO.read_text(encoding="utf-8"))


def num(chave: str) -> float:
    return L[chave]["valor"]


def br(valor: float, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def reais(valor: float) -> str:
    return f"R$ {br(valor)}"


def figura(nome: str) -> Path:
    FIGURAS.mkdir(parents=True, exist_ok=True)
    return FIGURAS / f"{nome}.png"


def _estilo(ax: plt.Axes) -> None:
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#d9d8d3")
    ax.tick_params(colors=CINZA_ESCURO, labelsize=11, length=0)
    ax.grid(False)


def grafico_pacing_metrica() -> Path:
    caminho = figura("pacing_metrica")
    rotulos = ["Investimento", "Impressões", "Cliques"]
    valores = [
        num("total.pacing_investimento"),
        num("total.pacing_impressoes"),
        num("total.pacing_cliques"),
    ]
    fig, ax = plt.subplots(figsize=(8.6, 3.5))
    barras = ax.barh(rotulos, valores, color=[AZUL, AZUL, CINZA], height=0.58)
    ax.axvline(100, color=CINZA_ESCURO, linestyle=(0, (5, 4)), linewidth=1.6)
    ax.text(100, -0.78, "plano = 100%", ha="center", fontsize=10.5, color=CINZA_ESCURO)
    for barra, valor in zip(barras, valores):
        ax.text(
            valor + 3, barra.get_y() + barra.get_height() / 2,
            f"{br(valor, 1)}%", va="center", fontsize=13, fontweight="bold", color="#0b0b0b",
        )
    ax.set_xlim(0, max(valores) * 1.22)
    ax.invert_yaxis()
    ax.set_xticks([])
    _estilo(ax)
    fig.tight_layout()
    fig.savefig(caminho, dpi=200, transparent=True)
    plt.close(fig)
    return caminho


def grafico_veiculo() -> Path:
    caminho = figura("pacing_veiculo")
    tab = pd.read_csv("analise/pacing_veiculo.csv").sort_values("pacing_investimento")
    rotulos = list(tab["Veiculo"])
    valores = [v * 100 for v in tab["pacing_investimento"]]
    cores = [VERMELHO if v == "Tiktok Ads" else CINZA for v in rotulos]
    fig, ax = plt.subplots(figsize=(8.6, 3.5))
    barras = ax.barh(rotulos, valores, color=cores, height=0.58)
    ax.axvline(100, color=CINZA_ESCURO, linestyle=(0, (5, 4)), linewidth=1.6)
    ax.text(100, -0.78, "plano = 100%", ha="center", fontsize=10.5, color=CINZA_ESCURO)
    for barra, valor in zip(barras, valores):
        ax.text(
            valor + 2.5, barra.get_y() + barra.get_height() / 2,
            f"{br(valor, 1)}%", va="center", fontsize=13, fontweight="bold", color="#0b0b0b",
        )
    ax.set_xlim(0, max(valores) * 1.2)
    ax.invert_yaxis()
    ax.set_xticks([])
    _estilo(ax)
    fig.tight_layout()
    fig.savefig(caminho, dpi=200, transparent=True)
    plt.close(fig)
    return caminho


def grafico_cliques() -> Path:
    """O denominador de cliques concentrado num flight, e o efeito de tira-lo."""
    caminho = figura("cliques")
    rotulos = ["Pacing de cliques\ncomo está no plano", "Pacing de cliques sem o\nflight de CTR atípico"]
    valores = [num("total.pacing_cliques"), num("cliques.pacing_sem_maior_flight")]
    fig, ax = plt.subplots(figsize=(8.6, 3.3))
    barras = ax.barh(rotulos, valores, color=[CINZA, AZUL], height=0.5)
    ax.axvline(100, color=CINZA_ESCURO, linestyle=(0, (5, 4)), linewidth=1.6)
    ax.text(100, -0.66, "plano = 100%", ha="center", fontsize=10.5, color=CINZA_ESCURO)
    for barra, valor in zip(barras, valores):
        ax.text(
            valor + 2.5, barra.get_y() + barra.get_height() / 2,
            f"{br(valor, 1)}%", va="center", fontsize=13, fontweight="bold", color="#0b0b0b",
        )
    ax.set_xlim(0, 125)
    ax.invert_yaxis()
    ax.set_xticks([])
    _estilo(ax)
    fig.tight_layout()
    fig.savefig(caminho, dpi=200, transparent=True)
    plt.close(fig)
    return caminho


def grafico_campanhas() -> Path:
    caminho = figura("campanhas")
    tab = pd.read_csv("analise/pacing_campanha.csv").nlargest(8, "plan_investimento")
    tab = tab.iloc[::-1]
    y = range(len(tab))
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    altura = 0.38
    ax.barh([i + altura / 2 for i in y], tab["plan_investimento"], height=altura,
            color=LARANJA, label="Planejado")
    ax.barh([i - altura / 2 for i in y], tab["real_investimento"], height=altura,
            color=AZUL, label="Realizado na janela")
    ax.set_yticks(list(y))
    ax.set_yticklabels(tab["Campanha"], fontsize=11)
    ax.set_xticks([])
    for i, (plano, real) in enumerate(zip(tab["plan_investimento"], tab["real_investimento"])):
        ax.text(plano + 2600, i + altura / 2, br(plano, 0), va="center", fontsize=11,
                color=CINZA_ESCURO)
        ax.text(real + 2600, i - altura / 2, br(real, 0), va="center", fontsize=11,
                color=CINZA_ESCURO)
    ax.set_xlim(0, float(tab["plan_investimento"].max()) * 1.26)
    # Fora da area das barras: no canto inferior direito ela cobria a ultima linha.
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, -0.01), ncol=2,
              frameon=False, fontsize=11.5, labelcolor=CINZA_ESCURO)
    _estilo(ax)
    fig.tight_layout()
    fig.savefig(caminho, dpi=200, transparent=True)
    plt.close(fig)
    return caminho


def grafico_cobertura() -> Path:
    """Quanto do investimento realizado pertence a este plano."""
    caminho = figura("cobertura")
    dentro = num("total.real_investimento")
    fora_camp = num("fora.campanha_sem_plano_investimento")
    fora_vei = num("fora.veiculo_sem_plano_investimento")
    fora_jan = num("fora.janela_investimento")
    rotulos = [
        "Dentro do plano",
        "Campanha sem\nlinha de plano",
        "Data fora da\njanela do flight",
        "Veículo fora do\nplano da campanha",
    ]
    valores = [dentro, fora_camp, fora_jan, fora_vei]
    cores = [AZUL, CINZA, CINZA, CINZA]
    fig, ax = plt.subplots(figsize=(8.8, 3.6))
    barras = ax.bar(rotulos, valores, color=cores, width=0.56)
    for barra, valor in zip(barras, valores):
        ax.text(
            barra.get_x() + barra.get_width() / 2, valor + 250_000,
            f"R$ {br(valor / 1e6, 2)} mi", ha="center", fontsize=12,
            fontweight="bold", color="#0b0b0b",
        )
    ax.set_ylim(0, max(valores) * 1.2)
    ax.set_yticks([])
    ax.tick_params(axis="x", labelsize=11)
    _estilo(ax)
    fig.tight_layout()
    fig.savefig(caminho, dpi=200, transparent=True)
    plt.close(fig)
    return caminho


# ---------------------------------------------------------------- montagem

def limpar_layout(slide) -> None:
    """Remove placeholder que o layout traz e o slide nao usa."""
    for forma in list(slide.placeholders):
        if not forma.has_text_frame or not forma.text_frame.text.strip():
            forma._element.getparent().remove(forma._element)


def caixa(slide, x: float, y: float, w: float, h: float, texto: str, tamanho: int,
          *, negrito: bool = False, cor: RGBColor = TINTA, espaco: float = 1.18,
          linhas_negrito: tuple[int, ...] = ()):
    forma = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    quadro = forma.text_frame
    quadro.word_wrap = True
    for i, linha in enumerate(texto.split("\n")):
        p = quadro.paragraphs[0] if i == 0 else quadro.add_paragraph()
        p.text = linha
        p.line_spacing = espaco
        p.space_after = Pt(6)
        p.alignment = PP_ALIGN.LEFT
        destacada = i in linhas_negrito
        for run in p.runs:
            run.font.size = Pt(tamanho)
            run.font.bold = negrito or destacada
            run.font.color.rgb = TINTA if destacada else cor
            run.font.name = "Calibri"
    return forma


def titulo(slide, texto: str) -> None:
    """Preenche o placeholder de titulo do layout, nao uma caixa de texto.

    O titulo precisa ser o placeholder de verdade: e o que o leitor de tela
    anuncia como titulo do slide e o que o validador procura.
    """
    forma = slide.shapes.title
    forma.left, forma.top = Inches(0.62), Inches(0.4)
    forma.width, forma.height = Inches(12.1), Inches(1.2)
    quadro = forma.text_frame
    quadro.word_wrap = True
    quadro.text = texto
    p = quadro.paragraphs[0]
    p.line_spacing = 1.06
    p.alignment = PP_ALIGN.LEFT
    for run in p.runs:
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = TINTA
        run.font.name = "Calibri"


def notas(slide, texto: str) -> None:
    slide.notes_slide.notes_text_frame.text = texto


def imagem(slide, caminho: Path, x: float, y: float, largura: float) -> None:
    slide.shapes.add_picture(str(caminho), Inches(x), Inches(y), width=Inches(largura))


def construir() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    branco = prs.slide_layouts[6]
    so_titulo = prs.slide_layouts[5]

    def novo(texto_titulo: str | None = None):
        """Capa sem titulo usa layout em branco; os demais usam Somente Titulo.

        A limpeza roda depois de preencher o titulo, senao o placeholder vazio
        seria removido junto com os que o layout traz e nao serao usados.
        """
        if texto_titulo is None:
            slide = prs.slides.add_slide(branco)
            limpar_layout(slide)
            return slide
        slide = prs.slides.add_slide(so_titulo)
        titulo(slide, texto_titulo)
        limpar_layout(slide)
        return slide

    # 1. Capa
    s = novo()
    caixa(s, 0.9, 1.95, 11.9, 2.6,
          "O dinheiro planejado foi entregue quase na régua,\ne rendeu mais mídia do que o plano previa",
          34, negrito=True, espaco=1.16)
    caixa(s, 0.9, 4.35, 11.9, 1.3,
          f"Pacing de investimento de {br(num('total.pacing_investimento'))}% e de impressões de "
          f"{br(num('total.pacing_impressoes'))}%.\nResultados de mídia, plano de maio a julho de 2024.",
          18, cor=TINTA2)
    caixa(s, 0.9, 6.4, 11.6, 0.5,
          "Base: BASE DE PACING_v2.csv.xls", 13, cor=TINTA2)
    notas(s, "Deck gerado por analise/scripts/11_apresentacao.py a partir de analise/numeros.json. "
             "Todo número citado tem script que o reproduz.")

    # 2. A pergunta
    s = novo("A pergunta")
    caixa(s, 0.9, 2.0, 11.5, 2.6,
          "“Como foi a performance das campanhas?\nA gente entregou o que tinha planejado?”",
          30, cor=DESTAQUE, espaco=1.22)
    caixa(s, 0.9, 4.5, 11.5, 1.6,
          "Pacing é o realizado dividido pelo planejado, contando só a entrega que caiu dentro da "
          "janela do flight, no mesmo veículo. Campanha sem linha de planejado fica fora da conta.",
          17, cor=TINTA2)
    notas(s, "A pergunta nas palavras de quem perguntou. A regra de pacing abaixo é a que foi "
             "acordada: janela do flight, mesmo veículo, campanha sem plano fora da conta.")

    # 3. A resposta
    s = novo("Sim, em dinheiro. E com mais mídia entregue do que o previsto")
    caixa(s, 0.62, 1.55, 12.1, 0.8,
          f"Entregamos {reais(num('total.real_investimento'))} contra "
          f"{reais(num('total.plan_investimento'))} planejados.", 19, cor=TINTA2)
    indicadores = [
        (f"{br(num('total.pacing_investimento'))}%", "pacing de investimento"),
        (f"{br(num('total.pacing_impressoes'))}%", "pacing de impressões"),
        (reais(num("flight.investimento_sem_entrega")), "plano que não foi ao ar"),
    ]
    for i, (valor, rotulo) in enumerate(indicadores):
        x = 0.62 + i * 4.12
        caixa(s, x, 2.75, 4.0, 1.3, valor, 34, negrito=True, cor=DESTAQUE, espaco=1.0)
        caixa(s, x, 3.95, 4.0, 0.9, rotulo, 17, cor=TINTA2)
    caixa(s, 0.62, 5.5, 12.1, 1.2,
          f"Base: {int(num('linhas.planejado'))} flights planejados e "
          f"{int(num('linhas.realizado_no_plano'))} dias de entrega dentro das janelas contratadas, "
          f"de {int(num('linhas.realizado'))} dias registrados no arquivo.", 15, cor=TINTA2)
    notas(s, "O terceiro indicador é o flight da Inauguracao no Tiktok, que não registrou "
             "nenhum dia de entrega na própria janela. É o único do plano nessa situação.")

    # 4. Insight: dinheiro na régua, mídia acima
    s = novo("Em dinheiro o plano fechou no ponto, e a mídia veio acima do previsto")
    imagem(s, grafico_pacing_metrica(), 1.4, 1.75, 10.5)
    caixa(s, 0.62, 5.85, 12.1, 1.1,
          f"A mesma verba comprou {br(num('total.gap_impressoes'), 0)} impressões a mais do que o "
          f"plano previa. O CPM real veio abaixo do orçado.", 17, cor=TINTA2)
    notas(s, f"Investimento {br(num('total.pacing_investimento'))}%, impressões "
             f"{br(num('total.pacing_impressoes'))}%, cliques {br(num('total.pacing_cliques'))}%. "
             "Cliques está em cinza de propósito: o slide seguinte mostra que ele é premissa de "
             "planejamento, não entrega. Diferença de investimento: "
             f"{reais(num('total.gap_investimento'))}.")

    # 5. Insight: Tiktok
    s = novo("O Tiktok Ads entregou menos da metade do que foi planejado")
    imagem(s, grafico_veiculo(), 1.4, 1.75, 10.5)
    caixa(s, 0.62, 5.85, 12.1, 1.2,
          f"São {reais(num('veiculo.tiktok.plan_investimento'))} planejados e "
          f"{reais(num('veiculo.tiktok.real_investimento'))} entregues. Metade da diferença é um "
          f"flight só, a Inauguracao, que não foi ao ar.", 17, cor=TINTA2)
    notas(s, f"Em impressões o Tiktok fica em {br(num('veiculo.tiktok.pacing_impressoes'))}%, pior "
             "que em investimento. Ação: separar a cobrança em duas, sub-entrega de ritmo nos "
             "flights que rodaram e o flight que não foi ao ar, de "
             f"{reais(num('camp.inauguracao.plan_investimento'))}.")

    # 6. Insight: cliques
    s = novo("O déficit de cliques não existe: é premissa de CTR de um flight só")
    imagem(s, grafico_cliques(), 1.4, 1.8, 10.5)
    caixa(s, 0.62, 5.7, 12.1, 1.4,
          f"O plano deriva cliques de uma premissa de CTR que vai de {br(num('ctr.plano_minimo'))}% a "
          f"{br(num('ctr.plano_maximo'))}%. Um flight concentra "
          f"{br(num('cliques.concentracao_maior_flight_pct'))}% dos cliques planejados. Sem ele, o "
          f"pacing é {br(num('cliques.pacing_sem_maior_flight'))}%.", 17, cor=TINTA2)
    notas(s, f"O flight é o da Freeshop no Meta Ads, com premissa de CTR de "
             f"{br(num('ctr.plano_maximo'))}%, quatro vezes a mediana do próprio plano, que é "
             f"{br(num('ctr.plano_mediana'))}%. O CTR efetivo da entrega foi "
             f"{br(num('ctr.realizado'))}%. Não há déficit de cliques a explicar; há premissa a "
             "corrigir no próximo plano.")

    # 7. Insight: campanha a campanha
    s = novo("Campanha a campanha, o desvio de verba é pequeno fora das inaugurações")
    imagem(s, grafico_campanhas(), 1.9, 1.7, 9.6)
    caixa(s, 0.62, 6.15, 12.1, 1.0,
          f"Das {int(num('campanha.com_pacing_investimento'))} campanhas com pacing calculável, "
          f"{int(num('campanha.dentro_80_120'))} ficaram entre "
          f"{br(num('faixa.limite_inferior_pct'), 0)}% e {br(num('faixa.limite_superior_pct'), 0)}% "
          f"do orçado.", 17, cor=TINTA2)
    notas(s, f"{int(num('campanha.abaixo_80'))} campanha abaixo de 80% e "
             f"{int(num('campanha.acima_120'))} acima de 120%. A maior diferença absoluta numa "
             f"campanha é {reais(num('campanha.maior_gap_absoluto'))}. O agregado não está "
             "escondendo extremos que se anulam.")

    # 8. Insight: cobertura do plano
    s = novo("Este plano cobre uma fração pequena do que foi veiculado")
    imagem(s, grafico_cobertura(), 1.9, 1.8, 9.6)
    caixa(s, 0.62, 5.95, 12.1, 1.3,
          f"Só {br(num('reconciliacao.share_dentro_do_plano_pct'))}% do investimento realizado no "
          f"arquivo pertence a este plano. As {int(num('fora.campanhas_sem_plano_distintas'))} "
          f"campanhas sem linha de planejado somam "
          f"{reais(num('fora.campanha_sem_plano_investimento'))}.", 17, cor=TINTA2)
    notas(s, f"Total realizado no arquivo: {reais(num('reconciliacao.investimento_realizado_total'))}. "
             "Isso não é erro de entrega e não entra no pacing. Mas muda o peso da conversa: o "
             "pacing descreve bem o plano e descreve pouco a operação inteira. Pergunta para a "
             "área: essas campanhas pertencem a outro plano?")

    # 9. O que não responde e qualidade da base
    s = novo("O que esta análise não responde, e o que olhar na base")
    caixa(s, 0.62, 1.7, 6.0, 4.6,
          "Não responde\n"
          f"• Pacing por flight onde o plano se sobrepõe: "
          f"{int(num('sobreposicao.pares_de_flights'))} pares de janelas cruzadas.\n"
          "• Se a sobra de impressões é preço ou formato.\n"
          "• Se as campanhas fora do plano têm outro plano.",
          16, cor=TINTA2, espaco=1.24)
    caixa(s, 6.9, 1.7, 5.9, 4.6,
          "Qualidade da base\n"
          "• Extensão .xls, conteúdo CSV.\n"
          f"• Duas tabelas empilhadas: {int(num('linhas.planejado'))} flights e "
          f"{int(num('linhas.realizado'))} dias de entrega.\n"
          f"• {int(num('denominador.flights_investimento_nulo'))} flights sem valor orçado.\n"
          f"• {int(num('denominador.pares_sem_pacing_investimento'))} par sem pacing, "
          "nunca mostrado como 0%.",
          16, cor=TINTA2, espaco=1.24)
    notas(s, "O par sem pacing é Joao Pessoa - Não Pulavel no Youtube Ads: teve "
             f"{int(num('sem_denominador.dias_entregues'))} dias de entrega real sem nada orçado "
             "contra o que comparar. As sobreposições estão em "
             f"{int(num('sobreposicao.combinacoes_afetadas'))} combinações de campanha e veículo. "
             "Somar a coluna de investimento do arquivo inteiro, sem separar pela coluna Base, "
             "mistura orçamento com gasto. Há também "
             f"{int(num('denominador.flights_entrega_zerada'))} flights com entrega orçada em zero.")

    # 10. Decisões de método
    s = novo("Duas decisões de método mudariam muito o número")
    caixa(s, 0.62, 1.7, 12.1, 4.6,
          "Cada entrega conta uma vez, mesmo com vários flights a reivindicando\n"
          f"Escolhido {br(num('total.pacing_investimento'))}% e "
          f"{br(num('total.pacing_impressoes'))}%  |  alternativa "
          f"{br(num('alt.sem_dedup_pacing_investimento'))}% e "
          f"{br(num('alt.sem_dedup_pacing_impressoes'))}%\n"
          "\n"
          "Só conta a entrega dentro da janela do flight\n"
          f"Escolhido {br(num('total.pacing_investimento'))}%  |  sem filtro de janela "
          f"{br(num('alt.sem_janela_pacing_investimento'))}%",
          18, cor=TINTA2, espaco=1.3, linhas_negrito=(0, 3))
    notas(s, f"São {int(num('sobreposicao.entregas_em_mais_de_um_flight'))} dias de entrega "
             f"disputados, um deles por {int(num('sobreposicao.max_flights_por_entrega'))} "
             "flights. O realizado cobre de 2023 a 2024 e o plano cobre maio a julho de 2024. "
             "Outras duas decisões testadas, com efeito menor: tratar a data de término como "
             f"exclusiva daria {br(num('alt.fim_exclusivo_pacing_investimento'))}%, e agrupar "
             "campanhas por prefixo do nome não muda nada, "
             f"{br(num('alt.prefixo_pacing_investimento'))}%, porque as "
             f"{int(num('alt.prefixo_linhas_remapeadas'))} linhas afetadas caem fora das janelas.")

    # 11. Próximos passos
    s = novo("Próximos passos")
    caixa(s, 0.62, 1.7, 12.1, 4.7,
          f"1. Tirar do faturamento o flight de {reais(num('flight.investimento_sem_entrega'))} "
          "que não foi ao ar, e cobrar a sub-entrega do Tiktok.\n"
          "2. Confirmar se essa campanha foi cancelada ou não reportada.\n"
          f"3. Corrigir a premissa de CTR, contra o efetivo de {br(num('ctr.realizado'))}%.\n"
          "4. Rever para baixo a premissa de CPM das inaugurações.\n"
          f"5. Definir se as {int(num('fora.campanhas_sem_plano_distintas'))} campanhas sem "
          "plano têm outro plano.\n"
          "6. Pedir uma chave de flight no realizado.",
          18, cor=TINTA2, espaco=1.36)
    notas(s, f"A premissa de CTR do plano hoje vai de {br(num('ctr.plano_minimo'))}% a "
             f"{br(num('ctr.plano_maximo'))}%, contra CTR efetivo de {br(num('ctr.realizado'))}%. "
             "Os itens 1 e 2 têm dinheiro associado e prazo de faturamento. Os itens 3 e 4 são "
             "para o próximo ciclo de planejamento. Os itens 5 e 6 são de processo.")

    # 12. Apêndice
    s = novo("Apêndice: como reproduzir")
    caixa(s, 0.62, 1.7, 12.1, 4.4,
          "Scripts, em ordem, a partir da pasta do projeto:\n"
          "perfilar.py, 01_escopo, 02_sobreposicao, 03_pacing, 04_alternativas, 05_cortes,\n"
          "06_cliques, 07_citados, 09_tabela_livro, 08_dashboard, 10_powerbi, 11_apresentacao\n"
          "\n"
          "Cada número deste deck está em analise/numeros.json, com o script que o calcula.\n"
          "As escolhas de método estão em analise/decisoes.md, com o valor da alternativa.\n"
          "\n"
          "Entregas: insights.docx, insights.pdf, dashboard.html e a pasta powerbi.",
          17, cor=TINTA2, espaco=1.34)
    notas(s, "O conferidor conferir_numeros.py roda contra o docx, o html e este pptx, e falha se "
             "algum número exibido não tiver lastro no livro.")

    return prs


if __name__ == "__main__":
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    apresentacao = construir()
    apresentacao.save(SAIDA)
    print(f"apresentacao: {SAIDA} ({len(apresentacao.slides.__iter__.__self__._sldIdLst)} slides)")
