import pandas as pd


def normalizar_codigo_territorial(
    valores: pd.Series,
    *,
    tamanho: int,
    nome: str,
    erros: str = "raise",
) -> pd.Series:
    """Normaliza e valida códigos territoriais sem convertê-los em números."""
    if erros not in {"raise", "coerce"}:
        raise ValueError("erros deve ser 'raise' ou 'coerce'.")

    codigos = (
        valores.astype("string")
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )
    invalidos = codigos.notna() & ~codigos.str.fullmatch(rf"\d{{{tamanho}}}")
    if invalidos.any() and erros == "raise":
        exemplos = codigos.loc[invalidos].drop_duplicates().head(5).tolist()
        raise ValueError(
            f"{nome} deve possuir {tamanho} dígitos. Exemplos inválidos: {exemplos}"
        )
    if erros == "coerce":
        codigos = codigos.mask(invalidos, pd.NA)
    return codigos
