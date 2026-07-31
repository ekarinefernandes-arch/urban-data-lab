import pandas as pd

from modules.config import (
    ANO_CENSO_2022,
    COLUNA_SETOR_RENDA,
    FONTE_CENSO_2022,
    INDICADORES_RENDA,
)
from modules.ingestao.schemas import COLUNAS_ESQUEMA_INDICADORES
from modules.ingestao.normalizers.valores import converter_moeda_brasileira
from modules.ingestao.quality import RelatorioQualidade, ResultadoNormalizacao
from modules.ingestao.validators.dataframe import (
    validar_colunas_obrigatorias,
    validar_duplicidades,
)
from modules.ingestao.validators.territorial import normalizar_codigo_territorial


def normalizar_renda_ibge(
    dados: pd.DataFrame,
    *,
    ano: int = ANO_CENSO_2022,
    fonte: str = FONTE_CENSO_2022,
) -> pd.DataFrame:
    """Converte a tabela bruta de renda do IBGE para o esquema interno longo."""
    return normalizar_renda_ibge_com_qualidade(
        dados,
        ano=ano,
        fonte=fonte,
    ).dados


def normalizar_renda_ibge_com_qualidade(
    dados: pd.DataFrame,
    *,
    ano: int = ANO_CENSO_2022,
    fonte: str = FONTE_CENSO_2022,
) -> ResultadoNormalizacao:
    """Normaliza renda e registra problemas recuperáveis sem interromper o lote."""
    colunas_brutas = [COLUNA_SETOR_RENDA, *INDICADORES_RENDA]
    validar_colunas_obrigatorias(
        dados,
        colunas_brutas,
        contexto="renda bruta do IBGE",
    )

    codigo_setor = normalizar_codigo_territorial(
        dados[COLUNA_SETOR_RENDA],
        tamanho=15,
        nome="codigo_setor",
        erros="coerce",
    )
    codigos_validos = codigo_setor.notna()
    codigos_duplicados = int(
        codigo_setor[codigos_validos].duplicated(keep=False).sum()
    )
    dados_validos = dados.loc[codigos_validos].copy()
    dados_validos["_codigo_setor"] = codigo_setor.loc[codigos_validos]
    dados_validos = dados_validos.drop_duplicates(
        subset="_codigo_setor",
        keep="first",
    )

    blocos: list[pd.DataFrame] = []
    invalidos: list[pd.DataFrame] = []
    total_ausentes = 0
    total_nao_numericos = 0

    for coluna_bruta, regra in INDICADORES_RENDA.items():
        valores, ausentes, nao_numericos = converter_moeda_brasileira(
            dados_validos[coluna_bruta]
        )
        total_ausentes += int(ausentes.sum())
        total_nao_numericos += int(nao_numericos.sum())
        if nao_numericos.any():
            invalidos.append(
                pd.DataFrame(
                    {
                        "linha_origem": dados_validos.index[nao_numericos],
                        "codigo_setor": dados_validos.loc[
                            nao_numericos,
                            "_codigo_setor",
                        ],
                        "coluna_origem": coluna_bruta,
                        "valor_original": dados_validos.loc[
                            nao_numericos,
                            coluna_bruta,
                        ].astype("string"),
                        "motivo": "valor_nao_numerico",
                    }
                )
            )
        bloco = pd.DataFrame(
            {
                "codigo_setor": dados_validos["_codigo_setor"],
                "codigo_municipio": dados_validos["_codigo_setor"].str.slice(0, 7),
                "nome_municipio": pd.Series(
                    pd.NA,
                    index=dados_validos.index,
                    dtype="string",
                ),
                "ano": int(ano),
                "fonte": fonte,
                "indicador": regra["indicador"],
                "valor": valores,
                "unidade": regra["unidade"],
            }
        )
        blocos.append(bloco.reset_index(drop=True))

    resultado = pd.concat(blocos, ignore_index=True)
    resultado["codigo_municipio"] = normalizar_codigo_territorial(
        resultado["codigo_municipio"],
        tamanho=7,
        nome="codigo_municipio",
    )
    validar_duplicidades(
        resultado,
        ["codigo_setor", "ano", "fonte", "indicador"],
        contexto="renda padronizada",
    )
    registros_invalidos = (
        pd.concat(invalidos, ignore_index=True)
        if invalidos
        else pd.DataFrame(
            columns=[
                "linha_origem",
                "codigo_setor",
                "coluna_origem",
                "valor_original",
                "motivo",
            ]
        )
    )
    relatorio = RelatorioQualidade(
        total_linhas=len(dados),
        codigos_validos=int(codigos_validos.sum()),
        codigos_duplicados=codigos_duplicados,
        valores_ausentes=total_ausentes,
        valores_nao_numericos=total_nao_numericos,
    )
    return ResultadoNormalizacao(
        dados=resultado.loc[:, COLUNAS_ESQUEMA_INDICADORES],
        relatorio=relatorio,
        valores_invalidos=registros_invalidos,
    )
