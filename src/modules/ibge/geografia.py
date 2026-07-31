from pathlib import Path
import unicodedata

import geopandas as gpd
import pyogrio

from modules.config import PASTA_GEOGRAFIA


SUPPORTED_GEOMETRY_EXTENSIONS = {".gpkg", ".shp"}


def _listar_arquivos_geografia() -> list[Path]:
    caminhos = []
    for ext in SUPPORTED_GEOMETRY_EXTENSIONS:
        caminhos.extend(PASTA_GEOGRAFIA.glob(f"*{ext}"))
    return sorted(caminhos)


def localizar_arquivo_geografia(estado: str | None = None) -> Path:
    arquivos = _listar_arquivos_geografia()

    if not arquivos:
        raise FileNotFoundError(
            f"Nenhum arquivo geográfico foi encontrado em:\n{PASTA_GEOGRAFIA}"
        )

    if estado is None:
        if len(arquivos) == 1:
            return arquivos[0]

        preferidos = [
            arquivo
            for arquivo in arquivos
            if arquivo.name in {
                "PR_setores_CD2022.gpkg",
                "base_cartografica.gpkg",
            }
        ]

        if preferidos:
            # Prefer the sector-based PR file when both are available,
            # because most thematic maps depend on CD_SETOR.
            preferidos.sort(
                key=lambda arquivo: arquivo.name != "PR_setores_CD2022.gpkg"
            )
            return preferidos[0]

        nomes = ", ".join(arquivo.name for arquivo in arquivos)
        raise ValueError(
            "Há mais de um arquivo geográfico disponível. "
            "Informe o estado ou renomeie o arquivo que deseja usar. "
            f"Arquivos disponíveis: {nomes}"
        )

    estado = estado.strip().upper()
    for arquivo in arquivos:
        nome = arquivo.stem.upper()
        if nome.startswith(estado) or nome.endswith(estado):
            return arquivo

    disponiveis = ", ".join(arquivo.name for arquivo in arquivos)
    raise ValueError(
        f"Nenhum arquivo de geografia encontrado para o estado '{estado}'. "
        f"Arquivos disponíveis: {disponiveis}"
    )


def escolher_layer_geografia(caminho: Path) -> str:
    layers = [layer for layer, _ in pyogrio.list_layers(str(caminho))]

    if len(layers) == 1:
        return layers[0]

    preferidos = [
        "lml_municipio_a",
        "lml_area_politico_administrativa_a",
        "lml_unidade_federacao_a",
        "lml_pais_a",
    ]

    for preferido in preferidos:
        if preferido in layers:
            return preferido

    municipio = [layer for layer in layers if "municipio" in layer.lower()]
    if municipio:
        return municipio[0]

    cidade = [layer for layer in layers if "cidade" in layer.lower()]
    if cidade:
        return cidade[0]

    raise ValueError(
        "Não foi possível escolher automaticamente a camada do GeoPackage. "
        f"Camadas disponíveis: {', '.join(layers)}"
    )


def carregar_malha(caminho: Path, layer: str | None = None) -> gpd.GeoDataFrame:
    """
    Carrega um arquivo geográfico e retorna um GeoDataFrame.
    """

    caminho = caminho.resolve()

    if not caminho.is_file():
        raise FileNotFoundError(
            f"Arquivo geográfico não encontrado: {caminho}"
        )

    if layer is None:
        layer = escolher_layer_geografia(caminho)

    return gpd.read_file(str(caminho), layer=layer)


def filtrar_municipio(
    malha: gpd.GeoDataFrame,
    municipio: str,
) -> gpd.GeoDataFrame:
    """
    Filtra a malha pelo nome ou pelo código IBGE do município.
    """

    valor = str(municipio).strip()

    if valor.isdigit():
        if "CD_MUN" in malha.columns:
            coluna_codigo = "CD_MUN"
        elif "geocodigo" in malha.columns:
            coluna_codigo = "geocodigo"
        elif "codigo" in malha.columns:
            coluna_codigo = "codigo"
        else:
            raise KeyError(
                "Nenhuma coluna de código municipal foi encontrada na malha. "
                "Procure por CD_MUN, geocodigo ou codigo."
            )

        filtro = malha[coluna_codigo].astype(str).str.strip() == valor
    else:
        if "NM_MUN" in malha.columns:
            coluna_nome = "NM_MUN"
        elif "nome" in malha.columns:
            coluna_nome = "nome"
        else:
            raise KeyError(
                "Nenhuma coluna de nome municipal foi encontrada na malha. "
                "Procure por NM_MUN ou nome."
            )

        valor_normalizado = _normalizar_texto(valor)
        filtro = (
            malha[coluna_nome]
            .astype(str)
            .map(_normalizar_texto)
            == valor_normalizado
        )

    resultado = malha[filtro].copy()

    if resultado.empty:
        raise ValueError(
            f"Município não encontrado na malha: {municipio}"
        )

    # Algumas malhas oficiais representam um setor em vários polígonos.
    # Consolida essas partes para manter uma linha por CD_SETOR.
    if "CD_SETOR" in resultado.columns:
        resultado["CD_SETOR"] = (
            resultado["CD_SETOR"].astype("string").str.strip()
        )
        if resultado["CD_SETOR"].duplicated().any():
            resultado = resultado.dissolve(
                by="CD_SETOR",
                as_index=False,
                aggfunc="first",
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
