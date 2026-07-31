import pandas as pd
import pytest

from modules.ingestao.normalizers.renda import (
    normalizar_renda_ibge,
    normalizar_renda_ibge_com_qualidade,
)
from modules.ingestao.schemas import COLUNAS_ESQUEMA_INDICADORES


def test_normalizar_renda_ibge_retorna_esquema_interno_longo() -> None:
    bruto = pd.DataFrame(
        {
            "CD_SETOR": ["355100901000001", "355100901000002"],
            "V06004": ["2500.50", "X"],
            "V06006": ["1800", "2000"],
        }
    )

    resultado = normalizar_renda_ibge(bruto)

    assert tuple(resultado.columns) == COLUNAS_ESQUEMA_INDICADORES
    assert len(resultado) == 4
    assert set(resultado["indicador"]) == {
        "renda_media_responsavel",
        "renda_mediana_responsavel",
    }
    assert resultado["codigo_municipio"].eq("3551009").all()
    assert resultado["ano"].eq(2022).all()
    assert resultado["unidade"].eq("R$").all()
    assert resultado["valor"].isna().sum() == 1


def test_normalizar_renda_ibge_registra_codigo_invalido_sem_interromper() -> None:
    bruto = pd.DataFrame(
        {
            "CD_SETOR": ["3551009"],
            "V06004": ["2500"],
            "V06006": ["1800"],
        }
    )

    resultado = normalizar_renda_ibge_com_qualidade(bruto)

    assert resultado.dados.empty
    assert resultado.relatorio.total_linhas == 1
    assert resultado.relatorio.codigos_validos == 0
