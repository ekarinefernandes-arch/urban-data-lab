from pathlib import Path

from src.modules.ibge.censo import (
    carregar_dados_censo,
    filtrar_dados_municipio,
    localizar_csv,
)


BASE_DIR = Path(__file__).resolve().parent.parent

pasta_dados = (
    BASE_DIR
    / "data"
    / "raw"
    / "censo"
    / "basico"
)

arquivo_csv = localizar_csv(
    pasta_dados
)

dados = carregar_dados_censo(
    arquivo_csv
)

municipio_informado = input(
    "Digite o nome ou o código IBGE do município: "
).strip()

if not municipio_informado:
    raise ValueError(
        "Você precisa informar um município."
    )

dados_municipio = filtrar_dados_municipio(
    dados,
    municipio_informado,
)

nome_municipio = dados_municipio["NM_MUN"].iloc[0]
codigo_municipio = dados_municipio["CD_MUN"].iloc[0]

print("\nMunicípio encontrado:")
print(f"Nome: {nome_municipio}")
print(f"Código IBGE: {codigo_municipio}")
print(f"Quantidade de setores: {len(dados_municipio)}")

print("\nPrimeiros setores e variáveis:")

print(
    dados_municipio[
        [
            "CD_SETOR",
            "NM_MUN",
            "v0001",
            "v0002",
            "v0003",
            "v0004",
            "v0005",
            "v0006",
            "v0007",
            "v0008",
            "v0009",
        ]
    ]
    .head()
    .to_string(index=False)
)