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

def preparar_renda(
    dados_municipio,
    coluna_renda,
):
    renda = dados_municipio[
        [
            "CD_SETOR",
            coluna_renda,
        ]
    ].copy()

    renda = renda.rename(
        columns={
            coluna_renda: "renda_media",
        }
    )

    renda["CD_SETOR"] = (
        renda["CD_SETOR"]
        .astype(str)
        .str.strip()
    )

    renda["renda_media"] = (
        renda["renda_media"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    renda["renda_media"] = (
        renda["renda_media"]
        .pipe(
            __import__("pandas").to_numeric,
            errors="coerce",
        )
    )

    return renda
