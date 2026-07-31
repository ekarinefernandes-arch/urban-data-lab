import pandas as pd


MARCADORES_AUSENTES = {
    "",
    "-",
    "...",
    "NA",
    "N/A",
    "NULL",
    "X",
}


def converter_moeda_brasileira(
    valores: pd.Series,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Converte moeda brasileira e identifica ausências e valores inválidos."""
    texto = (
        valores.astype("string")
        .str.strip()
        .str.replace("\u00a0", "", regex=False)
        .str.replace("R$", "", regex=False)
        .str.replace(" ", "", regex=False)
    )
    ausentes = texto.isna() | texto.str.upper().isin(MARCADORES_AUSENTES)
    possui_virgula = texto.str.contains(",", regex=False, na=False)
    normalizado = texto.copy()
    normalizado.loc[possui_virgula] = (
        normalizado.loc[possui_virgula]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    numerico = pd.to_numeric(normalizado.mask(ausentes), errors="coerce")
    nao_numericos = ~ausentes & numerico.isna()
    return numerico.astype("Float64"), ausentes, nao_numericos
