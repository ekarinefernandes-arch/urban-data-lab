import argparse
import sys
from pathlib import Path

PROJETO_SRC = Path(__file__).resolve().parents[1]
if str(PROJETO_SRC) not in sys.path:
    sys.path.insert(0, str(PROJETO_SRC))

from modules.config import PASTA_EXPORTACOES_GPKG, PASTA_EXPORTACOES_MAPAS
from modules.ibge.domicilios import preparar_domicilios
from modules.ibge.geografia import (
    carregar_malha,
    filtrar_municipio,
    localizar_arquivo_geografia,
)
from modules.ibge.pipeline import (
    construir_dataset_entorno,
    construir_dataset_populacao,
    construir_dataset_renda,
)
from modules.ibge.cruzamento import (
    cruzar_censo_renda,
    cruzar_domicilios_entorno,
)
from modules.visualizacao.mapas import (
    exportar_gpkg,
    obter_textos_padronizados,
    plotar_mapa,
    preparar_mapa_tematico,
)


def _subpasta_tipo(tipo: str) -> Path:
    if tipo.startswith("cruzar") or tipo.startswith("cruzamento"):
        return Path("cruzamentos") / tipo.replace("-", "_")
    return Path(tipo)


def carregar_malha_municipio(municipio: str, estado: str | None = None) -> object:
    arquivo_geo = localizar_arquivo_geografia(estado)
    malha = carregar_malha(arquivo_geo)
    malha_municipio = filtrar_municipio(malha, municipio)
    malha_municipio["CD_SETOR"] = (
        malha_municipio["CD_SETOR"]
        .astype("string")
        .str.strip()
    )
    return malha_municipio


def _exportar_mapa(
    mapa,
    tipo: str,
    municipio: str,
    coluna: str,
):
    pasta = PASTA_EXPORTACOES_GPKG / _subpasta_tipo(tipo)
    pasta.mkdir(parents=True, exist_ok=True)

    nome_arquivo = (
        f"{tipo}_{municipio.lower().replace(' ', '_')}_{coluna}"
    )

    arquivo = exportar_gpkg(
        mapa=mapa,
        pasta_exportacao=pasta,
        nome_arquivo=nome_arquivo,
        camada=f"{tipo}_{coluna}",
    )

    return arquivo


def montar_legenda(tipo: str, coluna: str) -> str:
    if tipo == "populacao":
        return "População"
    if tipo == "renda":
        if coluna == "renda_media_responsavel":
            return "Renda média do responsável (R$)"
        if coluna == "renda_mediana_responsavel":
            return "Renda mediana do responsável (R$)"
    if tipo == "domicilios":
        return coluna
    if tipo == "entorno":
        return coluna
    if tipo == "cruzar-censo-renda":
        if coluna == "renda_media_responsavel":
            return "Renda média do responsável (R$)"
        if coluna == "renda_mediana_responsavel":
            return "Renda mediana do responsável (R$)"
        return coluna
    if tipo == "cruzar-domicilios-entorno":
        return coluna
    return coluna


def gerar_mapa_simples(
    malha,
    dataset,
    coluna,
    titulo,
    tipo,
    municipio,
):
    mapa = preparar_mapa_tematico(
        malha=malha,
        indicadores=dataset,
        coluna_indicador=coluna,
        chave="CD_SETOR",
    )

    titulo, subtitulo, legenda_titulo = obter_textos_padronizados(
        coluna,
        municipio,
    )

    print(f"Gerando mapa: {titulo}")
    arquivo = _exportar_mapa(mapa, tipo, municipio, coluna)
    imagem = (
        PASTA_EXPORTACOES_MAPAS
        / _subpasta_tipo(tipo)
        / arquivo.with_suffix(".png").name
    )
    plotar_mapa(
        mapa,
        coluna,
        titulo,
        legenda_titulo=legenda_titulo,
        arquivo_saida=imagem,
        subtitulo=subtitulo,
        tema=tipo,
    )


