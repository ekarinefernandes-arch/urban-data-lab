from pathlib import Path

import pandas as pd

from modules.ibge.censo import obter_codigo_municipio
from modules.config import (
    COLUNA_SETOR,
    COLUNA_SETOR_ENTORNO,
    PASTA_ENTORNO,
)


def localizar_arquivo_entorno() -> Path:
    if not PASTA_ENTORNO.exists():
        raise FileNotFoundError(
            "A pasta de entorno não foi encontrada:\n"
            f"{PASTA_ENTORNO}"
        )

    arquivos = sorted(PASTA_ENTORNO.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo CSV foi encontrado em:\n"
            f"{PASTA_ENTORNO}"
        )

    if len(arquivos) > 1:
        nomes = "\n".join(f"- {arquivo.name}" for arquivo in arquivos)
        raise RuntimeError(
            "Foi encontrado mais de um arquivo CSV na pasta de entorno:\n\n"
            f"{nomes}"
        )

    return arquivos[0]


def ler_entorno(
    arquivo: Path | None = None,
    variaveis: list[str] | None = None,
) -> pd.DataFrame:
    caminho = arquivo or localizar_arquivo_entorno()

    colunas_leitura = None
    if variaveis is not None:
        colunas_leitura = list(
            dict.fromkeys(
                [COLUNA_SETOR_ENTORNO, *variaveis]
            )
        )

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8",
        usecols=colunas_leitura,
        dtype={COLUNA_SETOR_ENTORNO: "string"},
        low_memory=False,
    )

    if COLUNA_SETOR_ENTORNO not in df.columns:
        raise KeyError(
            f"A coluna '{COLUNA_SETOR_ENTORNO}' não foi encontrada na base de entorno."
        )

    df = df.rename(columns={COLUNA_SETOR_ENTORNO: COLUNA_SETOR})
    df[COLUNA_SETOR] = df[COLUNA_SETOR].astype("string").str.strip()

    return df


def filtrar_entorno_municipio(
    df: pd.DataFrame,
    codigo_municipio: str | int,
) -> pd.DataFrame:
    codigo = str(codigo_municipio).strip()
    if not codigo.isdigit():
        codigo = obter_codigo_municipio(codigo)

    if len(codigo) != 7 or not codigo.isdigit():
        raise ValueError(
            "O código do município deve possuir exatamente sete dígitos."
        )

    if COLUNA_SETOR not in df.columns:
        raise KeyError(
            f"A coluna '{COLUNA_SETOR}' não foi encontrada no DataFrame."
        )

    filtro = df[COLUNA_SETOR].str.startswith(codigo, na=False)
    return df.loc[filtro].copy()


def converter_variaveis_numericas(
    df: pd.DataFrame,
    variaveis: list[str],
) -> pd.DataFrame:
    resultado = df.copy()

    for variavel in variaveis:
        if variavel not in resultado.columns:
            raise KeyError(
                f"A variável '{variavel}' não foi encontrada na base de entorno."
            )

        resultado[variavel] = pd.to_numeric(
            resultado[variavel],
            errors="coerce",
        )

    return resultado


def preparar_entorno(
    codigo_municipio: str | int,
    variaveis: list[str],
    converter_numericos: bool = True,
) -> pd.DataFrame:
    if not variaveis:
        raise ValueError(
            "Informe pelo menos uma variável de entorno."
        )

    df = ler_entorno(variaveis=variaveis)
    df = filtrar_entorno_municipio(df=df, codigo_municipio=codigo_municipio)

    if converter_numericos:
        df = converter_variaveis_numericas(df=df, variaveis=variaveis)

    return df.reset_index(drop=True)
