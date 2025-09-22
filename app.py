import streamlit as st
import polars as pl
from io import BytesIO
from PIL import Image
import re

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
.stTextArea>div>div>textarea {
    border-radius: 5px;
    border: 1px solid #0A4C6A;
}
.stDataFrame {
    border: 1px solid #0A4C6A;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho centralizado verticalmente ---
try:
    logo = Image.open("logo.png")
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
            <div style="display:flex; align-items:center; justify-content:center; gap:20px;">
                <img src="logo.png" width="180" style="display:block;"/>
                <h1 style="color:#0A4C6A; margin:0;">🔎 Consulta de Códigos CRM</h1>
            </div>
        """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown('<h1 style="color:#0A4C6A; text-align:center;">🔎 Consulta de Códigos CRM</h1>', unsafe_allow_html=True)

st.markdown("---")

# --- Ler Excel com Polars ---
df = pl.read_excel("dados.xlsx")

# --- Campo de entrada ---
codigos_input = st.text_area(
    "Digite ou cole os Product IDs:",
    placeholder="Ex: 12345, 67890"
)

# --- Botão Buscar ---
if st.button("🔍 Buscar"):
    if codigos_input.strip() == "":
        st.warning("Digite ou cole pelo menos um Product ID.")
    else:
        lista_codigos = re.split(r'[\s,;]+', codigos_input.strip())
        lista_codigos = [c.strip() for c in lista_codigos if c.strip() != ""]

        resultado = df.filter(pl.col("Product ID").is_in(lista_codigos))

        if resultado.height > 0:
            st.success(f"🔹 {resultado.height} registro(s) encontrado(s).")
            st.dataframe(resultado.to_pandas())

            csv_bytes = resultado.write_csv()
            st.download_button(
                label="⬇️ Baixar resultado em CSV",
                data=csv_bytes,
                file_name="resultado.csv",
                mime="text/csv",
            )

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