def gerar_mapa_cruzamento(
    malha,
    mapa,
    coluna,
    tipo,
    municipio,
):
    titulo, subtitulo, legenda_titulo = obter_textos_padronizados(
        coluna,
        municipio,
    )
    print(f"Gerando mapa de cruzamento: {tipo}")
    arquivo = _exportar_mapa(mapa, tipo, municipio, coluna)
    imagem = (
        PASTA_EXPORTACOES_MAPAS
        / _subpasta_tipo(tipo)
        / arquivo.with_suffix(".png").name
    )
    plotar_mapa(
        mapa,
        coluna,
        titulo,
        legenda_titulo=legenda_titulo,
        arquivo_saida=imagem,
        subtitulo=subtitulo,
        tema=tipo,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera mapas temáticos para censitário, renda, domicílios e entorno."
    )

    parser.add_argument(
        "--tipo",
        choices=[
            "populacao",
            "renda",
            "domicilios",
            "entorno",
            "cruzar-censo-renda",
            "cruzar-domicilios-entorno",
        ],
        required=True,
    )
    parser.add_argument(
        "--municipio",
        default="4115200",
        help="Nome ou código IBGE do município.",
    )
    parser.add_argument(
        "--estado",
        help="Sigla do estado para localizar o arquivo geográfico correto.",
    )
    parser.add_argument(
        "--variavel",
        help="Variável a plotar para renda, domicílios ou entorno.",
    )
    parser.add_argument(
        "--variavel-domicilios",
        help="Variável de domicílios para o cruzamento com entorno.",
    )
    parser.add_argument(
        "--variavel-entorno",
        help="Variável de entorno para o cruzamento com domicílios.",
    )
    parser.add_argument(
        "--coluna-plot",
        help="Coluna a ser usada no mapa de cruzamento.",
    )

    args = parser.parse_args()

    malha = carregar_malha_municipio(
        municipio=args.municipio,
        estado=args.estado,
    )
    nome_municipio = (
        str(malha["NM_MUN"].iloc[0])
        if "NM_MUN" in malha.columns
        else args.municipio
    )

    if args.tipo == "populacao":
        dataset = construir_dataset_populacao(municipio=args.municipio)
        gerar_mapa_simples(
            malha=malha,
            dataset=dataset,
            coluna="populacao",
            titulo=f"População por setor — {nome_municipio}",
            tipo="populacao",
            municipio=nome_municipio,
        )
        return

    if args.tipo == "renda":
        coluna = args.variavel or "renda_media_responsavel"
        dataset = construir_dataset_renda(codigo_municipio=args.municipio)
        gerar_mapa_simples(
            malha=malha,
            dataset=dataset,
            coluna=coluna,
            titulo=f"Renda por setor — {nome_municipio}",
            tipo="renda",
            municipio=nome_municipio,
        )
        return

    if args.tipo == "domicilios":
        if not args.variavel:
            raise ValueError(
                "Informe --variavel para o tipo domicilios."
            )
        dataset = preparar_domicilios(
            codigo_municipio=args.municipio,
            variaveis=[args.variavel],
        )
        gerar_mapa_simples(
            malha=malha,
            dataset=dataset,
            coluna=args.variavel,
            titulo=f"Domicílios por setor — {nome_municipio}",
            tipo="domicilios",
            municipio=nome_municipio,
        )
        return

    if args.tipo == "entorno":
        if not args.variavel:
            raise ValueError(
                "Informe --variavel para o tipo entorno."
            )
        dataset = construir_dataset_entorno(
            codigo_municipio=args.municipio,
            variaveis=[args.variavel],
        )
        gerar_mapa_simples(
            malha=malha,
            dataset=dataset,
            coluna=args.variavel,
            titulo=f"Entorno por setor — {nome_municipio}",
            tipo="entorno",
            municipio=nome_municipio,
        )
        return

    if args.tipo == "cruzar-censo-renda":
        mapa = cruzar_censo_renda(
            malha=malha,
            populacao=construir_dataset_populacao(
                municipio=args.municipio,
            ),
            renda=construir_dataset_renda(
                codigo_municipio=args.municipio,
            ),
        )
        coluna = args.coluna_plot or "renda_media_responsavel"
        gerar_mapa_cruzamento(
            malha=malha,
            mapa=mapa,
            coluna=coluna,
            tipo="cruzar_censo_renda",
            municipio=nome_municipio,
        )
        return

    if args.tipo == "cruzar-domicilios-entorno":
        if not args.variavel_domicilios or not args.variavel_entorno:
            raise ValueError(
                "Informe --variavel-domicilios e --variavel-entorno para o cruzamento."
            )
        mapa = cruzar_domicilios_entorno(
            malha=malha,
            domicilios=preparar_domicilios(
                codigo_municipio=args.municipio,
                variaveis=[args.variavel_domicilios],
            ),
            entorno=construir_dataset_entorno(
                codigo_municipio=args.municipio,
                variaveis=[args.variavel_entorno],
            ),
        )
        coluna = args.coluna_plot or args.variavel_domicilios
        gerar_mapa_cruzamento(
            malha=malha,
            mapa=mapa,
            coluna=coluna,
            tipo="cruzar_domicilios_entorno",
            municipio=nome_municipio,
        )
        return


if __name__ == "__main__":
    main()
