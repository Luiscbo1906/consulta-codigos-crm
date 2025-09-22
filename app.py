import streamlit as st
import polars as pl
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO
from PIL import Image

# --- Configuração da página ---
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

# --- Cabeçalho com título e logo ---
logo_path = "logo.png"  # substitua pelo caminho correto do logo
try:
    logo = Image.open(logo_path)
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("## 🔍 Consulta de Códigos CRM")
    with col2:
        st.image(logo, width=180)
except FileNotFoundError:
    st.markdown("## 🔍 Consulta de Códigos CRM")  # fallback se não achar o logo

# --- Carregar Excel ---
@st.cache_data
def carregar_dados(caminho="dados.xlsx"):
    df = pl.read_excel(caminho)
    df = df.rename({
        df.columns[0]: "Product_ID",
        df.columns[1]: "Product_Description",
        df.columns[2]: "Price"
    })
    return pl.DataFrame(df)

df = carregar_dados()

# --- Input de códigos ---
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

codigos_input = st.text_area(
    "Digite os códigos (um por linha):",
    value=st.session_state["input_area"],
    height=150
)

# Botões lado a lado
col1, col2 = st.columns([1, 1])
with col1:
    buscar = st.button("🔍 Buscar")
with col2:
    nova = st.button("🧹 Nova pesquisa")
    if nova:
        st.session_state.input_area = ""
        st.experimental_rerun()

# --- Função para manter preço com $
def manter_preco_com_dolar(x):
    if x is None:
        return ""
    s = str(x).strip()
    if s == "" or s.lower() in ["nan", "none", "na", "n/a"]:
        return ""
    if s.startswith("$"):
        return s
    return f"${s}"

# --- Busca ---
if buscar and codigos_input.strip():
    codigos = [c.strip() for c in codigos_input.split("\n") if c.strip()]
    resultado = df.filter(pl.col("Product_ID").is_in(codigos))

    if resultado.is_empty():
        st.warning("Nenhum código encontrado.")
    else:
        # Selecionar apenas as 3 colunas
        resultado = resultado.select(["Product_ID", "Product_Description", "Price"])

        # Converter Description para maiúsculo
        resultado = resultado.with_columns([
            pl.col("Product_Description").cast(pl.Utf8).str.to_uppercase(),
            pl.col("Price").cast(pl.Utf8).apply(manter_preco_com_dolar)
        ])

        # Converter para pandas e resetar índice
        resultado_pd = resultado.to_pandas()
        resultado_pd.reset_index(drop=True, inplace=True)

        # --- AgGrid ---
        gb = GridOptionsBuilder.from_dataframe(resultado_pd)
        gb.configure_grid_options(domLayout='normal', hideIndex=True)

        # Ajustar largura das colunas
        gb.configure_column("Product_ID", width=150)
        gb.configure_column("Product_Description", width=350)
        gb.configure_column("Price", width=120)

        # Zebra alternada
        gb.configure_grid_options(
            getRowStyle="""
            function(params) {
                if (params.node.rowIndex % 2 === 0) {
                    return {'background-color':'#f9f9f9'};
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
        st.download_button(
            "⬇️ Excel",
            xlsx.getvalue(),
            "resultado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
