import json
from pathlib import Path

import pandas as pd

from modules.ingestao.quality import RelatorioQualidade


def _validar_destinos(
    destinos: list[Path],
    *,
    sobrescrever: bool,
) -> None:
    existentes = [caminho for caminho in destinos if caminho.exists()]
    if existentes and not sobrescrever:
        nomes = ", ".join(str(caminho) for caminho in existentes)
        raise FileExistsError(
            "Resultados processados já existem e não serão sobrescritos: "
            f"{nomes}"
        )


def salvar_resultados_renda(
    dados: pd.DataFrame,
    valores_invalidos: pd.DataFrame,
    relatorio: RelatorioQualidade,
    pasta: Path,
    *,
    identificador: str,
    sobrescrever: bool = False,
) -> dict[str, Path]:
    """Persiste renda padronizada e sua auditoria em arquivos separados."""
    pasta = Path(pasta)
    caminhos = {
        "dados": pasta / f"renda_{identificador}.csv",
        "invalidos": pasta / f"renda_{identificador}_invalidos.csv",
        "qualidade": pasta / f"renda_{identificador}_qualidade.json",
    }
    _validar_destinos(list(caminhos.values()), sobrescrever=sobrescrever)
    pasta.mkdir(parents=True, exist_ok=True)

    dados.to_csv(caminhos["dados"], index=False, encoding="utf-8-sig")
    valores_invalidos.to_csv(
        caminhos["invalidos"],
        index=False,
        encoding="utf-8-sig",
    )
    caminhos["qualidade"].write_text(
        json.dumps(relatorio.para_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return caminhos
