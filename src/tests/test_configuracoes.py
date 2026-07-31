from pathlib import Path

from modules.config import (
    PASTA_DADOS,
    PASTA_EXPORTACOES_GPKG,
    PASTA_EXPORTACOES_MAPAS,
    RAIZ_PROJETO,
)


def test_raiz_do_projeto_aponta_para_o_repositorio() -> None:
    assert RAIZ_PROJETO.exists()
    assert (RAIZ_PROJETO / "README.md").exists()
    assert (RAIZ_PROJETO / "data").exists()


def test_pasta_de_dados_esta_centralizada_na_raiz_do_projeto() -> None:
    assert PASTA_DADOS == RAIZ_PROJETO / "data"
    assert isinstance(PASTA_DADOS, Path)


def test_saidas_cartograficas_ficam_fora_de_src() -> None:
    assert PASTA_EXPORTACOES_GPKG == PASTA_DADOS / "exports" / "geopackage"
    assert PASTA_EXPORTACOES_MAPAS == PASTA_DADOS / "exports" / "mapas"
