from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from modules.config import PASTA_EXPORTACOES_GPKG, PASTA_EXPORTACOES_MAPAS, RAIZ_PROJETO
from modules.ibge.censo import carregar_dados_censo, localizar_csv, obter_codigo_municipio
from modules.ibge.geografia import carregar_malha, filtrar_municipio, localizar_arquivo_geografia
from modules.ibge.pipeline import construir_dataset_populacao, construir_dataset_renda
from modules.visualizacao.mapas import (
    adicionar_classes_mapa,
    exportar_gpkg,
    obter_textos_padronizados,
    plotar_mapa,
    preparar_mapa_tematico,
)

SIGLAS_UF_POR_CODIGO = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA",
    "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
    "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE",
    "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT",
    "52": "GO", "53": "DF",
}

NOMES_UF_POR_SIGLA = {
    "RO": "Rondônia", "AC": "Acre", "AM": "Amazonas", "RR": "Roraima",
    "PA": "Pará", "AP": "Amapá", "TO": "Tocantins", "MA": "Maranhão",
    "PI": "Piauí", "CE": "Ceará", "RN": "Rio Grande do Norte",
    "PB": "Paraíba", "PE": "Pernambuco", "AL": "Alagoas", "SE": "Sergipe",
    "BA": "Bahia", "MG": "Minas Gerais", "ES": "Espírito Santo",
    "RJ": "Rio de Janeiro", "SP": "São Paulo", "PR": "Paraná",
    "SC": "Santa Catarina", "RS": "Rio Grande do Sul",
    "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "GO": "Goiás",
    "DF": "Distrito Federal",
}


def _normalizar_texto(valor: str) -> str:
    return str(valor).strip().upper()


def _resolver_sigla_uf(uf: str) -> str | None:
    valor = _normalizar_texto(uf)
    if not valor:
        return None
    if valor.isdigit() and len(valor) == 2:
        return SIGLAS_UF_POR_CODIGO.get(valor)
    for sigla, nome in NOMES_UF_POR_SIGLA.items():
        if valor in {sigla, _normalizar_texto(nome)}:
            return sigla
    return None


@lru_cache(maxsize=4)
def _carregar_base_censo_cache(caminho_csv: str) -> pd.DataFrame:
    return carregar_dados_censo(Path(caminho_csv))


def carregar_base_censo(caminho_csv: Path | None = None) -> pd.DataFrame:
    """Carrega e reutiliza a base do Censo durante a sessão do painel."""
    caminho = caminho_csv or localizar_csv(
        RAIZ_PROJETO / "data" / "raw" / "censo" / "basico"
    )
    return _carregar_base_censo_cache(str(Path(caminho).resolve()))


def listar_ufs(caminho_csv: Path | None = None) -> list[tuple[str, str]]:
    """Retorna as UFs disponíveis como pares (sigla, nome)."""
    dados = carregar_base_censo(caminho_csv)
    if "CD_UF" not in dados.columns or "NM_UF" not in dados.columns:
        return []

    ufs = dados[["CD_UF", "NM_UF"]].drop_duplicates().copy()
    ufs["CD_UF"] = ufs["CD_UF"].astype(str).str.strip()
    ufs["NM_UF"] = ufs["NM_UF"].astype(str).str.strip()
    itens = [
        (SIGLAS_UF_POR_CODIGO[codigo], str(nome))
        for codigo, nome in ufs.itertuples(index=False)
        if codigo in SIGLAS_UF_POR_CODIGO
    ]
    return sorted(itens, key=lambda item: item[1])


def listar_municipios_por_uf(
    uf: str, caminho_csv: Path | None = None
) -> list[tuple[str, str]]:
    """Retorna os municípios de uma UF como pares (código, nome)."""
    dados = carregar_base_censo(caminho_csv)
    obrigatorias = {"CD_UF", "CD_MUN", "NM_MUN"}
    ausentes = obrigatorias - set(dados.columns)
    if ausentes:
        raise KeyError(f"Colunas ausentes na base do Censo: {sorted(ausentes)}")

    sigla = _resolver_sigla_uf(uf)
    if sigla is None:
        raise ValueError(f"UF inválida: {uf}")
    codigo_uf = next(codigo for codigo, item in SIGLAS_UF_POR_CODIGO.items() if item == sigla)
    municipios = (
        dados.loc[
            dados["CD_UF"].astype(str).str.strip() == codigo_uf,
            ["CD_MUN", "NM_MUN"],
        ]
        .drop_duplicates()
        .copy()
    )
    municipios["NM_MUN"] = municipios["NM_MUN"].astype(str).str.strip()
    municipios = municipios.sort_values("NM_MUN", kind="stable")
    return [
        (str(codigo).strip(), str(nome))
        for codigo, nome in municipios.itertuples(index=False)
    ]


def gerar_painel_ibge(
    uf: str,
    municipio: str,
    tipo: str,
    variavel: str | None = None,
) -> tuple[pd.DataFrame, Path, Path, str]:
    """Gera tabela, mapa e arquivos de exportação para o painel."""
    codigo_municipio = str(obter_codigo_municipio(municipio)).strip()

    if tipo == "populacao":
        dataset = construir_dataset_populacao(municipio=codigo_municipio)
        coluna, legenda, tema = "populacao", "População", "populacao"
    elif tipo == "renda":
        dataset = construir_dataset_renda(codigo_municipio=codigo_municipio)
        coluna, legenda, tema = variavel or "renda_media_responsavel", "Renda", "renda"
    else:
        raise ValueError(f"Tipo de dado não suportado: {tipo}")

    malha = carregar_malha(localizar_arquivo_geografia(estado=uf))
    malha_municipio = filtrar_municipio(malha, codigo_municipio)
    nome_municipio = (
        str(malha_municipio["NM_MUN"].iloc[0])
        if "NM_MUN" in malha_municipio.columns
        else codigo_municipio
    )
    titulo, subtitulo, legenda = obter_textos_padronizados(
        coluna,
        nome_municipio,
    )
    mapa = preparar_mapa_tematico(
        malha=malha_municipio,
        indicadores=dataset,
        coluna_indicador=coluna,
        chave="CD_SETOR",
    )
    mapa = adicionar_classes_mapa(
        mapa=mapa,
        coluna=coluna,
        legenda_titulo=legenda,
    )

    tabela_simplificada = mapa[
        ["CD_SETOR", "NM_MUN", coluna, "faixa_mapa"]
    ].copy()

    tabela_simplificada = tabela_simplificada.rename(
        columns={
            "CD_SETOR": "setor_censitario",
            "NM_MUN": "municipio",
            coluna: "valor",
            "faixa_mapa": "faixa_do_mapa",
        }
    )
    nome_arquivo = f"{tipo}_{codigo_municipio}_{coluna}"
    pasta_gpkg = PASTA_EXPORTACOES_GPKG / tipo
    caminho_gpkg = exportar_gpkg(
        mapa=mapa,
        pasta_exportacao=pasta_gpkg,
        nome_arquivo=nome_arquivo,
        camada=f"{tipo}_{coluna}",
    )
    caminho_png = PASTA_EXPORTACOES_MAPAS / tipo / f"{nome_arquivo}.png"
    plotar_mapa(
        mapa,
        coluna,
        titulo,
        legenda_titulo=legenda,
        arquivo_saida=caminho_png,
        subtitulo=subtitulo,
        tema=tema,
    )
    return tabela_simplificada, caminho_gpkg, caminho_png, coluna
