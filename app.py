import streamlit as st
import polars as pl
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO

st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

# --- carregar Excel ---
@st.cache_data
def carregar_dados(caminho="dados.xlsx"):
    return pl.read_excel(caminho)

df = carregar_dados()

# --- Input de códigos ---
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

codigos_input = st.text_area("Digite os códigos (um por linha):", value=st.session_state["input_area"], height=150)

col1, col2 = st.columns([1,1])
with col1:
    buscar = st.button("🔍 Buscar")
with col2:
    if st.button("🧹 Nova pesquisa"):
        st.session_state.input_area = ""
        st.experimental_rerun()

# --- Função para manter preço igual Excel com $ ---
def manter_preco_com_dolar(x):
    if x is None: return ""
    s = str(x).strip()
    if s == "" or s.lower() in ["nan", "none", "na", "n/a"]:
        return ""
    if s.startswith("$"):
        return s
    return f"${s}"

# --- Busca ---
if buscar and codigos_input.strip():
    codigos = [c.strip() for c in codigos_input.split("\n") if c.strip()]

    resultado = df.filter(pl.col("Product ID").is_in(codigos))

    if resultado.is_empty():
        st.warning("Nenhum código encontrado.")
    else:
        # --- Remover coluna ID se existir ---
        if "ID" in resultado.columns:
            resultado = resultado.drop("ID")

        # --- Definir colunas para exibir ---
        colunas_exibir = resultado.columns.copy()

        # Se a primeira coluna não for Product ID, renomeia como Pos ID
        if colunas_exibir[0] != "Product ID":
            resultado = resultado.rename({colunas_exibir[0]: "Pos ID"})
            # Reorganizar colunas
            colunas_exibir = ["Pos ID", "Product ID", "Description", "Price"]
            resultado = resultado.select(colunas_exibir)
        else:
            # Caso não tenha fantasma
            colunas_exibir = ["Product ID", "Description", "Price"]
            resultado = resultado.select(colunas_exibir)

        # Description em maiúsculo
        resultado = resultado.with_column(pl.col("Description").str.to_uppercase())

        # Price com $
        resultado = resultado.with_column(pl.col("Price").apply(manter_preco_com_dolar))

        # Converter para pandas para AgGrid
        resultado_pd = resultado.to_pandas()

        # --- AgGrid com zebra forçada ---
        gb = GridOptionsBuilder.from_dataframe(resultado_pd)
        gb.configure_grid_options(domLayout='normal')

        # Ajustar largura das colunas
        for col in resultado_pd.columns:
            if col == "Pos ID":
                gb.configure_column(col, width=80)
            elif col == "Product ID":
                gb.configure_column(col, width=150)
            elif col == "Description":
                gb.configure_column(col, width=300)
            elif col == "Price":
                gb.configure_column(col, width=120)

        # Zebra alternada
        gb.configure_grid_options(
            getRowStyle="""
            function(params) {
                if (params.node.rowIndex % 2 === 0) {
                    return {'background-color':'#f2f2f2'};
                } else {
                    return {'background-color':'white'};
                }
            }
            """
        )

        gridOptions = gb.build()

        AgGrid(
            resultado_pd,
            gridOptions=gridOptions,
            height=400,
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True
        )

        # --- Downloads ---
        csv_bytes = resultado_pd.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ CSV", csv_bytes, "resultado.csv", mime="text/csv")

        xlsx = BytesIO()
        resultado_pd.to_excel(xlsx, index=False, sheet_name="Resultado")
        st.download_button("⬇️ Excel", xlsx.getvalue(), "resultado.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
