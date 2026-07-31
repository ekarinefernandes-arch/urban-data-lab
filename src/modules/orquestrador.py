from pathlib import Path

import geopandas as gpd
import pandas as pd

from modules.visualizacao.mapas import preparar_mapa_tematico


def executar_fluxo_populacao(
    malha: gpd.GeoDataFrame,
    indicadores: pd.DataFrame,
    coluna_indicador: str = "populacao",
    chave: str = "CD_SETOR",
) -> gpd.GeoDataFrame:
    """
    Orquestra o fluxo principal de preparação de um mapa temático de população.
    """

    return preparar_mapa_tematico(
        malha=malha,
        indicadores=indicadores,
        coluna_indicador=coluna_indicador,
        chave=chave,
    )


def executar_fluxo_completo(
    malha: gpd.GeoDataFrame,
    indicadores: pd.DataFrame,
    coluna_indicador: str = "populacao",
    chave: str = "CD_SETOR",
    pasta_exportacao: Path | None = None,
    nome_arquivo: str = "mapa",
    camada: str = "camada",
) -> gpd.GeoDataFrame:
    """
    Orquestra a preparação e a exportação de um mapa temático.
    """

    mapa = executar_fluxo_populacao(
        malha=malha,
        indicadores=indicadores,
        coluna_indicador=coluna_indicador,
        chave=chave,
    )

    if pasta_exportacao is not None:
        from modules.visualizacao.mapas import exportar_gpkg

        exportar_gpkg(
            mapa=mapa,
            pasta_exportacao=pasta_exportacao,
            nome_arquivo=nome_arquivo,
            camada=camada,
        )

    return mapa
