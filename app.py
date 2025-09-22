import streamlit as st
import polars as pl
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# --------------------------
# Configuração da página
# --------------------------
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

# CSS para alinhar os botões
st.markdown(
    """
    <style>
    div.stButton > button {
        height: 60px;
        margin-top: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Logo + Título
# --------------------------
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("### 🔍 Consulta de Códigos CRM")
with col2:
    st.image("logo.png", width=120)

# --------------------------
# Entrada de códigos
# --------------------------
col_input, col_b1, col_b2 = st.columns([4, 1, 1])

with col_input:
    input_area = st.text_area(
        "Digite os códigos (separados por vírgula ou quebra de linha):",
        key="input_area",
        height=100
    )

with col_b1:
    buscar = st.button("🔎 Buscar", use_container_width=True)

with col_b2:
    nova_pesquisa = st.button("🗑️ Nova Pesquisa", use_container_width=True)
    if nova_pesquisa:
        st.session_state.input_area = ""
        st.rerun()

# --------------------------
# Carregamento dos dados
# --------------------------
@st.cache_data
def carregar_dados():
    return pl.read_excel("dados.xlsx")

df = carregar_dados()

# --------------------------
# Processamento da busca
# --------------------------
if buscar and input_area.strip():
    # Normaliza entrada
    codigos = [c.strip() for c in input_area.replace("\n", ",").split(",") if c.strip()]

    # Filtra dados
    resultado = df.filter(pl.col("Code").is_in(codigos))

    if resultado.is_empty():
        st.warning("Nenhum código encontrado.")
    else:
        # Ajusta dados
        resultado_pd = resultado.to_pandas()

        # Remove colunas indesejadas (como Unnamed: 0, index, etc.)
        resultado_pd = resultado_pd.loc[:, ~resultado_pd.columns.str.contains("^Unnamed")]

        # Adiciona ID sequencial
        resultado_pd.insert(0, "ID", range(1, len(resultado_pd) + 1))

        # Descrição maiúscula
        if "Description" in resultado_pd.columns:
            resultado_pd["Description"] = resultado_pd["Description"].str.upper()

        # Preço com $
        if "Price" in resultado_pd.columns:
            resultado_pd["Price"] = resultado_pd["Price"].apply(
                lambda x: f"${x:,.2f}" if pd.notnull(x) else ""
            )

        # --------------------------
        # Mostrando com AgGrid
        # --------------------------
        gb = GridOptionsBuilder.from_dataframe(resultado_pd)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        gb.configure_column("ID", width=80)
        grid_options = gb.build()

        AgGrid(
            resultado_pd,
            gridOptions=grid_options,
            fit_columns_on_grid_load=True,
            height=400,
            enable_enterprise_modules=False,
        )
