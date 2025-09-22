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

# --- Estilo tipo CRM ---
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

# --- Cabeçalho: título à esquerda e logo à direita ---
col1, col2 = st.columns([5, 1])
with col1:
    st.markdown('<h1 style="color:#0A4C6A; margin:0;">🔎 Consulta de Códigos CRM</h1>', unsafe_allow_html=True)
with col2:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=180)
    except FileNotFoundError:
        pass  # ignora se não houver logo

st.markdown("---")

# --- Ler Excel com Polars ---
df = pl.read_excel("dados.xlsx")

# --- Campo de entrada ---
codigos_input = st.text_area(
    "Digite ou cole os Product IDs (separados por vírgula, espaço ou tabulação):",
    placeholder="Ex: 12345, 67890"
)

# --- Botão Buscar ---
if st.button("🔍 Buscar"):
    if codigos_input.strip() == "":
        st.warning("Digite ou cole pelo menos um Product ID.")
    else:
        # Separar múltiplos IDs
        lista_codigos = re.split(r'[\s,;]+', codigos_input.strip())
        lista_codigos = [c.strip() for c in lista_codigos if c.strip() != ""]

        # Filtrar com Polars
        resultado = df.filter(pl.col("Product ID").is_in(lista_codigos))

        if resultado.height > 0:
            # Coluna "Product Description" em maiúsculo
            if "Product Description" in resultado.columns:
                resultado = resultado.with_columns([
                    pl.col("Product Description").str.to_uppercase().alias("Product Description")
                ])

            # Coluna "Price" com símbolo de dólar
            if "Price" in resultado.columns:
                resultado = resultado.with_columns([
                    pl.col("Price").apply(lambda x: f"${x:,.2f}" if x is not None else "").alias("Price")
                ])

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
