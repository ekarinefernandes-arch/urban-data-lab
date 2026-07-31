import geopandas as gpd
import pandas as pd

from modules.orquestrador import executar_fluxo_populacao


def test_executar_fluxo_populacao_retorna_mapa_com_coluna() -> None:
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

    mapa = executar_fluxo_populacao(malha=malha, indicadores=indicadores)

    assert isinstance(mapa, gpd.GeoDataFrame)
    assert "populacao" in mapa.columns
    assert mapa.shape[0] == 2
