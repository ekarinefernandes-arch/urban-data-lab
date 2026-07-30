import pandas as pd
from pathlib import Path

from src.modules.ibge.api import consultar

BASE_DIR = Path(__file__).resolve().parent.parent


url = (
    "https://servicodados.ibge.gov.br/api/v3/agregados/"
    "6579/periodos/2021/variaveis/9324?"
    "localidades=N6[4115200]"
)

resposta = consultar(url)
dados = resposta.json()

variavel = dados[0]["variavel"]
unidade = dados[0]["unidade"]

serie = dados[0]["resultados"][0]["series"][0]

municipio = serie["localidade"]["nome"]
ano, valor = next(iter(serie["serie"].items()))

tabela = pd.DataFrame(
    [
        {
            "municipio": municipio,
            "ano": int(ano),
            "indicador": variavel,
            "unidade": unidade,
            "valor": int(valor),
        }
    ]
)

print(tabela)

arquivo_saida = (
    BASE_DIR
    / "data"
    / "processed"
    / "populacao_maringa_2021.csv"
)

tabela.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo CSV salvo com sucesso!")