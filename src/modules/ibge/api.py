import requests
import pandas as pd

BASE_URL = "https://servicodados.ibge.gov.br/api/v3"
API_TIMEOUT = 30


def consultar(url: str, params: dict[str, str] | None = None) -> requests.Response:
    """
    Faz uma requisição GET para a API do IBGE.
    """

    resposta = requests.get(url, params=params, timeout=API_TIMEOUT)
    resposta.raise_for_status()

    print(f"URL: {resposta.url}")
    print(f"Status: {resposta.status_code}")

    return resposta


def buscar_agregados_por_nivel(nivel: str) -> list[dict]:
    """
    Lista agregados disponíveis para um determinado nível geográfico.
    """

    url = f"{BASE_URL}/agregados"
    params = {"nivel": nivel}
    return consultar(url, params=params).json()


def buscar_metadados_agregado(agregado: str | int) -> dict:
    """
    Busca metadados do agregado IBGE informado.
    """

    url = f"{BASE_URL}/agregados/{agregado}/metadados"
    return consultar(url).json()


def buscar_localidades_agregado(agregado: str | int, nivel: str) -> list[dict]:
    """
    Busca localidades associadas a um agregado em um determinado nível geográfico.
    """

    url = f"{BASE_URL}/agregados/{agregado}/localidades/{nivel}"
    return consultar(url).json()


def buscar_variaveis_agregado(
    agregado: str | int,
    variavel: str = "all",
    periodos: str = "-1",
    localidades: str = "BR",
    view: str = "flat",
    classificacao: str | None = None,
) -> list[dict]:
    """
    Busca resultados da API de variáveis do IBGE para um agregado.
    """

    url = f"{BASE_URL}/agregados/{agregado}/periodos/{periodos}/variaveis/{variavel}"
    params: dict[str, str] = {"localidades": localidades}

    if view:
        params["view"] = view
    if classificacao:
        params["classificacao"] = classificacao

    return consultar(url, params=params).json()


def resultados_para_dataframe(
    resultados: list[dict],
    agregado: str | int,
) -> pd.DataFrame:
    """
    Normaliza o retorno da API de variáveis em um DataFrame.
    """

    linhas: list[dict] = []

    for variavel_obj in resultados:
        variavel_id = variavel_obj.get("id")
        nome_variavel = variavel_obj.get("variavel")
        unidade = variavel_obj.get("unidade")

        for resultado in variavel_obj.get("resultados", []):
            for serie in resultado.get("series", []):
                localidade = serie.get("localidade", {})
                localidade_id = localidade.get("id")
                localidade_nome = localidade.get("nome")
                periodo_series = serie.get("serie", {})

                for periodo, valor in periodo_series.items():
                    linhas.append(
                        {
                            "agregado": str(agregado),
                            "variavel_id": variavel_id,
                            "variavel": nome_variavel,
                            "unidade": unidade,
                            "localidade_id": localidade_id,
                            "localidade_nome": localidade_nome,
                            "periodo": periodo,
                            "valor": valor,
                        }
                    )

    return pd.DataFrame(linhas)