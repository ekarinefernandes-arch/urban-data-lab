from dataclasses import asdict, dataclass

import pandas as pd


@dataclass
class RelatorioQualidade:
    """Métricas auditáveis da ingestão e da junção geográfica."""

    total_linhas: int
    codigos_validos: int
    codigos_duplicados: int
    valores_ausentes: int
    valores_nao_numericos: int
    correspondencias_merge: int = 0
    nao_correspondencias_merge: int = 0

    def para_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class ResultadoNormalizacao:
    """Dados padronizados acompanhados da auditoria da normalização."""

    dados: pd.DataFrame
    relatorio: RelatorioQualidade
    valores_invalidos: pd.DataFrame
