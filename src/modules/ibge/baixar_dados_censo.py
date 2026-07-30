from pathlib import Path
from zipfile import BadZipFile, ZipFile

import requests


URL_DADOS_BASICOS = (
    "https://ftp.ibge.gov.br/Censos/"
    "Censo_Demografico_2022/"
    "Agregados_por_Setores_Censitarios/"
    "Agregados_por_Setor_csv/"
    "Agregados_por_setores_basico_BR_20260520.zip"
)


def baixar_arquivo(
    url: str,
    caminho_destino: Path,
) -> Path:
    """
    Baixa um arquivo da internet.

    Se o arquivo já existir, o download não será realizado
    novamente.
    """

    caminho_destino = Path(caminho_destino)

    caminho_destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if caminho_destino.exists():
        print(
            "O arquivo já existe e não será baixado novamente:"
        )
        print(caminho_destino)

        return caminho_destino

    print("Baixando os dados do Censo 2022...")

    try:
        with requests.get(
            url,
            timeout=120,
            stream=True,
        ) as resposta:

            resposta.raise_for_status()

            with caminho_destino.open("wb") as arquivo:
                for bloco in resposta.iter_content(
                    chunk_size=1024 * 1024
                ):
                    if bloco:
                        arquivo.write(bloco)

    except requests.RequestException as erro:
        if caminho_destino.exists():
            caminho_destino.unlink()

        raise ConnectionError(
            "Não foi possível baixar os dados do IBGE.\n"
            f"Erro: {erro}"
        ) from erro

    print("Download concluído:")
    print(caminho_destino)

    return caminho_destino


def extrair_arquivo_zip(
    caminho_zip: Path,
    pasta_destino: Path,
) -> Path:
    """
    Extrai o conteúdo de um arquivo ZIP.

    Se a pasta de destino já possuir arquivos CSV,
    a extração não será repetida.
    """

    caminho_zip = Path(caminho_zip)
    pasta_destino = Path(pasta_destino)

    if not caminho_zip.exists():
        raise FileNotFoundError(
            f"O arquivo ZIP não foi encontrado:\n{caminho_zip}"
        )

    pasta_destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivos_csv = list(
        pasta_destino.rglob("*.csv")
    )

    if arquivos_csv:
        print(
            "Os dados já foram extraídos:"
        )
        print(pasta_destino)

        return pasta_destino

    print("Extraindo os dados do Censo 2022...")

    try:
        with ZipFile(caminho_zip, "r") as arquivo_zip:
            arquivo_zip.extractall(pasta_destino)

    except BadZipFile as erro:
        raise ValueError(
            f"O arquivo não é um ZIP válido:\n{caminho_zip}"
        ) from erro

    print("Extração concluída:")
    print(pasta_destino)

    return pasta_destino


def preparar_dados_censo(
    pasta_censo: Path,
) -> Path:
    """
    Baixa e extrai os dados básicos do Censo 2022.

    Retorna o caminho da pasta onde os arquivos foram
    extraídos.
    """

    pasta_censo = Path(pasta_censo)

    caminho_zip = (
        pasta_censo
        / "Agregados_por_setores_basico_BR_20260520.zip"
    )

    pasta_extraida = (
        pasta_censo
        / "basico"
    )

    baixar_arquivo(
        url=URL_DADOS_BASICOS,
        caminho_destino=caminho_zip,
    )

    extrair_arquivo_zip(
        caminho_zip=caminho_zip,
        pasta_destino=pasta_extraida,
    )

    return pasta_extraida


if __name__ == "__main__":
    base_dir = (
        Path(__file__)
        .resolve()
        .parents[3]
    )

    pasta_censo = (
        base_dir
        / "data"
        / "raw"
        / "censo"
    )

    preparar_dados_censo(
        pasta_censo=pasta_censo,
    )