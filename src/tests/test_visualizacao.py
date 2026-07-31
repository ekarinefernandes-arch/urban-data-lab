import geopandas as gpd
import pandas as pd

from modules.visualizacao.mapas import preparar_mapa_tematico
from modules.visualizacao.estilos import obter_estilo_mapa


def test_preparar_mapa_tematico_retorna_geodataframe() -> None:
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

    mapa = preparar_mapa_tematico(malha, indicadores, coluna_indicador="populacao")

    assert isinstance(mapa, gpd.GeoDataFrame)
    assert "populacao" in mapa.columns
    assert mapa.shape[0] == 2


def test_estilo_de_renda_possui_identidade_visual_propria() -> None:
    estilo = obter_estilo_mapa("renda")

    assert estilo.cmap == "YlOrBr"
    assert estilo.numero_classes == 5
