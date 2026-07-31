from modules.ibge.censo import (
    carregar_dados_censo,
    filtrar_dados_municipio,
    localizar_csv,
)
from modules.ibge.constantes import PASTA_BASICO


CODIGO_MUNICIPIO = "4115200"


def test_carregar_dados_municipio() -> None:
    """
    Verifica se os dados básicos do Censo podem ser carregados
    e filtrados para o município informado.
    """

    arquivo_csv = localizar_csv(PASTA_BASICO)

    dados = carregar_dados_censo(arquivo_csv)

    dados_municipio = filtrar_dados_municipio(
        dados=dados,
        municipio=CODIGO_MUNICIPIO,
    )

    assert not dados_municipio.empty
    assert "CD_MUN" in dados_municipio.columns
    assert "NM_MUN" in dados_municipio.columns

    assert (
        dados_municipio["CD_MUN"]
        .astype(str)
        .str.strip()
        .eq(CODIGO_MUNICIPIO)
        .all()
    )