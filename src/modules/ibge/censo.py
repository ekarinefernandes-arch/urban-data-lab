from pathlib import Path
import unicodedata

import pandas as pd
from modules.config import PASTA_BASICO


def localizar_csv(pasta: Path) -> Path:
    """
    Localiza o arquivo CSV dos dados básicos do Censo 2022.

    A busca é feita dentro da pasta informada e de todas
    as suas subpastas.
    """

    pasta = Path(pasta)

    if not pasta.exists():
        raise FileNotFoundError(
            f"A pasta informada não existe:\n{pasta}"
        )

    arquivos_csv = list(
        pasta.rglob("Agregados_por_setores_basico_BR.csv")
    )

    if not arquivos_csv:
        arquivos_csv = list(pasta.rglob("*.csv"))

    if not arquivos_csv:
        raise FileNotFoundError(
            f"Nenhum arquivo CSV foi encontrado em:\n{pasta}"
        )

    return arquivos_csv[0]


def carregar_dados_censo(
    caminho_csv: Path,
) -> pd.DataFrame:
    """
    Carrega o arquivo CSV dos dados básicos do Censo 2022.

    A função testa combinações de codificação e separador
    para evitar erros de leitura.
    """

    caminho_csv = Path(caminho_csv)

    if not caminho_csv.exists():
        raise FileNotFoundError(
            f"O arquivo CSV não foi encontrado:\n{caminho_csv}"
        )

    configuracoes = [
        {
            "sep": ";",
            "encoding": "utf-8",
        },
        {
            "sep": ";",
            "encoding": "latin-1",
        },
        {
            "sep": ",",
            "encoding": "utf-8",
        },
        {
            "sep": ",",
            "encoding": "latin-1",
        },
    ]

    ultimo_erro = None

    for configuracao in configuracoes:
        try:
            dados = pd.read_csv(
                caminho_csv,
                sep=configuracao["sep"],
                encoding=configuracao["encoding"],
                dtype=str,
                low_memory=False,
            )

            if len(dados.columns) > 1:
                print(
                    "Dados do Censo carregados com sucesso."
                )
                print(
                    f"Quantidade de registros: {len(dados)}"
                )
                print(
                    f"Quantidade de colunas: {len(dados.columns)}"
                )

                return dados

        except Exception as erro:
            ultimo_erro = erro

    raise ValueError(
        "Não foi possível carregar o arquivo CSV.\n"
        f"Arquivo: {caminho_csv}\n"
        f"Último erro encontrado: {ultimo_erro}"
    )


def filtrar_dados_municipio(
    dados: pd.DataFrame,
    municipio: str,
) -> pd.DataFrame:
    """
    Filtra os dados censitários pelo nome ou pelo código IBGE
    do município.

    Exemplos:
        filtrar_dados_municipio(dados, "Maringá")
        filtrar_dados_municipio(dados, "4115200")
    """

    municipio = str(municipio).strip()

    colunas_obrigatorias = {
        "CD_MUN",
        "NM_MUN",
    }

    colunas_ausentes = (
        colunas_obrigatorias - set(dados.columns)
    )

    if colunas_ausentes:
        raise KeyError(
            "As seguintes colunas não foram encontradas "
            f"nos dados: {sorted(colunas_ausentes)}"
        )

    if municipio.isdigit():
        resultado = dados[
            dados["CD_MUN"]
            .astype(str)
            .str.strip()
            == municipio
        ].copy()

    else:
        municipio_normalizado = _normalizar_texto(municipio)
        resultado = dados[
            dados["NM_MUN"]
            .astype(str)
            .map(_normalizar_texto)
            == municipio_normalizado
        ].copy()

    if resultado.empty:
        raise ValueError(
            "Nenhum dado censitário foi encontrado para "
            f"o município: {municipio}"
        )

    print(
        f"Município encontrado: "
        f"{resultado['NM_MUN'].iloc[0]}"
    )
    print(
        f"Quantidade de setores: {len(resultado)}"
    )

    return resultado


def _normalizar_texto(valor: str) -> str:
    texto = str(valor).strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    return texto.casefold()


def obter_codigo_municipio(
    municipio: str,
    caminho_csv: Path | None = None,
) -> str:
    municipio = str(municipio).strip()

    if municipio.isdigit():
        if len(municipio) != 7:
            raise ValueError(
                "O código do município deve possuir exatamente sete dígitos."
            )
        return municipio

    caminho_arquivo = (
        Path(caminho_csv)
        if caminho_csv is not None
        else localizar_csv(PASTA_BASICO)
    )
    dados_censo = carregar_dados_censo(caminho_arquivo)
    dados_municipio = filtrar_dados_municipio(dados_censo, municipio)

    codigos = (
        dados_municipio["CD_MUN"]
        .astype(str)
        .str.strip()
        .unique()
    )

    if len(codigos) > 1:
        raise ValueError(
            "O nome do município é ambíguo e corresponde a mais de um código IBGE. "
            "Informe o código IBGE ou passe o nome com a sigla do estado."
        )

    return codigos[0]
