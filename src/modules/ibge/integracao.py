import geopandas as gpd
import pandas as pd
import warnings


def _normalizar_chave(serie: pd.Series) -> pd.Series:
    """Normaliza códigos vindos de CSV sem transformar ausentes em texto."""
    return serie.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)


def integrar_dados_geometria(
    malha: gpd.GeoDataFrame,
    indicadores: pd.DataFrame,
    chave: str = "CD_SETOR",
) -> gpd.GeoDataFrame:
    """
    Une uma malha geográfica com indicadores tabulares por uma chave comum.
    """

    if chave not in malha.columns:
        raise KeyError(f"A coluna '{chave}' não foi encontrada na malha.")

    if chave not in indicadores.columns:
        raise KeyError(f"A coluna '{chave}' não foi encontrada nos indicadores.")

    malha_normalizada = malha.copy()
    indicadores_normalizados = indicadores.copy()

    malha_normalizada[chave] = _normalizar_chave(malha_normalizada[chave])
    indicadores_normalizados[chave] = _normalizar_chave(
        indicadores_normalizados[chave]
    )

    duplicadas = indicadores_normalizados[chave].duplicated(keep=False)
    if duplicadas.any():
        exemplos = indicadores_normalizados.loc[duplicadas, chave].dropna().unique()[:5]
        raise ValueError(
            "A tabela de indicadores possui mais de uma linha por chave. "
            f"Exemplos: {', '.join(map(str, exemplos))}"
        )

    resultado = malha_normalizada.merge(
        indicadores_normalizados,
        on=chave,
        how="left",
        validate="many_to_one",
        indicator="_situacao_cruzamento",
    )

    sem_correspondencia = resultado["_situacao_cruzamento"].eq("left_only").sum()
    if sem_correspondencia:
        warnings.warn(
            f"{sem_correspondencia} de {len(resultado)} geometrias não "
            "encontraram indicador pela chave informada.",
            stacklevel=2,
        )

    return resultado.drop(columns="_situacao_cruzamento")
