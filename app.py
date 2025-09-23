import streamlit as st
import polars as pl
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO
from PIL import Image

# --- Configuração da página ---
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

# --- Cabeçalho com título e logo ---
logo_path = "logo.png"  # Substitua pelo caminho correto do logo
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(
        "<h1 style='text-align: left; color: #0a3d62;'>🔍 Consulta de Códigos CRM</h1>",
        unsafe_allow_html=True
    )
with col2:
    try:
        logo = Image.open(logo_path)
        st.image(logo, width=120)
    except FileNotFoundError:
        pass

st.markdown("---")

# --- Carregar Excel ---
@st.cache_data
def carregar_dados(caminho="dados.xlsx"):
    df = pl.read_excel(caminho)
    df = df.rename({
        df.columns[0]: "Product_ID",
        df.columns[1]: "Product_Description",
        df.columns[2]: "Price"
    })
    return df

df = carregar_dados()

# --- Input de códigos ---
if "input_area" not in st.session_state:
    st.session_state.input_area = ""

st.markdown(
    "<p style='font-size:16px; font-weight:600;'>Digite os códigos (um por linha):</p>",
    unsafe_allow_html=True
)

codigos_input = st.text_area(
    "",
    value=st.session_state.input_area,
    height=150,
    placeholder="Exemplo:\n12345\n67890"
)

# --- Botão Buscar (tamanho normal) ---
buscar = st.button("🔎 Buscar")

# --- Função para manter preço com $
def manter_preco_com_dolar(x):
    if x is None or str(x).strip() == "":
        return ""
    s = str(x).strip()
    if s.startswith("$"):
        return s
    return f"${s}"

# --- Busca ---
if buscar and codigos_input.strip():
    codigos = [c.strip() for c in codigos_input.split("\n") if c.strip()]
    resultado = df.filter(pl.col("Product_ID").is_in(codigos))

    if resultado.is_empty():
        st.warning("⚠️ Nenhum código encontrado.")
    else:
        # Selecionar apenas as 3 colunas
        resultado = resultado.select(["Product_ID", "Product_Description", "Price"])

        # Converter para pandas
        resultado_pd = resultado.to_pandas()

        # Description em maiúsculo
        resultado_pd["Product_Description"] = resultado_pd["Product_Description"].astype(str).str.upper()

        # Price com $
        resultado_pd["Price"] = resultado_pd["Price"].apply(manter_preco_com_dolar)

        # Resetar índice
        resultado_pd.reset_index(drop=True, inplace=True)

        # --- AgGrid com formatação ---
        gb = GridOptionsBuilder.from_dataframe(resultado_pd)
        gb.configure_grid_options(domLayout='normal', hideIndex=True)

        # Ajustar largura das colunas
        gb.configure_column("Product_ID", header_name="Código", width=150)
        gb.configure_column("Product_Description", header_name="Descrição", width=400)
        gb.configure_column("Price", header_name="Preço (USD)", width=150)

        # Ativar linhas zebradas
        gb.configure_grid_options(
            rowStyle={"backgroundColor": "#f9f9f9"},
            getRowStyle="""function(params) {
                                if (params.node.rowIndex % 2 === 0) {
                                    return { backgroundColor: '#ffffff' }
                                }
                                return { backgroundColor: '#f2f6fc' }
                            }"""
        )

        gridOptions = gb.build()

        st.markdown(f"### ✅ {len(resultado_pd)} resultados encontrados")

        AgGrid(
            resultado_pd,
            gridOptions=gridOptions,
            height=400,
            fit_columns_on_grid_load=True,
            theme="alpine"
        )

        # --- Downloads lado a lado ---
        st.markdown("### 📥 Exportar resultados")
        colA, colB = st.columns(2)

        with colA:
            csv_bytes = resultado_pd.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar CSV", csv_bytes, "resultado.csv", mime="text/csv")

        with colB:
            xlsx = BytesIO()
            resultado_pd.to_excel(xlsx, index=False, sheet_name="Resultado")
            st.download_button(
                "⬇️ Baixar Excel",
                xlsx.getvalue(),
                "resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
