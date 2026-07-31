import pandas as pd

from modules.ingestao.normalizers.valores import converter_moeda_brasileira


def test_converter_moeda_brasileira_trata_formatos_e_invalidos() -> None:
    valores = pd.Series(
        ["R$ 1.234,56", "2500.50", "1234,00", "X", "", "inválido"]
    )

    numericos, ausentes, invalidos = converter_moeda_brasileira(valores)

    assert numericos.iloc[:3].tolist() == [1234.56, 2500.50, 1234.00]
    assert int(ausentes.sum()) == 2
    assert int(invalidos.sum()) == 1
    assert pd.isna(numericos.iloc[5])
