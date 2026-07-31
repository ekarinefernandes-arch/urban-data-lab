import pandas as pd

def preparar_populacao(
    dados: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepara a população residente por setor censitário.

    Retorna apenas as colunas necessárias para os mapas
    e análises espaciais.
    """

    colunas = [
        "CD_SETOR",
        "v0001",
    ]

    populacao = (
        dados[colunas]
        .copy()
        .rename(
            columns={
                "v0001": "populacao",
            }
        )
    )

    populacao["populacao"] = (
        pd.to_numeric(
            populacao["populacao"],
            errors="coerce",
        )
        .fillna(0)
        .astype(int)
    )

    return populacao
