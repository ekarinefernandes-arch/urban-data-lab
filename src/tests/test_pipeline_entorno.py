import pandas as pd

from modules.ibge.pipeline import construir_dataset_entorno


def test_construir_dataset_entorno_retorna_indicador_pronto() -> None:
    dataset = construir_dataset_entorno(
        codigo_municipio="4115200",
        variaveis=["V05200", "V05201"],
    )

    assert isinstance(dataset, pd.DataFrame)
    assert {"CD_SETOR", "V05200", "V05201"}.issubset(dataset.columns)
    assert not dataset.empty
    assert dataset["CD_SETOR"].dtype == "string"
