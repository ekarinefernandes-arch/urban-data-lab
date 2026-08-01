from __future__ import annotations

import sys
from pathlib import Path

PROJETO_SRC = Path(__file__).resolve().parent
if str(PROJETO_SRC) not in sys.path:
    sys.path.insert(0, str(PROJETO_SRC))

import streamlit as st

from modules.ibge.interface import gerar_painel_ibge, listar_municipios_por_uf, listar_ufs

st.set_page_config(page_title="Painel IBGE", page_icon="🗺️", layout="wide")

st.title("Painel interativo do IBGE")
st.write(
    "Busque dados censitários por UF, município e tema para visualizar "
    "uma tabela e um mapa."
)

with st.sidebar:
    st.header("Filtros")
    ufs = listar_ufs()
    if not ufs:
        st.error("Nenhuma UF foi encontrada na base do Censo.")
        st.stop()

    uf = st.selectbox("UF", options=[sigla for sigla, _ in ufs], index=0)
    municipios = listar_municipios_por_uf(uf)
    if not municipios:
        st.error("Nenhum município foi encontrado para a UF selecionada.")
        st.stop()

    nomes_por_codigo = dict(municipios)
    municipio = st.selectbox(
        "Município",
        options=list(nomes_por_codigo),
        index=0,
        format_func=lambda codigo: nomes_por_codigo[codigo],
    )
    tipo = st.selectbox(
        "Bloco do IBGE",
        options=["populacao", "renda"],
        format_func=lambda item: {
            "populacao": "População",
            "renda": "Renda",
        }[item],
    )
    variavel = None
    if tipo == "renda":
        variavel = st.selectbox(
            "Indicador",
            options=["renda_media_responsavel", "renda_mediana_responsavel"],
            format_func=lambda item: {
                "renda_media_responsavel": "Renda média",
                "renda_mediana_responsavel": "Renda mediana",
            }[item],
        )

    if st.button("Gerar painel"):
        try:
            with st.spinner("Processando dados e mapa..."):
                dataset, caminho_gpkg, caminho_png, coluna = gerar_painel_ibge(
                    uf=uf,
                    municipio=municipio,
                    tipo=tipo,
                    variavel=variavel,
                )
        except Exception as erro:
            st.error(f"Não foi possível gerar o painel: {erro}")
        else:
            st.session_state["dataset"] = dataset
            st.session_state["caminho_gpkg"] = caminho_gpkg
            st.session_state["caminho_png"] = caminho_png
            st.session_state["coluna"] = coluna

if "dataset" in st.session_state:
    tabela = st.session_state["dataset"]
    caminho_gpkg = st.session_state["caminho_gpkg"]
    caminho_png = st.session_state["caminho_png"]
    coluna = st.session_state["coluna"]

    st.subheader("Mapa")
    st.image(
        str(caminho_png),
        caption="Mapa temático do município selecionado",
        use_container_width=True,
    )

    st.subheader("Dados representados no mapa")
    st.write(
        "Baixe a tabela simplificada contendo os setores, "
        "valores e faixas utilizadas no mapa."
    )

    st.download_button(
        label="Baixar planilha do mapa",
        data=tabela.to_csv(
            index=False,
            sep=";",
            encoding="utf-8-sig",
        ),
        file_name=f"{coluna}_por_setor.csv",
        mime="text/csv",
    )

    with st.expander("Visualizar os dados"):
        st.dataframe(tabela.head(50), use_container_width=True)