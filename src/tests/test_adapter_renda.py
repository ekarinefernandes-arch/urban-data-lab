import pandas as pd

from modules.datasets.adapters import renda_para_formato_mapa
from modules.ingestao.normalizers.renda import normalizar_renda_ibge


def test_renda_para_formato_mapa_preserva_contrato_legado() -> None:
    bruto = pd.DataFrame(
        {
            "CD_SETOR": ["355100901000001"],
            "V06004": ["2500"],
            "V06006": ["1800"],
        }
    )

    resultado = renda_para_formato_mapa(normalizar_renda_ibge(bruto))

    assert resultado.columns.tolist() == [
        "CD_SETOR",
        "renda_media_responsavel",
        "renda_mediana_responsavel",
    ]
    assert resultado.loc[0, "CD_SETOR"] == "355100901000001"
    assert resultado.loc[0, "renda_media_responsavel"] == 2500
    assert resultado.loc[0, "renda_mediana_responsavel"] == 1800
