import pandas as pd

from modules.ingestao.schemas import COLUNAS_ESQUEMA_INDICADORES
from modules.ingestao.validators.dataframe import validar_colunas_obrigatorias


def renda_para_formato_mapa(dados: pd.DataFrame) -> pd.DataFrame:
    """Adapta renda padronizada ao contrato largo usado pelos mapas atuais."""
    validar_colunas_obrigatorias(
        dados,
        COLUNAS_ESQUEMA_INDICADORES,
        contexto="renda padronizada",
    )
    resultado = (
        dados.pivot(
            index="codigo_setor",
            columns="indicador",
            values="valor",
        )
        .rename_axis(columns=None)
        .reset_index()
        .rename(columns={"codigo_setor": "CD_SETOR"})
    )
    resultado["CD_SETOR"] = resultado["CD_SETOR"].astype("string")

    colunas = [
        "CD_SETOR",
        "renda_media_responsavel",
        "renda_mediana_responsavel",
    ]
    for coluna in colunas:
        if coluna not in resultado.columns:
            resultado[coluna] = pd.NA
    return resultado.loc[:, colunas]
