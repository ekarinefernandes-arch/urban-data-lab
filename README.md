# Urban Data Lab

Biblioteca em Python para análise de dados urbanos utilizando bases oficiais do IBGE e dados geoespaciais.

O projeto tem como objetivo construir uma plataforma modular para leitura, tratamento, integração e visualização de dados territoriais, servindo de base para estudos de planejamento urbano, geoprocessamento, mercado imobiliário e Planta Genérica de Valores (PGV).

---

## Objetivos

- Automatizar a leitura de bases oficiais do IBGE;
- Integrar dados estatísticos e geográficos;
- Produzir mapas temáticos em Python;
- Criar indicadores urbanos reutilizáveis;
- Estruturar uma biblioteca para análises espaciais.

---
# Arquitetura do projeto

Urban Data Lab foi projetado para ser modular.

Cada conjunto de dados do IBGE possui seu próprio módulo responsável pela leitura, tratamento e preparação das informações.

Essa arquitetura permite adicionar novos conjuntos de dados sem alterar o restante da aplicação.

---
# Estrutura do projeto

```text
urban-data-lab/

├── data/
│   ├── exports/
│   ├── processed/
│   └── raw/
│       ├── censo/
│       │   ├── basico/
│       │   ├── dicionarios/
│       │   ├── domicilios/
│       │   ├── entorno/
│       │   └── renda/
│       └── geografia/
│
├── src/
│   ├── modules/
│   │   ├── ibge/
│   │   │   ├── api.py
│   │   │   ├── baixar_dados_censo.py
│   │   │   ├── censo.py
│   │   │   ├── geografia.py
│   │   │   └── indicadores.py
│   │   │
│   │   ├── mercado/
│   │   └── visualizacao/
│   │
│   ├── app.py
│   ├── inspecionar_censo.py
│   ├── mapa_populacao.py
│   ├── mapa_setores.py
│   └── testar_dados_municipio.py
│
├── tests/
├── README.md
└── requirements.txt
```

---

# Funcionalidades implementadas

Atualmente o projeto já permite:

- leitura dos agregados do Censo Demográfico 2022;
- leitura da malha dos setores censitários;
- filtragem por município utilizando o código IBGE;
- integração entre dados censitários e geometria;
- geração de mapas temáticos de população;
- exportação em GeoPackage;
- estrutura modular para reutilização em novos indicadores.

---

# Fluxo atual

```text
Agregados do Censo
        │
        ▼
Leitura dos dados
        │
        ▼
Filtragem do município
        │
        ▼
Preparação dos indicadores
        │
        ▼
Leitura da malha geográfica
        │
        ▼
Junção por CD_SETOR
        │
        ▼
GeoDataFrame
        │
        ▼
Mapa temático
        │
        ▼
Exportação (.gpkg)
```

---

# Estrutura do módulo IBGE

O módulo `ibge` centraliza todas as funções relacionadas às bases oficiais do IBGE.

Atualmente:

- leitura dos agregados censitários;
- leitura das malhas geográficas;
- preparação dos indicadores básicos.

Em desenvolvimento:

- indicadores de renda;
- indicadores de domicílios;
- indicadores de entorno urbano.

---

# Dados utilizados

## Censo Demográfico 2022

- Dados básicos
- Dicionários de dados
- Características dos domicílios
- Rendimento do responsável
- Entorno dos domicílios

## Dados geográficos

- Setores censitários
- Malhas territoriais

---

# Roadmap

## Versão 0.1 ✔

- Estrutura do projeto
- Integração entre Censo e Geometria
- Primeiro mapa temático

## Próximas versões

- Módulo de renda
- Módulo de domicílios
- Módulo de entorno
- Indicadores urbanos
- Integração completa dos dados do IBGE
- Estudos voltados à PGV
- Integração com outras bases públicas

---

# Tecnologias

- Python
- Pandas
- GeoPandas
- Matplotlib
- Shapely
- Pyogrio
- QGIS
- Git

---

# Autora

**Emmanuely Karine Fernandes da Paz**

Arquiteta e Urbanista

Especialista em Geoprocessamento, Planejamento Urbano e Ciência de Dados aplicada ao território.

---
**Urban Data Lab** é um projeto em desenvolvimento contínuo voltado à criação de ferramentas abertas para análise espacial e planejamento urbano utilizando dados públicos.