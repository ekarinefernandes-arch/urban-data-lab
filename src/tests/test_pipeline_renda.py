import pandas as pd

from modules.ibge.pipeline import construir_dataset_renda


def test_construir_dataset_renda_retorna_indicador_pronto() -> None:
    dataset = construir_dataset_renda(codigo_municipio="4115200")

    assert isinstance(dataset, pd.DataFrame)
    assert {"CD_SETOR", "renda_media_responsavel", "renda_mediana_responsavel"}.issubset(dataset.columns)
    assert not dataset.empty
    assert dataset["CD_SETOR"].dtype == "string"
