from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import pandas as pd

from modules.config import ANO_CENSO_2022, PASTA_PROCESSADOS_RENDA
from modules.datasets.adapters import renda_para_formato_mapa
from modules.datasets.repository import salvar_resultados_renda
from modules.ibge.integracao import integrar_dados_geometria
from modules.ibge.renda import ler_renda_bruta
from modules.ingestao.normalizers.renda import normalizar_renda_ibge_com_qualidade
from modules.ingestao.quality import RelatorioQualidade
from modules.ingestao.validators.territorial import normalizar_codigo_territorial


@dataclass
class ResultadoPipelineRenda:
    """Produtos em memória e caminhos gerados pelo pipeline de renda."""

    dados_padronizados: pd.DataFrame
    dados_mapa: pd.DataFrame
    mapa: gpd.GeoDataFrame
    relatorio: RelatorioQualidade
    valores_invalidos: pd.DataFrame
    arquivos: dict[str, Path]


def executar_pipeline_renda(
    codigo_municipio: str,
    malha: gpd.GeoDataFrame,
    *,
    arquivo_bruto: Path | None = None,
    pasta_processados: Path = PASTA_PROCESSADOS_RENDA,
    sobrescrever: bool = False,
) -> ResultadoPipelineRenda:
    """Executa ingestão, qualidade, persistência e junção geográfica da renda."""
    codigo = str(codigo_municipio).strip()
    if len(codigo) != 7 or not codigo.isdigit():
        raise ValueError("codigo_municipio deve possuir sete dígitos.")
    if "CD_SETOR" not in malha.columns:
        raise KeyError("A malha deve possuir a coluna 'CD_SETOR'.")

    bruto = ler_renda_bruta(arquivo=arquivo_bruto)
    codigos_brutos = normalizar_codigo_territorial(
        bruto["CD_SETOR"],
        tamanho=15,
        nome="CD_SETOR da renda",
        erros="coerce",
    )
    bruto_municipal = bruto.loc[
        codigos_brutos.str.startswith(codigo, na=False)
    ].copy()
    normalizacao = normalizar_renda_ibge_com_qualidade(bruto_municipal)
    dados_municipais = normalizacao.dados
    dados_mapa = renda_para_formato_mapa(dados_municipais)

    malha_normalizada = malha.copy()
    malha_normalizada["CD_SETOR"] = normalizar_codigo_territorial(
        malha_normalizada["CD_SETOR"],
        tamanho=15,
        nome="CD_SETOR da malha",
        erros="coerce",
    )
    chaves_dados = set(dados_mapa["CD_SETOR"].dropna())
    correspondencias = int(malha_normalizada["CD_SETOR"].isin(chaves_dados).sum())
    nao_correspondencias = int(len(malha_normalizada) - correspondencias)
    normalizacao.relatorio.correspondencias_merge = correspondencias
    normalizacao.relatorio.nao_correspondencias_merge = nao_correspondencias

    mapa = integrar_dados_geometria(
        malha=malha_normalizada,
        indicadores=dados_mapa,
        chave="CD_SETOR",
    )
    identificador = f"{ANO_CENSO_2022}_{codigo}"
    arquivos = salvar_resultados_renda(
        dados=dados_municipais,
        valores_invalidos=normalizacao.valores_invalidos,
        relatorio=normalizacao.relatorio,
        pasta=pasta_processados,
        identificador=identificador,
        sobrescrever=sobrescrever,
    )
    return ResultadoPipelineRenda(
        dados_padronizados=dados_municipais,
        dados_mapa=dados_mapa,
        mapa=mapa,
        relatorio=normalizacao.relatorio,
        valores_invalidos=normalizacao.valores_invalidos,
        arquivos=arquivos,
    )
