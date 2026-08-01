from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter

from modules.ibge.integracao import integrar_dados_geometria
from modules.visualizacao.estilos import EstiloMapa, obter_estilo_mapa


def preparar_mapa_tematico(
    malha: gpd.GeoDataFrame,
    indicadores: pd.DataFrame,
    coluna_indicador: str,
    chave: str = "CD_SETOR",
) -> gpd.GeoDataFrame:
    """
    Prepara um GeoDataFrame temático a partir de uma malha e indicadores.
    """

    mapa = integrar_dados_geometria(
        malha=malha,
        indicadores=indicadores,
        chave=chave,
    )

    if coluna_indicador not in mapa.columns:
        raise KeyError(
            f"A coluna '{coluna_indicador}' não foi encontrada no mapa preparado."
        )

    return mapa


def calcular_densidade_populacional(
    mapa: gpd.GeoDataFrame,
    coluna_populacao: str = "populacao",
    coluna_saida: str = "densidade_pop_km2",
) -> gpd.GeoDataFrame:
    """Calcula habitantes por km² usando uma projeção métrica local."""
    if mapa.crs is None:
        raise ValueError("A malha precisa ter um CRS para calcular a área.")
    if coluna_populacao not in mapa.columns:
        raise KeyError(f"A coluna '{coluna_populacao}' não foi encontrada.")

    resultado = mapa.copy()
    crs_metrico = resultado.estimate_utm_crs()
    if crs_metrico is None:
        raise ValueError("Não foi possível determinar uma projeção métrica.")

    area_km2 = resultado.to_crs(crs_metrico).geometry.area / 1_000_000
    populacao = pd.to_numeric(resultado[coluna_populacao], errors="coerce")
    resultado[coluna_saida] = populacao.div(area_km2.where(area_km2 > 0))
    return resultado


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


def _formatar_moeda(valor, pos):
    if pd.isna(valor):
        return ""
    try:
        valor_float = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    inteiro = int(round(valor_float, 0))
    texto = f"R$ {inteiro:,}".replace(",", ".")
    return texto


def _formatar_numero(valor, pos):
    if pd.isna(valor):
        return ""
    try:
        valor_float = float(valor)
    except (TypeError, ValueError):
        return str(valor)
    if valor_float.is_integer():
        return f"{int(valor_float):,}".replace(",", ".")
    return f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _is_currency_column(coluna: str, legenda_titulo: str) -> bool:
    coluna_texto = str(coluna).lower()
    titulo_texto = str(legenda_titulo).lower()
    return "renda" in coluna_texto or "renda" in titulo_texto or "r$" in titulo_texto


ROTULOS_INDICADORES = {
    "populacao": ("População", "População (habitantes)"),
    "densidade_pop_km2": (
        "Densidade populacional",
        "Densidade populacional (hab./km²)",
    ),
    "renda_media_responsavel": (
        "Renda média do responsável",
        "Renda média do responsável (R$)",
    ),
    "renda_mediana_responsavel": (
        "Renda mediana do responsável",
        "Renda mediana do responsável (R$)",
    ),
}


def obter_textos_padronizados(
    coluna: str,
    municipio: str,
) -> tuple[str, str, str]:
    """Monta título, subtítulo e legenda no padrão cartográfico do projeto."""
    nome_padrao = str(coluna).replace("_", " ").title()
    nome_indicador, legenda = ROTULOS_INDICADORES.get(
        coluna,
        (nome_padrao, nome_padrao),
    )
    titulo = f"{nome_indicador} por setor censitário — {municipio}"
    subtitulo = "Censo Demográfico 2022 • classificação por quantis (5 classes)"
    return titulo, subtitulo, legenda


