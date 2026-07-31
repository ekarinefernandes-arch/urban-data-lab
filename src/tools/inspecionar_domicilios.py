from pathlib import Path

import pandas as pd


RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DOMICILIOS = RAIZ_PROJETO / "data" / "raw" / "censo" / "domicilios"


def localizar_arquivo() -> Path:
    arquivos = sorted(PASTA_DOMICILIOS.glob("*.csv"))

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo CSV foi encontrado em:\n"
            f"{PASTA_DOMICILIOS}"
        )

    return arquivos[0]


def testar_leitura(arquivo: Path) -> tuple[pd.DataFrame, str, str]:
    tentativas = [
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ";", "encoding": "latin-1"},
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ",", "encoding": "latin-1"},
    ]

    erros = []

    for configuracao in tentativas:
        try:
            df = pd.read_csv(
                arquivo,
                sep=configuracao["sep"],
                encoding=configuracao["encoding"],
                nrows=10,
                low_memory=False,
            )

            if len(df.columns) > 1:
                return (
                    df,
                    configuracao["sep"],
                    configuracao["encoding"],
                )

        except Exception as erro:
            erros.append(str(erro))

    raise RuntimeError(
        "Não foi possível abrir o arquivo.\n"
        + "\n".join(erros)
    )


def main() -> None:
    print("\n" + "=" * 70)
    print("INSPEÇÃO DO ARQUIVO DE DOMICÍLIOS")
    print("=" * 70)

    arquivo = localizar_arquivo()

    print("\nArquivo encontrado:")
    print(arquivo)

    tamanho_mb = arquivo.stat().st_size / (1024 * 1024)
    print(f"\nTamanho do arquivo: {tamanho_mb:.2f} MB")

    df, separador, codificacao = testar_leitura(arquivo)

    print("\n" + "-" * 70)
    print("CONFIGURAÇÃO DE LEITURA")
    print("-" * 70)
    print(f"Separador: {repr(separador)}")
    print(f"Codificação: {codificacao}")

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
    print("VERIFICAÇÃO DA CHAVE")
    print("-" * 70)

    if "CD_SETOR" in df.columns:
        print("[OK] CD_SETOR")
    else:
        print("[NÃO ENCONTRADA] CD_SETOR")

    print("\n" + "=" * 70)
    print("INSPEÇÃO CONCLUÍDA")
    print("=" * 70)


if __name__ == "__main__":
    main()