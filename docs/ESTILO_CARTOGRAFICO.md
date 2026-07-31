# Padrão cartográfico

## Estrutura de saída

Todos os dados e produtos ficam fora de `src`:

```text
data/
├── raw/                         # fontes originais
├── processed/                   # tabelas tratadas
└── exports/
    ├── geopackage/              # camadas editáveis no QGIS
    │   ├── populacao/
    │   ├── renda/
    │   ├── domicilios/
    │   ├── entorno/
    │   └── cruzamentos/
    └── mapas/                   # imagens diagramadas
        ├── populacao/
        ├── renda/
        ├── domicilios/
        ├── entorno/
        └── cruzamentos/
```

Arquivos históricos que não seguem a nomenclatura atual ficam em uma pasta
`legado` dentro do respectivo tema.

## Identidade visual

O estilo é centralizado em `src/modules/visualizacao/estilos.py`. Cada tema
possui uma paleta própria:

- renda: `YlOrBr`;
- população: `PuRd`;
- domicílios: `Blues`;
- entorno: `YlGnBu`;
- densidade: `magma`;
- cruzamentos: `viridis`.

O mapa de apresentação usa fundo neutro, limites brancos, cinco classes por
quantis, hachura para setores sem informação, título alinhado à esquerda,
subtítulo, indicação de norte, fonte e legenda discreta.

## Regras de diagramação

1. Usar o nome do município no título e o código IBGE somente no arquivo.
2. Informar indicador e unidade no título da legenda.
3. Manter setores sem informação visíveis e identificados.
4. Não comparar cores de mapas com indicadores diferentes como se tivessem a
   mesma escala.
5. Usar densidade, proporção ou taxa quando a intenção for representar
   concentração; totais absolutos respondem a outra pergunta.
6. Preservar o GeoPackage como produto analítico e o PNG como produto de
   comunicação.

## Pontos ainda a estruturar

- criar um catálogo legível para os códigos `V00090`, `V05200` e demais
  variáveis do IBGE;
- definir indicadores derivados em percentual, evitando mapas apenas de
  contagens absolutas;
- adicionar escala gráfica e mapa de localização;
- criar versões A4 retrato, A4 paisagem e apresentação 16:9;
- criar testes de regressão visual para cores, legendas e posicionamento;
- padronizar nomes de cruzamentos com hífen ou sublinhado, escolhendo apenas
  uma convenção;
- transformar `src/app.py` em uma interface real ou movê-lo para exemplos.
