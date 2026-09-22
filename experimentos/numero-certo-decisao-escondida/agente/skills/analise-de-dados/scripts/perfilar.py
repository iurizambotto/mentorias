"""Generic first look at any tabular file, trusting nothing about it.

Detects the real format regardless of the extension, then profiles columns,
finds groups of columns that are null together (a sign that two tables were
stacked into one) and the column that explains that split, text tokens that
mean null, float32 export artifacts, and category variants sharing a prefix.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

_NULOS_TEXTO = {
    "",
    "n/a",
    "na",
    "n.a.",
    "-",
    "--",
    "null",
    "none",
    "nan",
    "#n/a",
    "nd",
    "n/d",
    "sem informacao",
    "sem informação",
}
_MAGICAS = [(b"PK\x03\x04", "xlsx"), (b"\xd0\xcf\x11\xe0", "xls"), (b"PAR1", "parquet")]


def detectar_formato(caminho: Path) -> dict:
    cabeca = caminho.read_bytes()[:65536]
    extensao = caminho.suffix.lower().lstrip(".")
    formato = next((nome for magica, nome in _MAGICAS if cabeca.startswith(magica)), None)
    info: dict = {"arquivo": caminho.name, "extensao": extensao, "bytes": caminho.stat().st_size}

    if formato is None:
        bom = cabeca.startswith(b"\xef\xbb\xbf")
        try:
            texto = cabeca.decode("utf-8-sig")
            encoding = "utf-8-sig" if bom else "utf-8"
        except UnicodeDecodeError:
            texto, encoding = cabeca.decode("latin-1"), "latin-1"
        inicio = texto.lstrip()[:1]
        if inicio in "{[":
            formato = "json"
        else:
            formato = "csv"
            try:
                info["separador"] = csv.Sniffer().sniff(texto[:8192], delimiters=",;\t|").delimiter
            except csv.Error:
                info["separador"] = ","
            info["quebra_linha"] = "CRLF" if "\r\n" in texto else "LF"
        info.update({"encoding": encoding, "bom": bom})
    else:
        info.update({"encoding": None, "bom": False})

    equivalentes = {
        "csv": {"csv", "txt", "tsv"},
        "xlsx": {"xlsx", "xlsm"},
        "xls": {"xls"},
        "json": {"json"},
        "parquet": {"parquet"},
    }
    info["formato_real"] = formato
    info["extensao_confere"] = extensao in equivalentes.get(formato, set())
    return info


def carregar(caminho: Path, formato: dict) -> pd.DataFrame:
    real = formato["formato_real"]
    if real == "csv":
        return pd.read_csv(caminho, sep=formato.get("separador", ","), encoding=formato.get("encoding") or "utf-8")
    if real in {"xlsx", "xls"}:
        return pd.read_excel(caminho)
    if real == "json":
        return pd.read_json(caminho)
    if real == "parquet":
        return pd.read_parquet(caminho)
    raise ValueError(f"formato nao suportado: {real}")


def _artefatos_float(serie: pd.Series) -> int:
    valores = pd.to_numeric(serie, errors="coerce").dropna().to_numpy(dtype=float)
    if valores.size == 0:
        return 0
    arredondado = np.round(valores, 2)
    como_float32 = arredondado.astype(np.float32).astype(float)
    return int(np.sum((valores != arredondado) & np.isclose(valores, como_float32, rtol=0, atol=1e-9)))


def _variantes_de_prefixo(serie: pd.Series, limite: int = 200) -> list[list[str]]:
    valores = sorted({str(v).strip() for v in serie.dropna().unique()})
    if not 1 < len(valores) <= limite:
        return []
    grupos: list[list[str]] = []
    for base in valores:
        if len(base) < 4:
            continue
        filhos = [v for v in valores if v != base and v.lower().startswith(base.lower() + " ")]
        if filhos:
            grupos.append([base, *filhos])
    return grupos


def padroes_de_nulo(df: pd.DataFrame) -> list[dict]:
    mascaras: dict[bytes, list[str]] = {}
    for coluna in df.columns:
        mascara = df[coluna].isna().to_numpy()
        if 0 < mascara.sum() < len(df):
            mascaras.setdefault(mascara.tobytes(), []).append(coluna)

    grupos = []
    for chave, colunas in mascaras.items():
        mascara = np.frombuffer(chave, dtype=bool)
        grupo = {"colunas": colunas, "linhas_nulas": int(mascara.sum()), "discriminador": None}
        for candidata in df.columns:
            if candidata in colunas or df[candidata].nunique(dropna=False) > 10:
                continue
            quando_nulo = set(df.loc[mascara, candidata].astype(str))
            quando_cheio = set(df.loc[~mascara, candidata].astype(str))
            if quando_nulo and not quando_nulo & quando_cheio:
                grupo["discriminador"] = {"coluna": candidata, "valores_quando_nulo": sorted(quando_nulo)}
                break
        grupos.append(grupo)
    return grupos


def perfilar(df: pd.DataFrame) -> dict:
    colunas = {}
    for coluna in df.columns:
        serie = df[coluna]
        texto = serie.dropna().astype(str).str.strip().str.lower()
        colunas[coluna] = {
            "tipo": str(serie.dtype),
            "nulos": int(serie.isna().sum()),
            "nulos_em_texto": int(texto.isin(_NULOS_TEXTO).sum()) if serie.dtype == object else 0,
            "distintos": int(serie.nunique(dropna=True)),
            "exemplos": [str(v) for v in serie.dropna().unique()[:5]],
            "artefatos_float": _artefatos_float(serie) if pd.api.types.is_float_dtype(serie) else 0,
            "variantes_de_prefixo": _variantes_de_prefixo(serie) if serie.dtype == object else [],
        }
        if pd.api.types.is_numeric_dtype(serie):
            colunas[coluna].update({"min": float(serie.min()), "max": float(serie.max()), "soma": float(serie.sum())})
    return {
        "linhas": len(df),
        "colunas_total": df.shape[1],
        "duplicatas_exatas": int(df.duplicated().sum()),
        "colunas": colunas,
        "padroes_de_nulo": padroes_de_nulo(df),
    }


def _markdown(formato: dict, perfil: dict) -> str:
    linhas = ["# Perfil do arquivo", "", "## Formato", ""]
    linhas += [f"- {k}: {v}" for k, v in formato.items()]
    if not formato["extensao_confere"]:
        linhas.append(
            f"- ATENCAO: a extensao .{formato['extensao']} nao corresponde ao conteudo, que e {formato['formato_real']}"
        )
    linhas += [
        "",
        f"## Forma: {perfil['linhas']} linhas, {perfil['colunas_total']} colunas, "
        f"{perfil['duplicatas_exatas']} duplicatas exatas",
        "",
    ]
    linhas += [
        "| coluna | tipo | nulos | nulos em texto | distintos | artefatos float | exemplos |",
        "|---|---|---|---|---|---|---|",
    ]
    for nome, c in perfil["colunas"].items():
        exemplos = "; ".join(c["exemplos"])[:80]
        linhas.append(
            f"| {nome} | {c['tipo']} | {c['nulos']} | {c['nulos_em_texto']} | {c['distintos']} "
            f"| {c['artefatos_float']} | {exemplos} |"
        )
    linhas += ["", "## Colunas nulas juntas", ""]
    if not perfil["padroes_de_nulo"]:
        linhas.append("Nenhum grupo encontrado.")
    for g in perfil["padroes_de_nulo"]:
        linhas.append(f"- {', '.join(g['colunas'])}: nulas juntas em {g['linhas_nulas']} linhas")
        if g["discriminador"]:
            d = g["discriminador"]
            linhas.append(
                f"  - explicado por `{d['coluna']}` = {d['valores_quando_nulo']}. "
                "Provavel mistura de duas tabelas com grao diferente"
            )
    linhas += ["", "## Variantes de categoria por prefixo", ""]
    variantes = [(n, g) for n, c in perfil["colunas"].items() for g in c["variantes_de_prefixo"]]
    linhas += [f"- {n}: {g}" for n, g in variantes] or ["Nenhuma."]
    return "\n".join(linhas) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Perfil generico de um arquivo tabular.")
    parser.add_argument("arquivo", type=Path)
    parser.add_argument("--saida", type=Path, default=Path("analise"))
    args = parser.parse_args()

    formato = detectar_formato(args.arquivo)
    perfil = perfilar(carregar(args.arquivo, formato))
    args.saida.mkdir(parents=True, exist_ok=True)
    (args.saida / "perfil.json").write_text(
        json.dumps({"formato": formato, **perfil}, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    md = _markdown(formato, perfil)
    (args.saida / "perfil.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
