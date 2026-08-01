import argparse
import sys
from pathlib import Path

PROJETO_SRC = Path(__file__).resolve().parents[1]
if str(PROJETO_SRC) not in sys.path:
    sys.path.insert(0, str(PROJETO_SRC))

from modules.config import PASTA_EXPORTACOES_GPKG, PASTA_EXPORTACOES_MAPAS
from modules.ibge.censo import localizar_csv
from modules.ibge.domicilios import preparar_domicilios
from modules.ibge.entorno import preparar_entorno
from modules.ibge.geografia import (
    carregar_malha,
    filtrar_municipio,
    localizar_arquivo_geografia,
)
from modules.ibge.pipeline import (
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


def carregar_malha_por_estado(municipio: str, estado: str | None = None) -> object:
    arquivo_geo = localizar_arquivo_geografia(estado)
    malha = carregar_malha(arquivo_geo)
    return filtrar_municipio(malha, municipio)


def montar_titulo(tipo: str, municipio: str, coluna: str) -> str:
    nome_tipo = {
        "populacao": "PopulaÃ§Ã£o",
        "renda": "Renda mÃ©dia do responsÃ¡vel",
        "domicilios": "DomicÃ­lios",
        "entorno": "Entorno",
        "cruzar-censo-renda": "Cruzamento Censo x Renda",
        "cruzar-domicilios-entorno": "Cruzamento DomicÃ­lios x Entorno",
    }

    return f"{nome_tipo.get(tipo, tipo)} â€” {coluna} â€” {municipio}"


def _exportar_mapa(mapa, tipo: str, municipio: str, coluna: str):
    pasta = PASTA_EXPORTACOES_GPKG / _subpasta_tipo(tipo)
    pasta.mkdir(parents=True, exist_ok=True)

    nome_arquivo = f"{tipo}_{municipio.lower().replace(' ', '_')}_{coluna}"

    return exportar_gpkg(
        mapa=mapa,
        pasta_exportacao=pasta,
        nome_arquivo=nome_arquivo,
        camada=f"{tipo}_{coluna}",
    )


def gerar_mapa(
    malha,
    dataset,
    coluna,
    tipo,
    municipio,
):
    mapa = preparar_mapa_tematico(
        malha=malha,
        indicadores=dataset,
        coluna_indicador=coluna,
        chave="CD_SETOR",
    )

    titulo, subtitulo, legenda = obter_textos_padronizados(coluna, municipio)
    arquivo = _exportar_mapa(mapa, tipo, municipio, coluna)
    imagem = (
        PASTA_EXPORTACOES_MAPAS
        / _subpasta_tipo(tipo)
        / arquivo.with_suffix(".png").name
    )
    plotar_mapa(
        mapa=mapa,
        coluna=coluna,
        titulo=titulo,
        legenda_titulo=legenda,
        arquivo_saida=imagem,
        subtitulo="DistribuiÃ§Ã£o por setor censitÃ¡rio",
        tema=tipo,
    )


def gerar_mapa_pronto(mapa, coluna, tipo, municipio):
    titulo, subtitulo, legenda = obter_textos_padronizados(coluna, municipio)
    arquivo = _exportar_mapa(mapa, tipo, municipio, coluna)
    imagem = (
        PASTA_EXPORTACOES_MAPAS
        / _subpasta_tipo(tipo)
        / arquivo.with_suffix(".png").name
    )
    plotar_mapa(
        mapa=mapa,
        coluna=coluna,
        titulo=titulo,
        legenda_titulo=legenda,
        arquivo_saida=imagem,
        subtitulo="IntegraÃ§Ã£o de indicadores por setor censitÃ¡rio",
        tema=tipo,
    )


def escolher_interativo() -> dict:
    tipos = [
        "populacao",
        "renda",
        "domicilios",
        "entorno",
        "cruzar-censo-renda",
        "cruzar-domicilios-entorno",
    ]

    print("Escolha o tipo de mapa:")
    for i, tipo in enumerate(tipos, start=1):
        print(f"{i}. {tipo}")

    indice = int(input("Digite o nÃºmero do tipo de mapa: ").strip())
    tipo = tipos[indice - 1]

    municipio = input("Digite o nome ou cÃ³digo IBGE do municÃ­pio: ").strip()
    estado = input("Digite a sigla do estado (opcional): ").strip() or None
    variavel = None
    variavel_domicilios = None
    variavel_entorno = None
    coluna_plot = None

    if tipo in {"domicilios", "entorno"}:
        variavel = input("Digite a variÃ¡vel a ser mapeada (por exemplo V00090 ou V05200): ").strip()

    if tipo == "cruzar-domicilios-entorno":
        variavel_domicilios = input("Digite a variÃ¡vel de domicÃ­lios: ").strip()
        variavel_entorno = input("Digite a variÃ¡vel de entorno: ").strip()
        coluna_plot = input("Digite a coluna a plotar no resultado do cruzamento (ou deixe vazio): ").strip() or None

    return {
        "tipo": tipo,
        "municipio": municipio,
        "estado": estado,
        "variavel": variavel,
        "variavel_domicilios": variavel_domicilios,
        "variavel_entorno": variavel_entorno,
        "coluna_plot": coluna_plot,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gerador interativo de mapas temÃ¡ticos para IBGE."
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
        required=False,
    )
    parser.add_argument(
        "--municipio",
        default="4115200",
        help="Nome ou cÃ³digo IBGE do municÃ­pio.",
    )
    parser.add_argument(
        "--estado",
        help="Sigla do estado para busca de municÃ­pios (em desenvolvimento).",
    )
    parser.add_argument(
        "--variavel",
        help="VariÃ¡vel para domicÃ­lios ou entorno.",
    )
    parser.add_argument(
        "--variavel-domicilios",
        help="VariÃ¡vel de domicÃ­lios para cruzamento.",
    )
    parser.add_argument(
        "--variavel-entorno",
        help="VariÃ¡vel de entorno para cruzamento.",
    )
    parser.add_argument(
        "--coluna-plot",
        help="Coluna a ser usada no mapa de cruzamento.",
    )

    args = parser.parse_args()

    if args.tipo is None:
        valores = escolher_interativo()
        args.tipo = valores["tipo"]
        args.municipio = valores["municipio"]
        args.estado = valores["estado"]
        args.variavel = valores["variavel"]
        args.variavel_domicilios = valores["variavel_domicilios"]
        args.variavel_entorno = valores["variavel_entorno"]
        args.coluna_plot = valores["coluna_plot"]

    malha = carregar_malha_por_estado(args.municipio, args.estado)

    if args.tipo == "populacao":
        dataset = construir_dataset_populacao(municipio=args.municipio)
        gerar_mapa(
            malha=malha,
            dataset=dataset,
            coluna="populacao",
            tipo="populacao",
            municipio=args.municipio,
        )
        return

    if args.tipo == "renda":
        coluna = args.variavel or "renda_media_responsavel"
        dataset = construir_dataset_renda(codigo_municipio=args.municipio)
        gerar_mapa(
            malha=malha,
            dataset=dataset,
            coluna=coluna,
            tipo="renda",
            municipio=args.municipio,
        )
        return

    if args.tipo == "domicilios":
        if not args.variavel:
            raise ValueError("Informe --variavel para o tipo domicilios.")
        dataset = preparar_domicilios(
            codigo_municipio=args.municipio,
            variaveis=[args.variavel],
        )
        gerar_mapa(
            malha=malha,
            dataset=dataset,
            coluna=args.variavel,
            tipo="domicilios",
            municipio=args.municipio,
        )
        return

    if args.tipo == "entorno":
        if not args.variavel:
            raise ValueError("Informe --variavel para o tipo entorno.")
        dataset = preparar_entorno(
            codigo_municipio=args.municipio,
            variaveis=[args.variavel],
        )
        gerar_mapa(
            malha=malha,
            dataset=dataset,
            coluna=args.variavel,
            tipo="entorno",
            municipio=args.municipio,
        )
        return

    if args.tipo == "cruzar-censo-renda":
        mapa = cruzar_censo_renda(
            malha=malha,
            populacao=construir_dataset_populacao(municipio=args.municipio),
            renda=construir_dataset_renda(codigo_municipio=args.municipio),
        )
        coluna = args.coluna_plot or "renda_media_responsavel"
        gerar_mapa_pronto(
            mapa=mapa,
            coluna=coluna,
            tipo="cruzar-censo-renda",
            municipio=args.municipio,
        )
        return

    if args.tipo == "cruzar-domicilios-entorno":
        if not args.variavel_domicilios or not args.variavel_entorno:
            raise ValueError("Informe --variavel-domicilios e --variavel-entorno para o cruzamento.")
        mapa = cruzar_domicilios_entorno(
            malha=malha,
            domicilios=preparar_domicilios(
                codigo_municipio=args.municipio,
                variaveis=[args.variavel_domicilios],
            ),
            entorno=preparar_entorno(
                codigo_municipio=args.municipio,
                variaveis=[args.variavel_entorno],
            ),
        )
        coluna = args.coluna_plot or args.variavel_domicilios
        gerar_mapa_pronto(
            mapa=mapa,
            coluna=coluna,
            tipo="cruzar-domicilios-entorno",
            municipio=args.municipio,
        )
        return


if __name__ == "__main__":
    main()
