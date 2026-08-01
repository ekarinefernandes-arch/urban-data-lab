import sys
from pathlib import Path

PROJETO_SRC = Path(__file__).resolve().parents[1]
if str(PROJETO_SRC) not in sys.path:
    sys.path.insert(0, str(PROJETO_SRC))

from modules.config import (
    PASTA_BASICO,
    PASTA_EXPORTACOES_GPKG,
    PASTA_EXPORTACOES_MAPAS,
)
from modules.ibge.geografia import (
    carregar_malha,
    filtrar_municipio,
    localizar_arquivo_geografia,
)
from modules.ibge.pipeline import construir_dataset_populacao
from modules.visualizacao.mapas import (
    calcular_densidade_populacional,
    exportar_gpkg,
    obter_textos_padronizados,
    plotar_mapa,
    preparar_mapa_tematico,
)


BASE_DIR = Path(__file__).resolve().parent.parent


# --------------------------------------------------
# CAMINHOS DOS ARQUIVOS
# --------------------------------------------------

arquivo_malha = localizar_arquivo_geografia()
pasta_censo = PASTA_BASICO


# --------------------------------------------------
# MUNICÍPIO ESCOLHIDO
# --------------------------------------------------

municipio_informado = input(
    "Digite o nome ou o código IBGE do município: "
).strip()

if not municipio_informado:
    raise ValueError(
        "Você precisa informar um município."
    )


# --------------------------------------------------
# CARREGAMENTO DA MALHA
# --------------------------------------------------

malha = carregar_malha(
    arquivo_malha
)

malha_municipio = filtrar_municipio(
    malha,
    municipio_informado,
)

malha_municipio["CD_SETOR"] = (
    malha_municipio["CD_SETOR"]
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# CARREGAMENTO DOS DADOS DO CENSO
# --------------------------------------------------

populacao = construir_dataset_populacao(
    caminho_csv=pasta_censo / "Agregados_por_setores_basico_BR.csv",
    municipio=municipio_informado,
)


# --------------------------------------------------
# UNIÃO ENTRE DADOS E GEOMETRIA
# --------------------------------------------------

mapa = preparar_mapa_tematico(
    malha=malha_municipio,
    indicadores=populacao,
    coluna_indicador="populacao",
    chave="CD_SETOR",
)
mapa = calcular_densidade_populacional(mapa)

nome_municipio = (
    malha_municipio["NM_MUN"].iloc[0]
)


# --------------------------------------------------
# EXPORTAÇÃO PARA O QGIS
# --------------------------------------------------

pasta_exportacao = PASTA_EXPORTACOES_GPKG / "populacao"

pasta_exportacao.mkdir(
    parents=True,
    exist_ok=True,
)

nome_arquivo = (
    nome_municipio
    .lower()
    .replace(" ", "_")
    .replace("-", "_")
)

arquivo_saida = (
    pasta_exportacao
    / f"populacao_{nome_arquivo}.gpkg"
)

arquivo_saida = exportar_gpkg(
    mapa=mapa,
    pasta_exportacao=pasta_exportacao,
    nome_arquivo=f"populacao_{nome_arquivo}",
    camada="populacao_setores",
)


# --------------------------------------------------
# VERIFICAÇÃO DO RESULTADO
# --------------------------------------------------

setores_com_dados = (
    mapa["populacao"].notna().sum()
)

setores_sem_dados = (
    mapa["populacao"].isna().sum()
)

print("\nResultado da integração:")
print(f"Município: {nome_municipio}")
print(f"Setores da malha: {len(mapa)}")
print(f"Setores com população: {setores_com_dados}")
print(f"Setores sem população: {setores_sem_dados}")

print("\nResumo da população:")
print(
    mapa["populacao"].describe()
)


# --------------------------------------------------
# MAPA TEMÁTICO
# --------------------------------------------------

titulo, subtitulo, legenda = obter_textos_padronizados(
    "densidade_pop_km2",
    nome_municipio,
)

plotar_mapa(
    mapa=mapa,
    coluna="densidade_pop_km2",
    titulo=titulo,
    legenda_titulo=legenda,
    arquivo_saida=(
        PASTA_EXPORTACOES_MAPAS
        / "populacao"
        / f"populacao_{nome_arquivo}.png"
    ),
    subtitulo=subtitulo,
    tema="densidade",
)
