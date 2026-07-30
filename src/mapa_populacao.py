from pathlib import Path


from modules.ibge.censo import (
    carregar_dados_censo,
    filtrar_dados_municipio,
    localizar_csv,
)
from src.modules.visualizacao.mapas import (
    exportar_gpkg,
    plotar_mapa,
)
from modules.ibge.geografia import (
    carregar_malha,
    filtrar_municipio,
)
from modules.ibge.indicadores import preparar_populacao



BASE_DIR = Path(__file__).resolve().parent.parent


# --------------------------------------------------
# CAMINHOS DOS ARQUIVOS
# --------------------------------------------------

arquivo_malha = (
    BASE_DIR
    / "data"
    / "raw"
    / "geografia"
    / "PR_setores_CD2022.gpkg"
)

pasta_censo = (
    BASE_DIR
    / "data"
    / "raw"
    / "censo"
    / "basico"
)


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

arquivo_csv = localizar_csv(
    pasta_censo
)

dados_censo = carregar_dados_censo(
    arquivo_csv
)

dados_municipio = filtrar_dados_municipio(
    dados_censo,
    municipio_informado,
)

populacao = preparar_populacao(
    dados_municipio
)


# --------------------------------------------------
# UNIÃO ENTRE DADOS E GEOMETRIA
# --------------------------------------------------

mapa = malha_municipio.merge(
    populacao,
    on="CD_SETOR",
    how="left",
)

nome_municipio = (
    malha_municipio["NM_MUN"].iloc[0]
)


# --------------------------------------------------
# EXPORTAÇÃO PARA O QGIS
# --------------------------------------------------

pasta_exportacao = (
    BASE_DIR
    / "data"
    / "exports"
    / "geopackage"
)

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

plotar_mapa(
    mapa=mapa,
    coluna="populacao",
    titulo=(
        f"População por setor censitário — {nome_municipio}\n"
        "Censo Demográfico 2022"
    ),
)
