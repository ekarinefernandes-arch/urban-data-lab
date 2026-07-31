import argparse
import json
import sys
from pathlib import Path

PROJETO_SRC = Path(__file__).resolve().parents[1]
if str(PROJETO_SRC) not in sys.path:
    sys.path.insert(0, str(PROJETO_SRC))

from modules.ibge.geografia import (
    carregar_malha,
    filtrar_municipio,
    localizar_arquivo_geografia,
)
from modules.ibge.pipeline_renda import executar_pipeline_renda


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Processa e audita a base de renda do Censo 2022."
    )
    parser.add_argument("--municipio", required=True, help="Código IBGE municipal.")
    parser.add_argument("--estado", required=True, help="Sigla da unidade federativa.")
    parser.add_argument(
        "--sobrescrever",
        action="store_true",
        help="Permite substituir produtos processados já existentes.",
    )
    args = parser.parse_args()

    arquivo_geografia = localizar_arquivo_geografia(args.estado)
    malha = filtrar_municipio(
        carregar_malha(arquivo_geografia),
        args.municipio,
    )
    resultado = executar_pipeline_renda(
        codigo_municipio=args.municipio,
        malha=malha,
        sobrescrever=args.sobrescrever,
    )

    print("\nRelatório de qualidade:")
    print(json.dumps(resultado.relatorio.para_dict(), ensure_ascii=False, indent=2))
    print("\nArquivos processados:")
    for nome, caminho in resultado.arquivos.items():
        print(f"- {nome}: {caminho}")


if __name__ == "__main__":
    main()
