import streamlit as st
import polars as pl
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# ==============================
# Configuração da página
# ==============================
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

# Título com ícone
st.markdown(
    """
    <h2 style="display: flex; align-items: center; font-family: Arial; margin-bottom: 20px;">
        🔍 Consulta de Códigos CRM
    </h2>
    """,
    unsafe_allow_html=True,
)

# ==============================
# Carregar dados
# ==============================
@st.cache_data
def carregar_dados():
    return pl.read_excel("dados.xlsx", sheet_name="Planilha1")

df = carregar_dados()

# 👀 Mostra nomes reais das colunas
st.write("Colunas encontradas no Excel:", df.columns)

# ==============================
# Caixa de busca + botão
# ==============================
col1, col2 = st.columns([6, 1])
with col1:
    input_area = st.text_area("Digite os códigos (um por linha):", height=120)
with col2:
    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)  # alinhamento
    buscar = st.button("Pesquisar", use_container_width=True)

# ==============================
# Lógica de pesquisa
# ==============================
if buscar and input_area.strip():
    codigos_digitados = [c.strip() for c in input_area.splitlines() if c.strip()]

    # ⚠️ Ajuste aqui os nomes das colunas conforme mostrado em df.columns
    col_id = "Product ID"
    col_desc = "Description"
    col_price = "Price"

    resultado = df.filter(pl.col(col_id).is_in(codigos_digitados))

    if resultado.is_empty():
        st.warning("Nenhum código encontrado.")
    else:
        # Apenas as colunas desejadas
        resultado = resultado.select([col_id, col_desc, col_price])

        # ==============================
        # Configuração AgGrid
        # ==============================
        gb = GridOptionsBuilder.from_dataframe(resultado.to_pandas())
        gb.configure_default_column(
            resizable=True, filter=True, sortable=True, wrapText=True, autoHeight=True
        )
        gb.configure_grid_options(
            getRowStyle="""function(params) {
                if (params.node.rowIndex % 2 === 0) {
                    return { 'backgroundColor': '#f9f9f9' }
                }
                return { 'backgroundColor': 'white' }
            }"""
        )
        gridOptions = gb.build()

        st.subheader("Resultado da Pesquisa")
        AgGrid(
            resultado.to_pandas(),
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=True,
            height=400,
            theme="balham",
        )
