import pandas as pd

from modules.config import PASTA_BASICO
from modules.ibge.censo import localizar_csv
from modules.ibge.pipeline import construir_dataset_populacao


def test_construir_dataset_populacao_retorna_indicador_pronto() -> None:
    caminho_csv = localizar_csv(PASTA_BASICO)

    dataset = construir_dataset_populacao(
        caminho_csv=caminho_csv,
        municipio="4115200",
    )

    assert isinstance(dataset, pd.DataFrame)
    assert {"CD_SETOR", "populacao"}.issubset(dataset.columns)
    assert dataset["populacao"].dtype.kind in {"i", "u", "f"}
    assert not dataset.empty
