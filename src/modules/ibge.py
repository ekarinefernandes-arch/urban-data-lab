import requests


def consultar_ibge(url):
    """
    Faz uma consulta à API do IBGE e retorna os dados em formato JSON.
    """

    resposta = requests.get(url)

    if resposta.status_code == 200:
        return resposta.json()

    raise Exception(f"Erro {resposta.status_code} ao consultar a API.")