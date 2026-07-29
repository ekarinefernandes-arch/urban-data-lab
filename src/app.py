import pandas as pd

from modules.ibge import consultar


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

tabela.to_csv(
    "../data/processed/populacao_maringa_2021.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo CSV salvo com sucesso!")