def _plotar_mapa_legado(
    mapa,
    coluna,
    titulo,
    cmap="OrRd",
    legenda_titulo="Legenda",
    usar_quantis=True,
    arquivo_saida: Path | None = None,
):
    """
    Gera um mapa temático.
    """

    fig, ax = plt.subplots(
        figsize=(10, 10)
    )

    dados_plot = mapa.copy()
    coluna_plot = coluna
    valores = pd.to_numeric(dados_plot[coluna], errors="coerce")
    currency = _is_currency_column(coluna, legenda_titulo)

    categorical = False
    if usar_quantis and not currency and valores.nunique(dropna=True) > 1:
        coluna_plot = f"_{coluna}_classes"
        dados_plot[coluna_plot] = pd.qcut(
            valores,
            q=min(5, valores.nunique(dropna=True)),
            duplicates="drop",
        )
        categorical = True

    formatter = FuncFormatter(
        _formatar_moeda if currency else _formatar_numero
    )

    legend_kwds = (
        {"title": legenda_titulo}
        if categorical
        else {
            "label": legenda_titulo,
            "orientation": "vertical",
            "format": formatter,
        }
    )

    dados_plot.plot(
        ax=ax,
        column=coluna_plot,
        cmap=cmap,
        categorical=categorical,
        legend=True,
        edgecolor="black",
        linewidth=0.15,
        missing_kwds={
            "color": "lightgrey",
            "label": "Sem informação",
        },
        legend_kwds=legend_kwds,
    )

    ax.set_title(
        titulo,
        fontsize=16,
    )

    ax.set_axis_off()

    plt.tight_layout()

    if arquivo_saida is not None:
        arquivo_saida = Path(arquivo_saida)
        arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(arquivo_saida, dpi=200, bbox_inches="tight")
        print(f"Visualização exportada:\n{arquivo_saida}")

    if arquivo_saida is None:
        plt.show()
    plt.close(fig)


def plotar_mapa(
    mapa,
    coluna,
    titulo,
    cmap=None,
    legenda_titulo="Legenda",
    usar_quantis=True,
    arquivo_saida: Path | None = None,
    subtitulo: str | None = None,
    fonte: str = "Fonte: IBGE, Censo Demográfico 2022.",
    nota: str | None = None,
    tema: str | None = None,
    estilo: EstiloMapa | None = None,
):
    """Gera um mapa temático diagramado e pronto para apresentação."""
    if coluna not in mapa.columns:
        raise KeyError(f"A coluna '{coluna}' não foi encontrada no mapa.")

    estilo = estilo or obter_estilo_mapa(tema)
    cmap = cmap or estilo.cmap
    dados_plot = mapa.copy()
    if dados_plot.crs is not None and dados_plot.crs.is_geographic:
        crs_local = dados_plot.estimate_utm_crs()
        if crs_local is not None:
            dados_plot = dados_plot.to_crs(crs_local)

    valores = pd.to_numeric(dados_plot[coluna], errors="coerce")
    dados_plot[coluna] = valores
    currency = _is_currency_column(coluna, legenda_titulo)
    fig, ax = plt.subplots(figsize=estilo.figsize, facecolor=estilo.cor_fundo)
    ax.set_facecolor(estilo.cor_fundo)
    legendas = []

    if usar_quantis and valores.nunique(dropna=True) > 1:
        classificados = adicionar_classes_mapa(
            dados_plot,
            coluna,
            numero_classes=estilo.numero_classes,
            legenda_titulo=legenda_titulo,
        )
        dados_plot["_classe_mapa"] = classificados["classe_mapa"]
        dados_plot["_faixa_mapa"] = classificados["faixa_mapa"]
        faixas = (
            dados_plot[["_classe_mapa", "_faixa_mapa"]]
            .dropna()
            .drop_duplicates()
            .sort_values("_classe_mapa")
        )
        quantidade = len(faixas)
        mapa_cores = plt.get_cmap(cmap, quantidade)
        dados_plot.plot(
            ax=ax,
            column="_classe_mapa",
            cmap=mapa_cores,
            vmin=0,
            vmax=max(quantidade - 1, 1),
            edgecolor=estilo.cor_borda,
            linewidth=0.25,
            missing_kwds={"color": estilo.cor_sem_dados, "hatch": "///"},
        )
        for indice, rotulo in faixas.itertuples(index=False):
            legendas.append(
                Patch(facecolor=mapa_cores(indice), edgecolor="none", label=rotulo)
            )
    else:
        dados_plot.plot(
            ax=ax,
            column=coluna,
            cmap=cmap,
            legend=True,
            edgecolor=estilo.cor_borda,
            linewidth=0.25,
            missing_kwds={"color": estilo.cor_sem_dados, "hatch": "///"},
            legend_kwds={
                "label": legenda_titulo,
                "orientation": "vertical",
                "format": FuncFormatter(
                    _formatar_moeda if currency else _formatar_numero
                ),
            },
        )

    if valores.isna().any():
        legendas.append(
            Patch(
                facecolor=estilo.cor_sem_dados,
                edgecolor=estilo.cor_borda,
                hatch="///",
                label="Sem informação",
            )
        )
    if legendas:
        ax.legend(
            handles=legendas,
            title=legenda_titulo,
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            frameon=False,
            fontsize=9,
            title_fontsize=10,
            borderaxespad=0
        )

    ax.set_title(
        titulo,
        loc="left",
        fontsize=20,
        fontweight="bold",
        color=estilo.cor_texto,
        pad=28,
    )
    if subtitulo:
        ax.text(
            0,
            1.01,
            subtitulo,
            transform=ax.transAxes,
            fontsize=10.5,
            color=estilo.cor_secundaria,
            va="bottom",
        )
    ax.annotate(
        "N",
        xy=(0.965, 0.94),
        xytext=(0.965, 0.86),
        xycoords="axes fraction",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color=estilo.cor_texto,
        arrowprops={"facecolor": estilo.cor_texto, "width": 2, "headwidth": 8},
    )
    rodape = fonte if not nota else f"{fonte}\n{nota}"
    ax.text(
        0,
        -0.045,
        rodape,
        transform=ax.transAxes,
        fontsize=8,
        color=estilo.cor_secundaria,
        va="top",
    )
    ax.set_axis_off()
    fig.subplots_adjust(left=0.04, right=0.98, top=0.88, bottom=0.10)

    if arquivo_saida is not None:
        arquivo_saida = Path(arquivo_saida)
        arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            arquivo_saida,
            dpi=estilo.dpi,
            bbox_inches="tight",
            facecolor=fig.get_facecolor(),
        )
        print(f"Visualização exportada:\n{arquivo_saida}")
    else:
        plt.show()
    plt.close(fig)


