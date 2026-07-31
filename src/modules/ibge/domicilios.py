from pathlib import Path

import pandas as pd

from modules.ibge.censo import obter_codigo_municipio
from .constantes import (
    COLUNA_SETOR,
    COLUNA_SETOR_DOMICILIOS,
    PASTA_DOMICILIOS,
)


def localizar_arquivo_domicilios() -> Path:
    """
    Localiza o arquivo CSV de características dos domicílios.
    """

    if not PASTA_DOMICILIOS.exists():
        raise FileNotFoundError(
            "A pasta de domicílios não foi encontrada:\n"
            f"{PASTA_DOMICILIOS}"
        )

    arquivos = sorted(PASTA_DOMICILIOS.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo CSV foi encontrado na pasta:\n"
            f"{PASTA_DOMICILIOS}"
        )

    if len(arquivos) > 1:
        nomes = "\n".join(
            f"- {arquivo.name}" for arquivo in arquivos
        )

        raise RuntimeError(
            "Foi encontrado mais de um arquivo CSV na pasta "
            "de domicílios.\n\n"
            f"{nomes}"
        )

    return arquivos[0]


def ler_domicilios(
    arquivo: Path | None = None,
    variaveis: list[str] | None = None,
) -> pd.DataFrame:
    """
    Lê a base de características dos domicílios do Censo 2022.

    Como o arquivo possui mais de 400 colunas e cerca de 747 MB,
    recomenda-se informar somente as variáveis necessárias.

    A coluna original 'setor' é padronizada para 'CD_SETOR'.
    """

    caminho = arquivo or localizar_arquivo_domicilios()

    colunas_leitura = None

    if variaveis is not None:
        colunas_leitura = list(
            dict.fromkeys(
                [COLUNA_SETOR_DOMICILIOS, *variaveis]
            )
        )

    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8",
        usecols=colunas_leitura,
        dtype={
            COLUNA_SETOR_DOMICILIOS: "string",
        },
        low_memory=False,
    )

    if COLUNA_SETOR_DOMICILIOS not in df.columns:
        raise KeyError(
            f"A coluna '{COLUNA_SETOR_DOMICILIOS}' "
            "não foi encontrada na base de domicílios."
        )

    df = df.rename(
        columns={
            COLUNA_SETOR_DOMICILIOS: COLUNA_SETOR
        }
    )

    df[COLUNA_SETOR] = (
        df[COLUNA_SETOR]
        .astype("string")
        .str.strip()
    )

    return df


def filtrar_domicilios_municipio(
    df: pd.DataFrame,
    codigo_municipio: str | int,
) -> pd.DataFrame:
    """
    Filtra os setores censitários de um município.

    O código municipal do IBGE deve possuir sete dígitos.
    """

    codigo = str(codigo_municipio).strip()
    if not codigo.isdigit():
        codigo = obter_codigo_municipio(codigo)

    if len(codigo) != 7 or not codigo.isdigit():
        raise ValueError(
            "O código do município deve possuir "
            "exatamente sete dígitos."
        )

    if COLUNA_SETOR not in df.columns:
        raise KeyError(
            f"A coluna '{COLUNA_SETOR}' não foi encontrada "
            "no DataFrame."
        )

    filtro = df[COLUNA_SETOR].str.startswith(
        codigo,
        na=False,
    )

    return df.loc[filtro].copy()


def converter_variaveis_numericas(
    df: pd.DataFrame,
    variaveis: list[str],
) -> pd.DataFrame:
    """
    Converte as variáveis informadas para formato numérico.

    Valores não numéricos, como 'X', são convertidos para ausentes.
    O DataFrame original não é alterado.
    """

    resultado = df.copy()

    for variavel in variaveis:
        if variavel not in resultado.columns:
            raise KeyError(
                f"A variável '{variavel}' não foi encontrada "
                "na base de domicílios."
            )

        resultado[variavel] = pd.to_numeric(
            resultado[variavel],
            errors="coerce",
        )

    return resultado


def preparar_domicilios(
    codigo_municipio: str | int,
    variaveis: list[str],
    converter_numericos: bool = True,
) -> pd.DataFrame:
    """
    Lê, filtra e prepara as variáveis de domicílios
    para um município.

    Parameters
    ----------
    codigo_municipio:
        Código IBGE municipal com sete dígitos.
    variaveis:
        Lista dos códigos das variáveis do IBGE.
    converter_numericos:
        Quando True, converte números e transforma valores como
        'X' em valores ausentes.

    Returns
    -------
    pandas.DataFrame
        Base municipal contendo CD_SETOR e as variáveis solicitadas.
    """

    if not variaveis:
        raise ValueError(
            "Informe pelo menos uma variável de domicílios."
        )

    df = ler_domicilios(
        variaveis=variaveis,
    )

    df = filtrar_domicilios_municipio(
        df=df,
        codigo_municipio=codigo_municipio,
    )

    if converter_numericos:
        df = converter_variaveis_numericas(
            df=df,
            variaveis=variaveis,
        )

    return df.reset_index(drop=True)