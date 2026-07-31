from dataclasses import dataclass


@dataclass(frozen=True)
class EstiloMapa:
    """Identidade visual reutilizável para mapas temáticos."""

    nome: str
    cmap: str
    cor_fundo: str = "#F6F4EF"
    cor_texto: str = "#202124"
    cor_secundaria: str = "#5F6368"
    cor_borda: str = "#FFFFFF"
    cor_sem_dados: str = "#D7D9DC"
    figsize: tuple[float, float] = (12, 9)
    dpi: int = 220
    numero_classes: int = 5


ESTILOS_MAPA = {
    "renda": EstiloMapa("Renda", "YlOrBr"),
    "domicilios": EstiloMapa("Domicílios", "Blues"),
    "entorno": EstiloMapa("Entorno", "YlGnBu"),
    "populacao": EstiloMapa("População", "PuRd"),
    "densidade": EstiloMapa("Densidade", "magma"),
    "cruzamento": EstiloMapa("Cruzamento", "viridis"),
    "padrao": EstiloMapa("Indicador", "viridis"),
}


def obter_estilo_mapa(tema: str | None = None) -> EstiloMapa:
    chave = (tema or "padrao").strip().lower().replace("-", "_")
    if chave.startswith("cruzar") or chave.startswith("cruzamento"):
        chave = "cruzamento"
    return ESTILOS_MAPA.get(chave, ESTILOS_MAPA["padrao"])
