from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[2]

PASTA_DADOS = RAIZ_PROJETO / "data"
PASTA_RAW = PASTA_DADOS / "raw"
PASTA_PROCESSADOS = PASTA_DADOS / "processed"
PASTA_EXPORTACOES = PASTA_DADOS / "exports"
PASTA_EXPORTACOES_GPKG = PASTA_EXPORTACOES / "geopackage"
PASTA_EXPORTACOES_MAPAS = PASTA_EXPORTACOES / "mapas"

PASTA_CENSO = PASTA_RAW / "censo"
PASTA_BASICO = PASTA_CENSO / "basico"
PASTA_RENDA = PASTA_CENSO / "renda"
PASTA_DOMICILIOS = PASTA_CENSO / "domicilios"
PASTA_ENTORNO = PASTA_CENSO / "entorno"
PASTA_DICIONARIOS = PASTA_CENSO / "dicionarios"
PASTA_PROCESSADOS_RENDA = PASTA_PROCESSADOS / "renda"

PASTA_GEOGRAFIA = PASTA_RAW / "geografia"

COLUNA_SETOR = "CD_SETOR"
COLUNA_SETOR_BASICO = "CD_SETOR"
COLUNA_SETOR_RENDA = "CD_SETOR"
COLUNA_SETOR_DOMICILIOS = "setor"
COLUNA_SETOR_ENTORNO = "CD_setor"

V_RENDA_MEDIA = "V06004"
V_RENDA_MEDIANA = "V06006"

FONTE_CENSO_2022 = "IBGE - Censo Demográfico 2022"
ANO_CENSO_2022 = 2022

INDICADORES_RENDA = {
    V_RENDA_MEDIA: {
        "indicador": "renda_media_responsavel",
        "unidade": "R$",
    },
    V_RENDA_MEDIANA: {
        "indicador": "renda_mediana_responsavel",
        "unidade": "R$",
    },
}
