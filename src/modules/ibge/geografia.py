from pathlib import Path

import geopandas as gpd


def carregar_malha(caminho: Path) -> gpd.GeoDataFrame:
    """
    Carrega um arquivo geográfico e retorna um GeoDataFrame.
    """

    caminho = caminho.resolve()

    if not caminho.is_file():
        raise FileNotFoundError(
            f"Arquivo geográfico não encontrado: {caminho}"
        )

    return gpd.read_file(str(caminho))


def filtrar_municipio(
    malha: gpd.GeoDataFrame,
    municipio: str,
) -> gpd.GeoDataFrame:
    """
    Filtra a malha pelo nome ou pelo código IBGE do município.
    """

    valor = str(municipio).strip()

    if valor.isdigit():
        filtro = malha["CD_MUN"].astype(str) == valor
    else:
        filtro = (
            malha["NM_MUN"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == valor.casefold()
        )

    resultado = malha[filtro].copy()

    if resultado.empty:
        raise ValueError(
            f"Município não encontrado na malha: {municipio}"
        )

    return resultado