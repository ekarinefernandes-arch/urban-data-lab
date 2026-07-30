import requests

BASE_URL = "https://servicodados.ibge.gov.br/api/v3"


def consultar(url):
    """
    Faz uma requisição GET para a API do IBGE.
    """

    resposta = requests.get(url)

    print(f"Status: {resposta.status_code}")

    return resposta