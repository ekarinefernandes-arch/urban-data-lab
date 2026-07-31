from collections.abc import Iterable

import pandas as pd


def validar_colunas_obrigatorias(
    dados: pd.DataFrame,
    colunas: Iterable[str],
    *,
    contexto: str = "dataset",
) -> None:
    """Garante que um DataFrame contém as colunas exigidas."""
    ausentes = sorted(set(colunas) - set(dados.columns))
    if ausentes:
        raise KeyError(
            f"Colunas obrigatórias ausentes em {contexto}: {ausentes}"
        )


def validar_duplicidades(
    dados: pd.DataFrame,
    chaves: list[str],
    *,
    contexto: str = "dataset",
) -> None:
    """Rejeita mais de um registro para a mesma chave lógica."""
    duplicadas = dados.duplicated(subset=chaves, keep=False)
    if duplicadas.any():
        exemplos = dados.loc[duplicadas, chaves].head(5).to_dict("records")
        raise ValueError(
            f"Chaves duplicadas em {contexto}. Exemplos: {exemplos}"
        )
