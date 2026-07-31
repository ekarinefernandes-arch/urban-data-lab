import json
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import pandas as pd
import pytest

from modules.ibge.pipeline_renda import executar_pipeline_renda


def test_pipeline_renda_salva_processados_e_relatorio() -> None:
    raiz_temporaria = Path(".test_artifacts")
    raiz_temporaria.mkdir(exist_ok=True)

    with TemporaryDirectory(dir=raiz_temporaria) as pasta_temporaria:
        tmp_path = Path(pasta_temporaria)
        bruto = tmp_path / "renda.csv"
        pd.DataFrame(
            {
                "CD_SETOR": [
                    "355100901000001",
                    "355100901000002",
                ],
                "V06004": ["R$ 1.234,56", "inválido"],
                "V06006": ["1000", "X"],
            }
        ).to_csv(bruto, sep=";", index=False, encoding="utf-8")
        malha = gpd.GeoDataFrame(
            {
                "CD_SETOR": [
                    "355100901000001",
                    "355100901000002",
                    "355100901000003",
                ]
            },
            geometry=gpd.points_from_xy([0, 1, 2], [0, 1, 2]),
            crs="EPSG:4326",
        )
        pasta = tmp_path / "processed"

        resultado = executar_pipeline_renda(
            codigo_municipio="3551009",
            malha=malha,
            arquivo_bruto=bruto,
            pasta_processados=pasta,
        )

        assert resultado.relatorio.total_linhas == 2
        assert resultado.relatorio.codigos_validos == 2
        assert resultado.relatorio.valores_ausentes == 1
        assert resultado.relatorio.valores_nao_numericos == 1
        assert resultado.relatorio.correspondencias_merge == 2
        assert resultado.relatorio.nao_correspondencias_merge == 1
        assert all(caminho.is_file() for caminho in resultado.arquivos.values())
        relatorio_salvo = json.loads(
            resultado.arquivos["qualidade"].read_text(encoding="utf-8")
        )
        assert relatorio_salvo["correspondencias_merge"] == 2

        with pytest.raises(FileExistsError):
            executar_pipeline_renda(
                codigo_municipio="3551009",
                malha=malha,
                arquivo_bruto=bruto,
                pasta_processados=pasta,
            )
