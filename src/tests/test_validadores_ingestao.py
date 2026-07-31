import pandas as pd
import pytest

from modules.ingestao.validators.territorial import normalizar_codigo_territorial


def test_normalizar_codigo_territorial_preserva_string() -> None:
    resultado = normalizar_codigo_territorial(
        pd.Series([" 355100901000001 "]),
        tamanho=15,
        nome="codigo_setor",
    )

    assert resultado.dtype == "string"
    assert resultado.iloc[0] == "355100901000001"


def test_normalizar_codigo_territorial_modo_tolerante() -> None:
    resultado = normalizar_codigo_territorial(
        pd.Series(["inválido", "355100901000001"]),
        tamanho=15,
        nome="codigo_setor",
        erros="coerce",
    )

    assert pd.isna(resultado.iloc[0])
    assert resultado.iloc[1] == "355100901000001"


def test_normalizar_codigo_territorial_modo_estrito() -> None:
    with pytest.raises(ValueError, match="15 dígitos"):
        normalizar_codigo_territorial(
            pd.Series(["inválido"]),
            tamanho=15,
            nome="codigo_setor",
        )
