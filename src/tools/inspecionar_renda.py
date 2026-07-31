from pathlib import Path

import pandas as pd


# Caminho da raiz do projeto
RAIZ_PROJETO = Path(__file__).resolve().parent.parent

# Caminho completo do arquivo de renda
ARQUIVO_RENDA = (
    RAIZ_PROJETO
    / "data"
    / "raw"
    / "censo"
    / "renda"
    / "agregados_por_setores_renda_responsavel_BR.csv"
)


def testar_leitura(arquivo: Path) -> tuple[pd.DataFrame, str, str]:
    """
    Testa diferentes separadores e codificações até conseguir
    abrir corretamente o arquivo CSV.
    """

    tentativas = [
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ";", "encoding": "latin-1"},
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ",", "encoding": "latin-1"},
    ]

    erros = []

    for configuracao in tentativas:
        separador = configuracao["sep"]
        codificacao = configuracao["encoding"]

        try:
            df = pd.read_csv(
                arquivo,
                sep=separador,
                encoding=codificacao,
                nrows=10,
                low_memory=False,
            )

            # Se o arquivo tiver mais de uma coluna,
            # provavelmente o separador está correto.
            if len(df.columns) > 1:
                return df, separador, codificacao

        except Exception as erro:
            erros.append(
                f"Separador: {separador} | "
                f"Codificação: {codificacao} | "
                f"Erro: {type(erro).__name__}: {erro}"
            )

    mensagem_erros = "\n".join(erros)

    raise RuntimeError(
        "Não foi possível abrir o arquivo de renda.\n\n"
        f"Tentativas realizadas:\n{mensagem_erros}"
    )


def main() -> None:
    """
    Inspeciona o arquivo de renda do Censo 2022.
    """

    print("\n" + "=" * 70)
    print("INSPEÇÃO DO ARQUIVO DE RENDA")
    print("=" * 70)

    # Verifica se o arquivo existe
    if not ARQUIVO_RENDA.exists():
        raise FileNotFoundError(
            "\nO arquivo de renda não foi encontrado.\n\n"
            f"Caminho esperado:\n{ARQUIVO_RENDA}\n\n"
            "Confira se o nome do arquivo está correto e se ele está dentro de:\n"
            "data/raw/censo/renda/"
        )

    print("\nArquivo encontrado:")
    print(ARQUIVO_RENDA)

    tamanho_mb = ARQUIVO_RENDA.stat().st_size / (1024 * 1024)

    print(f"\nTamanho do arquivo: {tamanho_mb:.2f} MB")

    # Testa a leitura do arquivo
    df, separador, codificacao = testar_leitura(ARQUIVO_RENDA)

    print("\n" + "-" * 70)
    print("CONFIGURAÇÃO DE LEITURA")
    print("-" * 70)

    print(f"Separador identificado: {repr(separador)}")
    print(f"Codificação identificada: {codificacao}")

    print("\n" + "-" * 70)
    print("COLUNAS ENCONTRADAS")
    print("-" * 70)

    for numero, coluna in enumerate(df.columns, start=1):
        print(f"{numero}. {coluna}")

    print("\n" + "-" * 70)
    print("PRIMEIRAS LINHAS")
    print("-" * 70)

    print(df.head())

    print("\n" + "-" * 70)
    print("TIPOS DAS COLUNAS")
    print("-" * 70)

    print(df.dtypes)

    print("\n" + "-" * 70)
    print("VERIFICAÇÃO DAS VARIÁVEIS IMPORTANTES")
    print("-" * 70)

    variaveis_importantes = [
        "CD_SETOR",
        "CD_SETOR_CENSITARIO",
        "V06004",
        "V06006",
    ]

    for variavel in variaveis_importantes:
        if variavel in df.columns:
            print(f"[OK] {variavel}")
        else:
            print(f"[NÃO ENCONTRADA] {variavel}")

    print("\n" + "-" * 70)
    print("VALORES DAS VARIÁVEIS DE RENDA")
    print("-" * 70)

    for variavel in ["V06004", "V06006"]:
        if variavel in df.columns:
            print(f"\nVariável: {variavel}")
            print(df[variavel].head(10))

    print("\n" + "=" * 70)
    print("INSPEÇÃO CONCLUÍDA")
    print("=" * 70)


if __name__ == "__main__":
    main()