def formatar_reais(
    valor: float,
    per_capita: bool = False,
) -> str:
    texto = (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    if per_capita:
        texto += " per capita"

    return texto


PALETAS_TEMATICAS = {
    "renda": "YlOrBr",
    "populacao": "Blues",
    "densidade": "PuRd",
    "educacao": "Purples",
    "trabalho": "YlGn",
    "vulnerabilidade": "OrRd",
    "habitacao": "GnBu",
    "alagamentos": "BuPu",
    "infraestrutura": "YlGnBu",
}


def gerar_mapa_portfolio(
    dados: gpd.GeoDataFrame,
    coluna: str,
    titulo: str,
    subtitulo: str,
    tema: str,
    caminho_saida: Path,
    unidade: str | None = None,
    numero_classes: int = 5,
) -> None:
    if coluna not in dados.columns:
        raise KeyError(
            f"A coluna '{coluna}' não existe no GeoDataFrame."
        )

    try:
        from mapclassify import NaturalBreaks
    except ImportError as erro:
        raise ImportError(
            "O pacote 'mapclassify' é necessário para gerar o mapa de portfólio. "
            "Instale-o com 'pip install mapclassify'."
        ) from erro

    mapa = dados.copy()
    mapa[coluna] = mapa[coluna].astype("float64")
    valores_validos = mapa[coluna].dropna()

    if valores_validos.empty:
        raise ValueError(
            f"A coluna '{coluna}' não possui valores válidos."
        )

    paleta = PALETAS_TEMATICAS.get(
        tema,
        "viridis",
    )

    classificador = NaturalBreaks(
        valores_validos,
        k=numero_classes,
    )

    limites = classificador.bins
    limite_inferior = valores_validos.min()

    faixas = []
    inicio = limite_inferior
    for fim in limites:
        faixas.append((inicio, fim))
        inicio = fim

    cmap = plt.get_cmap(
        paleta,
        numero_classes,
    )

    norm = BoundaryNorm(
        boundaries=[limite_inferior, *limites],
        ncolors=numero_classes,
    )

    fig, ax = plt.subplots(
        figsize=(12, 12),
        facecolor="#F7F5F2",
    )
    ax.set_facecolor("#F7F5F2")

    mapa.plot(
        column=coluna,
        cmap=cmap,
        norm=norm,
        linewidth=0.15,
        edgecolor="#FFFFFF",
        ax=ax,
        missing_kwds={
            "color": "#D9D9D9",
            "edgecolor": "#FFFFFF",
            "hatch": "///",
        },
    )

    legendas = []
    for indice, (inicio, fim) in enumerate(faixas):
        if unidade == "reais_per_capita":
            rotulo = (
                f"{formatar_reais(inicio)} a "
                f"{formatar_reais(fim)} per capita"
            )
        elif unidade == "reais":
            rotulo = (
                f"{formatar_reais(inicio)} a "
                f"{formatar_reais(fim)}"
            )
        elif unidade == "percentual":
            rotulo = (
                f"{inicio:.1f}% a {fim:.1f}%"
                .replace(".", ",")
            )
        elif unidade == "habitantes":
            rotulo = (
                f"{inicio:,.0f} a {fim:,.0f} habitantes"
                .replace(",", ".")
            )
        else:
            rotulo = (
                f"{inicio:,.2f} a {fim:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

        legendas.append(
            Patch(
                facecolor=cmap(indice),
                edgecolor="none",
                label=rotulo,
            )
        )

    legendas.append(
        Patch(
            facecolor="#D9D9D9",
            edgecolor="#FFFFFF",
            hatch="///",
            label="Sem informação",
        )
    )

    ax.legend(
        handles=legendas,
        title="Faixas do indicador",
        loc="lower left",
        frameon=True,
        framealpha=0.95,
        facecolor="#FFFFFF",
        edgecolor="none",
        fontsize=9,
        title_fontsize=10,
    )

    ax.set_title(
        titulo,
        loc="left",
        fontsize=20,
        fontweight="bold",
        pad=28,
    )

    ax.text(
        0,
        1.01,
        subtitulo,
        transform=ax.transAxes,
        fontsize=10,
        color="#555555",
        va="bottom",
        ha="left",
    )

    ax.text(
        0,
        -0.035,
        "Fonte: IBGE, Censo Demográfico 2022. "
        "Elaboração própria.",
        transform=ax.transAxes,
        fontsize=8,
        color="#666666",
        ha="left",
    )

    ax.set_axis_off()
    plt.tight_layout()

    caminho_saida.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(
        caminho_saida,
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)

def adicionar_classes_mapa(
    mapa,
    coluna: str,
    numero_classes: int = 5,
    legenda_titulo: str = "",
):
    """Adiciona ao dado as mesmas classes e faixas exibidas na legenda."""
    if coluna not in mapa.columns:
        raise KeyError(f"A coluna '{coluna}' não foi encontrada.")

    resultado = mapa.copy()
    valores = pd.to_numeric(resultado[coluna], errors="coerce")

    if valores.nunique(dropna=True) <= 1:
        resultado["classe_mapa"] = pd.Series(
            pd.NA, index=resultado.index, dtype="Int64"
        )
        resultado["faixa_mapa"] = pd.Series(
            pd.NA, index=resultado.index, dtype="string"
        )
        return resultado

    classes = pd.qcut(
        valores,
        q=min(numero_classes, valores.nunique(dropna=True)),
        duplicates="drop",
    )

    codigos = classes.cat.codes.replace(-1, pd.NA).astype("Int64")
    formatador = (
        _formatar_moeda
        if _is_currency_column(coluna, legenda_titulo)
        else _formatar_numero
    )
    minimo = valores.min()
    rotulos = {}
    for indice, intervalo in enumerate(classes.cat.categories):
        limite_inferior = intervalo.left
        if pd.notna(minimo) and minimo >= 0 and limite_inferior < 0:
            limite_inferior = 0
        rotulos[indice] = (
            f"{formatador(limite_inferior, None)} – "
            f"{formatador(intervalo.right, None)}"
        )

    resultado["classe_mapa"] = codigos
    resultado["faixa_mapa"] = codigos.map(rotulos).astype("string")

    return resultado
