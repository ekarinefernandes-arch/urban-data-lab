import geopandas as gpd
import pandas as pd

from modules.ibge.integracao import integrar_dados_geometria


def _normalizar_chave_setor(df: pd.DataFrame, chave: str = "CD_SETOR") -> pd.DataFrame:
    resultado = df.copy()
    if chave not in resultado.columns:
        raise KeyError(f"A coluna '{chave}' não foi encontrada no DataFrame.")

    resultado[chave] = (
        resultado[chave]
        .astype("string")
        .str.strip()
    )
    return resultado


def cruzar_censo_renda(
    malha: gpd.GeoDataFrame,
    populacao: pd.DataFrame,
    renda: pd.DataFrame,
    chave: str = "CD_SETOR",
) -> gpd.GeoDataFrame:
    """
    Une malha, população e renda por setor censitário.
    """

    malha_normalizada = _normalizar_chave_setor(malha, chave)
    populacao_normalizada = _normalizar_chave_setor(populacao, chave)
    renda_normalizada = _normalizar_chave_setor(renda, chave)

    resultado = integrar_dados_geometria(
        malha_normalizada,
        populacao_normalizada,
        chave=chave,
    )
    resultado = integrar_dados_geometria(
        resultado,
        renda_normalizada,
        chave=chave,
    )

    return resultado


def cruzar_domicilios_entorno(
    malha: gpd.GeoDataFrame,
    domicilios: pd.DataFrame,
    entorno: pd.DataFrame,
    chave: str = "CD_SETOR",
) -> gpd.GeoDataFrame:
    """
    Une malha, domicílios e entorno por setor censitário.
    """

    malha_normalizada = _normalizar_chave_setor(malha, chave)
    domicilios_normalizados = _normalizar_chave_setor(domicilios, chave)
    entorno_normalizado = _normalizar_chave_setor(entorno, chave)

    resultado = integrar_dados_geometria(
        malha_normalizada,
        domicilios_normalizados,
        chave=chave,
    )
    resultado = integrar_dados_geometria(
        resultado,
        entorno_normalizado,
        chave=chave,
    )

    return resultado
