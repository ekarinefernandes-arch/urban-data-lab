from pathlib import Path

import pandas as pd

from modules.datasets.adapters import renda_para_formato_mapa
from modules.ibge.censo import obter_codigo_municipio
from modules.ingestao.normalizers.renda import normalizar_renda_ibge
from modules.ingestao.quality import ResultadoNormalizacao
from modules.ingestao.normalizers.renda import normalizar_renda_ibge_com_qualidade
from modules.ingestao.readers.csv import ler_csv
from .constantes import (
    COLUNA_SETOR,
    COLUNA_SETOR_RENDA,
    PASTA_RENDA,
    V_RENDA_MEDIA,
    V_RENDA_MEDIANA,
)


def localizar_arquivo_renda() -> Path:
    """
    Localiza o arquivo CSV de renda dentro da pasta do Censo.
    """

    if not PASTA_RENDA.exists():
        raise FileNotFoundError(
            "A pasta de renda não foi encontrada:\n"
            f"{PASTA_RENDA}"
        )

    arquivos = sorted(PASTA_RENDA.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo CSV foi encontrado em:\n"
            f"{PASTA_RENDA}"
        )

    if len(arquivos) > 1:
        nomes = "\n".join(
            f"- {arquivo.name}" for arquivo in arquivos
        )

        raise RuntimeError(
            "Foi encontrado mais de um arquivo CSV "
            "na pasta de renda:\n\n"
            f"{nomes}"
        )

    return arquivos[0]


def ler_renda(
    arquivo: Path | None = None,
) -> pd.DataFrame:
    """
    Lê as variáveis de renda média e renda mediana
    por setor censitário.
    """

    padronizado = ler_renda_padronizada(arquivo=arquivo)
    return renda_para_formato_mapa(padronizado)


def ler_renda_padronizada(
    arquivo: Path | None = None,
) -> pd.DataFrame:
    """Lê renda bruta e devolve o esquema interno estável em formato longo."""
    return normalizar_renda_ibge(ler_renda_bruta(arquivo=arquivo))


def ler_renda_bruta(
    arquivo: Path | None = None,
) -> pd.DataFrame:
    """Lê somente as colunas brutas necessárias para o fluxo de renda."""
    caminho = arquivo or localizar_arquivo_renda()
    colunas = [
        COLUNA_SETOR_RENDA,
        V_RENDA_MEDIA,
        V_RENDA_MEDIANA,
    ]
    return ler_csv(
        caminho,
        colunas=colunas,
        separador=";",
        codificacao="utf-8",
        tipos={COLUNA_SETOR_RENDA: "string"},
    )


def ler_renda_com_qualidade(
    arquivo: Path | None = None,
) -> ResultadoNormalizacao:
    """Lê e normaliza renda, mantendo relatório e registros inválidos."""
    return normalizar_renda_ibge_com_qualidade(
        ler_renda_bruta(arquivo=arquivo)
    )


def filtrar_renda_municipio(
    df: pd.DataFrame,
    codigo_municipio: str | int,
) -> pd.DataFrame:
    """
    Filtra os setores pertencentes ao município informado.
    """

    codigo = str(codigo_municipio).strip()
    if not codigo.isdigit():
        codigo = obter_codigo_municipio(codigo)

    if len(codigo) != 7 or not codigo.isdigit():
        raise ValueError(
            "O código do município deve possuir sete dígitos."
        )

    filtro = df[COLUNA_SETOR].str.startswith(
        codigo,
        na=False,
    )

    return df.loc[filtro].copy()


def preparar_renda(
    codigo_municipio: str | int,
) -> pd.DataFrame:
    """
    Lê e prepara a base de renda de um município.
    """

    df = ler_renda()

    df = filtrar_renda_municipio(
        df=df,
        codigo_municipio=codigo_municipio,
    )

    return df.reset_index(drop=True)
