from pathlib import Path

from src.modules.ibge.censo import (
    carregar_dados_censo,
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

print("\nArquivo selecionado:")
print(arquivo_csv)

dados = carregar_dados_censo(
    arquivo_csv
)

print("\nQuantidade de registros:")
print(len(dados))

print("\nQuantidade de colunas:")
print(len(dados.columns))

print("\nNomes das colunas:")

for coluna in dados.columns:
    print(f"- {coluna}")

print("\nPrimeiras cinco linhas:")
print(dados.head())

print("\nTodas as colunas:")
print(dados.columns.tolist())

print("\nPrimeiras linhas:")
print(
    dados.head().to_string()
)

print("\nColunas de identificação:")

for coluna in dados.columns:
    if any(
        termo in coluna.upper()
        for termo in ["SETOR", "MUN", "UF"]
    ):
        print(coluna)


# ADICIONE DAQUI PARA BAIXO

print("\n========== PRIMEIRA LINHA ==========\n")

print(
    dados.iloc[0].to_string()
)

def filtrar_dados_municipio(
    dados: pd.DataFrame,
    municipio: str,
) -> pd.DataFrame:
    """
    Filtra os dados do Censo pelo nome ou código IBGE
    do município.
    """

    valor = str(municipio).strip()

    if valor.isdigit():
        filtro = (
            dados["CD_MUN"]
            .astype(str)
            .str.strip()
            == valor
        )
    else:
        filtro = (
            dados["NM_MUN"]
            .astype(str)
            .str.strip()
            .str.casefold()
            == valor.casefold()
        )

    resultado = dados[filtro].copy()

    if resultado.empty:
        raise ValueError(
            f"Município não encontrado nos dados do Censo: {municipio}"
        )

    return resultado
