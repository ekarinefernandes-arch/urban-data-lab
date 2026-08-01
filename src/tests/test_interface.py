from pathlib import Path

import pandas as pd

from modules.ibge import interface


def _criar_base_municipios(caminho: Path) -> Path:
    pd.DataFrame(
        [
            {"CD_UF": "35", "NM_UF": "Sao Paulo", "CD_MUN": "3551009", "NM_MUN": "Sao Vicente"},
            {"CD_UF": "24", "NM_UF": "Rio Grande do Norte", "CD_MUN": "2413003", "NM_MUN": "Sao Vicente"},
        ]
    ).to_csv(caminho, sep=";", index=False)
    return caminho


def test_lista_municipio_com_codigo_da_uf_selecionada(tmp_path: Path) -> None:
    interface._carregar_base_censo_cache.cache_clear()
    caminho = _criar_base_municipios(tmp_path / "municipios.csv")

    assert interface.listar_municipios_por_uf("SP", caminho) == [
        ("3551009", "Sao Vicente")
    ]
    assert interface.listar_municipios_por_uf("RN", caminho) == [
        ("2413003", "Sao Vicente")
    ]


def test_base_censo_e_carregada_uma_vez(monkeypatch, tmp_path: Path) -> None:
    interface._carregar_base_censo_cache.cache_clear()
    caminho = tmp_path / "base.csv"
    caminho.touch()
    chamadas = 0

    def carregar(_caminho: Path) -> pd.DataFrame:
        nonlocal chamadas
        chamadas += 1
        return pd.DataFrame({"CD_UF": ["35"]})

    monkeypatch.setattr(interface, "carregar_dados_censo", carregar)

    primeira = interface.carregar_base_censo(caminho)
    segunda = interface.carregar_base_censo(caminho)

    assert primeira is segunda
    assert chamadas == 1
