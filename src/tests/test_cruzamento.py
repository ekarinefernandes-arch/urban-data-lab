import geopandas as gpd
import pandas as pd

from modules.ibge.cruzamento import (
    cruzar_censo_renda,
    cruzar_domicilios_entorno,
)


def test_cruzar_censo_renda_uniao_preserva_colunas() -> None:
    malha = gpd.GeoDataFrame(
        {"CD_SETOR": ["111", "222"]},
        geometry=gpd.points_from_xy([0, 1], [0, 1]),
        crs="EPSG:4326",
    )
    populacao = pd.DataFrame(
        {"CD_SETOR": ["111", "222"], "populacao": [100, 200]}
    )
    renda = pd.DataFrame(
        {"CD_SETOR": ["111", "222"], "renda_media_responsavel": [1500, 2500]}
    )

    resultado = cruzar_censo_renda(
        malha=malha,
        populacao=populacao,
        renda=renda,
    )

    assert isinstance(resultado, gpd.GeoDataFrame)
    assert "populacao" in resultado.columns
    assert "renda_media_responsavel" in resultado.columns
    assert resultado.shape[0] == 2


def test_cruzar_domicilios_entorno_uniao_preserva_colunas() -> None:
    malha = gpd.GeoDataFrame(
        {"CD_SETOR": ["111", "222"]},
        geometry=gpd.points_from_xy([0, 1], [0, 1]),
        crs="EPSG:4326",
    )
    domicilios = pd.DataFrame(
        {"CD_SETOR": ["111", "222"], "V00090": [10, 20]}
    )
    entorno = pd.DataFrame(
        {"CD_SETOR": ["111", "222"], "V05200": [5, 15]}
    )

    resultado = cruzar_domicilios_entorno(
        malha=malha,
        domicilios=domicilios,
        entorno=entorno,
    )

    assert isinstance(resultado, gpd.GeoDataFrame)
    assert "V00090" in resultado.columns
    assert "V05200" in resultado.columns
    assert resultado.shape[0] == 2
