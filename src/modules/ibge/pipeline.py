from pathlib import Path

import pandas as pd

from modules.ibge.censo import (
    carregar_dados_censo,
    filtrar_dados_municipio,
    localizar_csv,
)
from modules.ibge.entorno import preparar_entorno
from modules.ibge.indicadores import preparar_populacao
from modules.ibge.renda import preparar_renda
from modules.config import PASTA_BASICO


def construir_dataset_populacao(
    caminho_csv: Path | None = None,
    municipio: str = "4115200",
) -> pd.DataFrame:
    """
    Constrói um dataset pronto para integração espacial com a população por setor.
    """

    caminho_arquivo = (
        Path(caminho_csv)
        if caminho_csv is not None
        else localizar_csv(PASTA_BASICO)
    )

    dados_censo = carregar_dados_censo(caminho_arquivo)
    dados_municipio = filtrar_dados_municipio(dados_censo, municipio)

    return preparar_populacao(dados_municipio)


def construir_dataset_renda(
    codigo_municipio: str | int = "4115200",
) -> pd.DataFrame:
    """
    Constrói um dataset pronto para integração espacial com indicadores de renda.
    """

    return preparar_renda(codigo_municipio=codigo_municipio)


def construir_dataset_entorno(
    codigo_municipio: str | int = "4115200",
    variaveis: list[str] | None = None,
) -> pd.DataFrame:
    """
    Constrói um dataset pronto para integração espacial com indicadores de entorno.
    """

    return preparar_entorno(
        codigo_municipio=codigo_municipio,
        variaveis=variaveis or [],
    )
