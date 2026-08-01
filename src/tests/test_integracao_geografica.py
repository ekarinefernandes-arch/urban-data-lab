import geopandas as gpd
import pandas as pd

from modules.ibge import geografia
from modules.ibge.integracao import integrar_dados_geometria


def test_integrar_dados_geometria_preserva_geometria_e_colunas() -> None:
    malha = gpd.GeoDataFrame(
        {
            "CD_SETOR": ["111", "222"],
            "NM_MUN": ["Maringá", "Maringá"],
        },
        geometry=gpd.points_from_xy([0, 1], [0, 1]),
        crs="EPSG:4326",
    )

    indicadores = pd.DataFrame(
        {
            "CD_SETOR": ["111", "222"],
            "populacao": [10, 20],
        }
    )

    resultado = integrar_dados_geometria(malha, indicadores)

    assert isinstance(resultado, gpd.GeoDataFrame)
    assert "populacao" in resultado.columns
    assert resultado.shape[0] == 2
    assert resultado.geometry.notnull().all()


def test_localiza_geopackage_na_pasta_da_uf(monkeypatch, tmp_path) -> None:
    pasta_sp = tmp_path / "SP"
    pasta_sp.mkdir()
    geopackage = pasta_sp / "setores_CD2022.gpkg"
    shapefile = pasta_sp / "setores_CD2022.shp"
    geopackage.touch()
    shapefile.touch()

    monkeypatch.setattr(geografia, "PASTA_GEOGRAFIA", tmp_path)

    assert geografia.localizar_arquivo_geografia("sp") == geopackage
