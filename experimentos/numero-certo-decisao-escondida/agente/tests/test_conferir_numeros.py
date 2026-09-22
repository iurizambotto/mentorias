from pathlib import Path

import pytest
from conferir_numeros import conferir, extrair_numeros, tem_lastro


def valores(*vs: float) -> list[float]:
    return list(vs)


class TestExtracao:
    def test_pt_br_thousands_and_currency(self) -> None:
        nums = extrair_numeros("Realizado de R$ 1.047.334 no período")
        assert [n.candidatos for n in nums] == [[1047334.0]]

    def test_decimal_comma_and_percent(self) -> None:
        (n,) = extrair_numeros("pacing de 101,3%")
        assert n.percentual and n.candidatos == [101.3] and n.casas == 1

    def test_scale_words(self) -> None:
        nums = extrair_numeros("R$ 1,07 milhão e R$ 313 mil e 167,4 MM")
        assert [(n.candidatos[0], n.escala) for n in nums] == [(1.07, 1e6), (313.0, 1e3), (167.4, 1e6)]

    def test_lowercase_m_is_not_million(self) -> None:
        (n,) = extrair_numeros("a 5 m de distancia")
        assert n.escala == 1.0

    def test_dates_and_years_are_ignored(self) -> None:
        assert extrair_numeros("entre 28/05/2024 e 2024-07-31, ano 2023") == []

    def test_line_enumeration_is_ignored(self) -> None:
        assert extrair_numeros("1. Primeiro ponto\n2. Segundo ponto") == []

    def test_ambiguous_group_keeps_both_readings(self) -> None:
        (n,) = extrair_numeros("valor 1.047 registrado")
        assert set(n.candidatos) == {1047.0, 1.047}


class TestLastro:
    def test_rounded_display_matches(self) -> None:
        (n,) = extrair_numeros("R$ 1,07 milhão")
        assert tem_lastro(n, valores(1_070_515.0))

    def test_display_outside_rounding_does_not_match(self) -> None:
        # Real case from round 1: the stated total matched no reproducible cut.
        (n,) = extrair_numeros("R$ 1,07 milhão")
        assert not tem_lastro(n, valores(1_031_072.0, 1_053_076.0))

    def test_percent_matches_fraction_or_percent(self) -> None:
        (n,) = extrair_numeros("101,3%")
        assert tem_lastro(n, valores(1.01326))
        assert tem_lastro(n, valores(101.326))

    def test_thousands_display(self) -> None:
        (n,) = extrair_numeros("R$ 313 mil")
        assert tem_lastro(n, valores(312_999.0))


class TestConferir:
    def test_reports_only_unbacked_numbers(self, tmp_path: Path) -> None:
        livro = tmp_path / "numeros.json"
        livro.write_text('{"total": {"valor": 1047334.48}, "flights": {"valor": 42}}', encoding="utf-8")
        texto = tmp_path / "resposta.md"
        texto.write_text("Total de R$ 1.047.334 em 44 flights.", encoding="utf-8")
        sem_lastro, baixo_risco = conferir(texto, livro, estrito=False)
        assert [n.texto for n in sem_lastro] == ["44"]
        assert baixo_risco == []

    def test_small_integers_are_low_risk_unless_strict(self, tmp_path: Path) -> None:
        livro = tmp_path / "numeros.json"
        livro.write_text("{}", encoding="utf-8")
        texto = tmp_path / "t.md"
        texto.write_text("rodou 19 dos 30 dias", encoding="utf-8")
        sem_lastro, baixo_risco = conferir(texto, livro, estrito=False)
        assert sem_lastro == [] and len(baixo_risco) == 2
        sem_lastro, _ = conferir(texto, livro, estrito=True)
        assert len(sem_lastro) == 2

    def test_html_ignores_script_style_and_svg(self, tmp_path: Path) -> None:
        livro = tmp_path / "numeros.json"
        livro.write_text('{"a": {"valor": 500}}', encoding="utf-8")
        html = tmp_path / "d.html"
        html.write_text(
            "<html><style>.x{width:900px}</style><script>var d=[123456]</script>"
            "<svg><text>750000</text></svg><p>Total 500</p></html>",
            encoding="utf-8",
        )
        sem_lastro, _ = conferir(html, livro, estrito=False)
        assert sem_lastro == []

    def test_missing_ledger_fails_loudly(self, tmp_path: Path) -> None:
        texto = tmp_path / "t.md"
        texto.write_text("x", encoding="utf-8")
        with pytest.raises(FileNotFoundError):
            conferir(texto, tmp_path / "nao-existe.json", estrito=False)
