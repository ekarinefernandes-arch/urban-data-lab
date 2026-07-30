from pathlib import Path

import matplotlib.pyplot as plt

from src.modules.ibge.geografia import carregar_malha, filtrar_municipio


BASE_DIR = Path(__file__).resolve().parent.parent

arquivo = (
    BASE_DIR
    / "data"
    / "raw"
    / "geografia"
    / "PR_setores_CD2022.gpkg"
)

malha = carregar_malha(arquivo)

municipio_informado = input(
    "Digite o nome ou o código IBGE do município: "
)

municipio = filtrar_municipio(
    malha,
    municipio_informado,
)

nome_municipio = municipio["NM_MUN"].iloc[0]
codigo_municipio = municipio["CD_MUN"].iloc[0]

print(f"\nMunicípio: {nome_municipio}")
print(f"Código IBGE: {codigo_municipio}")
print(f"Quantidade de setores: {len(municipio)}")

print("\nPrimeiros setores:")
print(
    municipio[
        ["CD_SETOR", "CD_MUN", "NM_MUN"]
    ].head()
)

municipio.plot(
    edgecolor="black",
    linewidth=0.2,
)

plt.title(
    f"Setores censitários de {nome_municipio} — Censo 2022"
)
plt.axis("off")
plt.show()