import streamlit as st
import polars as pl
from io import BytesIO
from PIL import Image

# --- Configurações da página ---
st.set_page_config(
    page_title="Consulta de Códigos CRM",
    page_icon="📊",
    layout="wide"
)

# --- Estilo customizado tipo CRM ---
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
.stButton>button {
    background-color: #0A4C6A;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    height: 40px;
}
.stDataFrame {
    border: 1px solid #0A4C6A;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho com logo opcional e título ---
try:
    logo = Image.open("logo.png")
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(logo, width=200)
    with col2:
        st.markdown("""
            <div style="display: flex; align-items: center; height: 100%;">
                <h1 style="color: #0A4C6A;">🔎 Consulta de Códigos CRM</h1>
            </div>
        """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown('<h1 style="color: #0A4C6A;">🔎 Consulta de Códigos CRM</h1>', unsafe_allow_html=True)

st.markdown("---")

# --- Ler Excel com Polars ---
df = pl.read_excel("dados.xlsx")
all_ids = df["Product ID"].to_list()

# --- Campo de entrada com autocomplete múltiplo ---
selected_ids = st.multiselect(
    "Digite ou selecione os Product IDs:",
    options=all_ids,
    help="Você pode digitar ou selecionar múltiplos IDs"
)

# --- Botão Buscar ---
if st.button("🔍 Buscar"):
    if not selected_ids:
        st.warning("Selecione ou digite pelo menos um Product ID.")
    else:
        # Filtrar com Polars
        resultado = df.filter(pl.col("Product ID").is_in(selected_ids))

        if resultado.height > 0:
            st.success(f"🔹 {resultado.height} registro(s) encontrado(s).")
            st.dataframe(resultado.to_pandas())

            # --- Botão CSV ---
            csv_bytes = resultado.write_csv()
            st.download_button(
                label="⬇️ Baixar resultado em CSV",
                data=csv_bytes,
                file_name="resultado.csv",
                mime="text/csv",
            )

            # --- Botão Excel ---
            output = BytesIO()
            resultado.to_pandas().to_excel(output, index=False, sheet_name="Resultado")
            st.download_button(
                label="⬇️ Baixar resultado em Excel",
                data=output.getvalue(),
                file_name="resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("Nenhum Product ID encontrado.")
