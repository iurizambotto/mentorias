from pathlib import Path

import pandas as pd
from perfilar import carregar, detectar_formato, padroes_de_nulo, perfilar


def test_csv_disguised_as_xls_with_bom(tmp_path: Path) -> None:
    arquivo = tmp_path / "base.xls"
    arquivo.write_bytes("﻿a;b\r\n1;2\r\n".encode())
    formato = detectar_formato(arquivo)
    assert formato["formato_real"] == "csv"
    assert formato["bom"] is True
    assert formato["extensao_confere"] is False
    assert formato["separador"] == ";"
    assert formato["quebra_linha"] == "CRLF"
    df = carregar(arquivo, formato)
    assert list(df.columns) == ["a", "b"]


def test_real_xlsx_is_recognized(tmp_path: Path) -> None:
    arquivo = tmp_path / "base.xlsx"
    pd.DataFrame({"a": [1]}).to_excel(arquivo, index=False)
    formato = detectar_formato(arquivo)
    assert formato["formato_real"] == "xlsx" and formato["extensao_confere"] is True


def test_null_pattern_and_discriminator() -> None:
    df = pd.DataFrame(
        {
            "tipo": ["plano", "plano", "real", "real", "real"],
            "inicio": ["x", "y", None, None, None],
            "fim": ["x", "y", None, None, None],
            "valor": [1, 2, 3, 4, 5],
        }
    )
    grupos = padroes_de_nulo(df)
    assert len(grupos) == 1
    assert set(grupos[0]["colunas"]) == {"inicio", "fim"}
    assert grupos[0]["discriminador"] == {"coluna": "tipo", "valores_quando_nulo": ["real"]}


def test_text_nulls_float_artifacts_and_variants() -> None:
    df = pd.DataFrame(
        {
            "obj": ["Alcance", "N/a", "Trafego", "n/a"],
            "valor": [19847.51953125, 10.0, 5.5, 1.0],
            "camp": ["Material Didatico", "Material Didatico Influ", "Outra", "Material Didatico Influ"],
        }
    )
    perfil = perfilar(df)
    colunas = perfil["colunas"]
    assert colunas["obj"]["nulos_em_texto"] == 2
    assert colunas["valor"]["artefatos_float"] == 1
    assert ["Material Didatico", "Material Didatico Influ"] in colunas["camp"]["variantes_de_prefixo"]
