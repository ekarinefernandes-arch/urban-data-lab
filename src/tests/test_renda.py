from modules.ibge.renda import preparar_renda


CODIGO_MUNICIPIO = "4115200"


def main() -> None:
    df = preparar_renda(
        codigo_municipio=CODIGO_MUNICIPIO
    )

    print("\n" + "=" * 70)
    print("TESTE DO MÓDULO DE RENDA")
    print("=" * 70)

    print("\nPrimeiras linhas:")
    print(df.head())

    print("\nColunas:")
    print(df.columns.tolist())

    print("\nTipos:")
    print(df.dtypes)

    print("\nQuantidade de setores:")
    print(len(df))

    print("\nResumo da renda média:")
    print(df["renda_media_responsavel"].describe())

    print("\nResumo da renda mediana:")
    print(df["renda_mediana_responsavel"].describe())


if __name__ == "__main__":
    main()