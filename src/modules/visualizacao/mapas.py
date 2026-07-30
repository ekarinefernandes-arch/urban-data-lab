from pathlib import Path

import matplotlib.pyplot as plt


def exportar_gpkg(
    mapa,
    pasta_exportacao: Path,
    nome_arquivo: str,
    camada: str,
):
    """
    Exporta um GeoDataFrame para GeoPackage.
    """

    pasta_exportacao.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_saida = (
        pasta_exportacao
        / f"{nome_arquivo}.gpkg"
    )

    mapa.to_file(
        arquivo_saida,
        layer=camada,
        driver="GPKG",
    )

    print("\nArquivo exportado:")
    print(arquivo_saida)

    return arquivo_saida


def plotar_mapa(
    mapa,
    coluna,
    titulo,
    cmap="OrRd",
):
    """
    Gera um mapa temático.
    """

    fig, ax = plt.subplots(
        figsize=(10, 10)
    )

    mapa.plot(
        ax=ax,
        column=coluna,
        cmap=cmap,
        legend=True,
        edgecolor="black",
        linewidth=0.15,
        missing_kwds={
            "color": "lightgrey",
            "label": "Sem informação",
        },
    )

    ax.set_title(
        titulo,
        fontsize=16,
    )

    ax.set_axis_off()

    plt.tight_layout()

    plt.show()