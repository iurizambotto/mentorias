"""Find numbers in a deliverable that have no backing in the ledger.

Reads markdown, text, HTML, DOCX or PPTX, extracts every number written in
Brazilian or English notation, and checks each against the ledger allowing only
the rounding implied by how the number was displayed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

_ESCALAS = [
    (re.compile(r"^\s*(?:bilh(?:ão|ao|ões|oes)|bi)\b", re.I), 1e9),
    (re.compile(r"^\s*(?:milh(?:ão|ao|ões|oes)|mi)\b", re.I), 1e6),
    (re.compile(r"^\s*(?:MM|M)\b"), 1e6),
    (re.compile(r"^\s*mil\b", re.I), 1e3),
    (re.compile(r"^\s*[kK]\b"), 1e3),
]
_NUMERO = re.compile(
    r"(?<![\w.,])("
    r"\d{1,3}(?:\.\d{3})+(?:,\d+)?"
    r"|\d{1,3}(?:,\d{3}){2,}(?:\.\d+)?"
    r"|\d+,\d+"
    r"|\d+\.\d+"
    r"|\d+"
    r")(?![\w])"
)
_DATAS = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?\b"),
    re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"),
    re.compile(r"\b[a-zç]{3}\.?/\d{2,4}\b", re.I),
    re.compile(r"\b\d{1,2}:\d{2}\b"),
]
_ANO = re.compile(r"^(?:19|20|21)\d{2}$")
_ENUMERACAO = re.compile(r"^\s*\d+[.)]\s", re.M)
_LIMITE_BAIXO_RISCO = 31


@dataclass
class NumeroEncontrado:
    texto: str
    candidatos: list[float]
    casas: int
    escala: float = 1.0
    percentual: bool = False
    contexto: str = ""
    moeda: bool = field(default=False)

    @property
    def baixo_risco(self) -> bool:
        return (
            self.escala == 1.0
            and not self.percentual
            and not self.moeda
            and self.casas == 0
            and all(c <= _LIMITE_BAIXO_RISCO for c in self.candidatos)
        )


def _interpretar(token: str) -> tuple[list[float], int]:
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", token):
        inteiro, _, dec = token.partition(",")
        valor = float(inteiro.replace(".", "") + ("." + dec if dec else ""))
        casas = len(dec)
        if token.count(".") == 1 and not dec:
            return [valor, float(token)], 0
        return [valor], casas
    if re.fullmatch(r"\d{1,3}(?:,\d{3}){2,}(?:\.\d+)?", token):
        inteiro, _, dec = token.partition(".")
        return [float(inteiro.replace(",", "") + ("." + dec if dec else ""))], len(dec)
    if "," in token:
        inteiro, dec = token.split(",")
        return [float(f"{inteiro}.{dec}")], len(dec)
    if "." in token:
        return [float(token)], len(token.split(".")[1])
    return [float(token)], 0


def extrair_numeros(texto: str) -> list[NumeroEncontrado]:
    limpo = _ENUMERACAO.sub(lambda m: " " * len(m.group(0)), texto)
    for padrao in _DATAS:
        limpo = padrao.sub(lambda m: " " * len(m.group(0)), limpo)

    encontrados: list[NumeroEncontrado] = []
    for m in _NUMERO.finditer(limpo):
        token = m.group(1)
        if _ANO.match(token):
            continue
        candidatos, casas = _interpretar(token)
        depois = limpo[m.end() : m.end() + 12]
        antes = limpo[max(0, m.start() - 4) : m.start()]
        escala = 1.0
        for padrao, fator in _ESCALAS:
            if padrao.match(depois):
                escala = fator
                break
        percentual = bool(re.match(r"^\s*%", depois))
        moeda = "R$" in antes or "$" in antes
        inicio, fim = max(0, m.start() - 30), min(len(texto), m.end() + 30)
        encontrados.append(
            NumeroEncontrado(
                texto=token,
                candidatos=candidatos,
                casas=casas,
                escala=escala,
                percentual=percentual,
                moeda=moeda,
                contexto=" ".join(texto[inicio:fim].split()),
            )
        )
    return encontrados


def tem_lastro(numero: NumeroEncontrado, valores: list[float]) -> bool:
    tolerancia = 0.5 * 10 ** (-numero.casas) * numero.escala
    for candidato in numero.candidatos:
        exibido = candidato * numero.escala
        for v in valores:
            alvos = [v, v * 100] if numero.percentual else [v]
            for alvo in alvos:
                if abs(alvo - exibido) <= tolerancia + 1e-9 * max(1.0, abs(alvo)):
                    return True
    return False


class _TextoVisivel(HTMLParser):
    _IGNORAR = {"script", "style", "svg", "noscript"}

    def __init__(self) -> None:
        super().__init__()
        self.partes: list[str] = []
        self._profundidade = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._IGNORAR:
            self._profundidade += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._IGNORAR and self._profundidade:
            self._profundidade -= 1

    def handle_data(self, data: str) -> None:
        if not self._profundidade:
            self.partes.append(data)


def extrair_texto(caminho: Path) -> str:
    sufixo = caminho.suffix.lower()
    if sufixo in {".html", ".htm"}:
        parser = _TextoVisivel()
        parser.feed(caminho.read_text(encoding="utf-8"))
        return "\n".join(parser.partes)
    if sufixo == ".docx":
        from docx import Document

        doc = Document(str(caminho))
        partes = [p.text for p in doc.paragraphs]
        for tabela in doc.tables:
            for linha in tabela.rows:
                partes.append(" | ".join(c.text for c in linha.cells))
        return "\n".join(partes)
    if sufixo == ".pptx":
        from pptx import Presentation

        partes = []
        for slide in Presentation(str(caminho)).slides:
            for forma in slide.shapes:
                if forma.has_text_frame:
                    partes.append(forma.text_frame.text)
                if getattr(forma, "has_table", False) and forma.has_table:
                    for linha in forma.table.rows:
                        partes.append(" | ".join(c.text for c in linha.cells))
        return "\n".join(partes)
    return caminho.read_text(encoding="utf-8")


def conferir(caminho: Path, livro: Path, *, estrito: bool) -> tuple[list[NumeroEncontrado], list[NumeroEncontrado]]:
    if not livro.exists():
        raise FileNotFoundError(f"livro de numeros nao encontrado: {livro}")
    valores = [float(item["valor"]) for item in json.loads(livro.read_text(encoding="utf-8")).values()]
    sem_lastro: list[NumeroEncontrado] = []
    baixo_risco: list[NumeroEncontrado] = []
    for numero in extrair_numeros(extrair_texto(caminho)):
        if tem_lastro(numero, valores):
            continue
        if numero.baixo_risco and not estrito:
            baixo_risco.append(numero)
        else:
            sem_lastro.append(numero)
    return sem_lastro, baixo_risco


def main() -> int:
    parser = argparse.ArgumentParser(description="Confere numeros de uma entrega contra o livro.")
    parser.add_argument("arquivos", nargs="+", type=Path)
    parser.add_argument("--livro", type=Path, default=Path("analise/numeros.json"))
    parser.add_argument("--estrito", action="store_true", help="inteiros pequenos tambem reprovam")
    args = parser.parse_args()

    total = 0
    for arquivo in args.arquivos:
        sem_lastro, baixo_risco = conferir(arquivo, args.livro, estrito=args.estrito)
        print(f"== {arquivo}: {len(sem_lastro)} sem lastro, {len(baixo_risco)} inteiros pequenos para revisar")
        for n in sem_lastro:
            print(f"  SEM LASTRO  {n.texto:>14s}  ...{n.contexto}...")
        for n in baixo_risco:
            print(f"  revisar    {n.texto:>14s}  ...{n.contexto}...")
        total += len(sem_lastro)
    if total:
        print(f"\n{total} numero(s) sem lastro. Registre no livro com o script que o calcula, ou tire do texto.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
