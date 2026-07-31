from pathlib import Path

import pandas as pd


def ler_csv(
    caminho: Path,
    *,
    colunas: list[str] | None = None,
    separador: str = ";",
    codificacao: str = "utf-8",
    tipos: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Lê um CSV sem aplicar regras específicas da fonte."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {arquivo}")

    return pd.read_csv(
        arquivo,
        sep=separador,
        encoding=codificacao,
        usecols=colunas,
        dtype=tipos,
        low_memory=False,
    )
