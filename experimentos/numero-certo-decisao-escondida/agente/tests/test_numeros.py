import json
import math
from pathlib import Path

import pytest
from numeros import carregar, registrar


def test_register_and_upsert(tmp_path: Path) -> None:
    livro = tmp_path / "analise" / "numeros.json"
    registrar("total", 10.0, "total geral", linhas=5, script="s.py", livro=livro)
    registrar("total", 12.0, "total geral revisto", linhas=6, script="s.py", livro=livro)
    dados = carregar(livro)
    assert dados["total"]["valor"] == 12.0 and dados["total"]["linhas"] == 6
    assert json.loads(livro.read_text(encoding="utf-8"))["total"]["descricao"] == "total geral revisto"


@pytest.mark.parametrize("ruim", [math.nan, math.inf, -math.inf])
def test_rejects_non_finite_values(tmp_path: Path, ruim: float) -> None:
    # A silent division by zero must fail here, not reach the report.
    with pytest.raises(ValueError):
        registrar("x", ruim, "d", livro=tmp_path / "n.json")


def test_rejects_invalid_id(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        registrar("Id Com Espaço", 1.0, "d", livro=tmp_path / "n.json")


def test_records_decisions(tmp_path: Path) -> None:
    livro = tmp_path / "n.json"
    registrar("t", 1.0, "d", decisoes=["dedup de sobreposicao"], livro=livro)
    assert carregar(livro)["t"]["decisoes"] == ["dedup de sobreposicao"]
