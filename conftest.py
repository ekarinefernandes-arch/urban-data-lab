import sys
from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parent
PASTA_SRC = RAIZ_PROJETO / "src"

if str(PASTA_SRC) not in sys.path:
    sys.path.insert(0, str(PASTA_SRC))
    