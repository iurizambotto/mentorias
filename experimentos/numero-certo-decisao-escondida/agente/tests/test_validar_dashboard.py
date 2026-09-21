from pathlib import Path

from validar_dashboard import validar

BOM = (
    '<!doctype html><html lang="pt-BR"><head><meta name="viewport" content="width=device-width">'
    "<title>Painel</title></head><body><svg></svg>{extra}</body></html>"
)


def test_self_contained_passes(tmp_path: Path) -> None:
    f = tmp_path / "d.html"
    f.write_text(BOM.format(extra='<a href="https://exemplo.com">fonte</a>'), encoding="utf-8")
    assert validar(f) == []


def test_external_resources_are_rejected(tmp_path: Path) -> None:
    f = tmp_path / "d.html"
    f.write_text(
        BOM.format(extra='<script src="https://cdn.x/y.js"></script><style>@import url(https://f.x/a.css);</style>'),
        encoding="utf-8",
    )
    problemas = validar(f)
    assert any("script" in p for p in problemas)
    assert any("import" in p or "url(" in p for p in problemas)


def test_missing_title_and_chart(tmp_path: Path) -> None:
    f = tmp_path / "d.html"
    f.write_text("<html><body><p>oi</p></body></html>", encoding="utf-8")
    problemas = validar(f)
    assert any("title" in p for p in problemas)
    assert any("grafico" in p for p in problemas)
