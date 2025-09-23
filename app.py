import streamlit as st
import polars as pl
import pandas as pd
from PIL import Image
import base64
from io import BytesIO

# -----------------------------
# Função para carregar dados
# -----------------------------
@st.cache_data
def carregar_dados():
    df = pl.read_excel("dados.xlsx", sheet_name="Planilha1")
    return df

# -----------------------------
# Página
# -----------------------------
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

# CSS customizado
st.markdown(
    """
    <style>
    body {font-family: 'Calibri', sans-serif;}
    .stButton>button {height:40px; width:120px;}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Cabeçalho com logo e título
# -----------------------------
col1, col2 = st.columns([3,1])
with col1:
    st.markdown("## 🔍 Consulta de Códigos CRM")
with col2:
    img = Image.open("logo.png")
    st.markdown("<a href='https://irmen.com.br/' target='_blank'>", unsafe_allow_html=True)
    st.image(img, width=200)
    st.markdown("</a>", unsafe_allow_html=True)

st.write("---")

# -----------------------------
# Caixa de input e botão
# -----------------------------
codigos_input = st.text_area("Insira os códigos separados por vírgula ou espaço:", height=100)
botao = st.button("Pesquisar")

# -----------------------------
# Processamento da busca
# -----------------------------
if botao:
    if codigos_input.strip() == "":
        st.warning("Por favor, informe pelo menos 1 código!")
    else:
        codigos = [c.strip() for c in codigos_input.replace("\n",",").replace(" ",",").split(",") if c.strip()]

        df = carregar_dados()

        # Filtra apenas os códigos informados
        resultado = df.filter(pl.col("Product ID").is_in(codigos))

        # Colunas que queremos
        resultado = resultado.select(["Product ID", "Product Description", "Price"])

        # Product Description em maiúsculo
        resultado = resultado.with_column(
            pl.col("Product Description").str.to_uppercase()
        )

        resultado_pd = resultado.to_pandas()

        st.success(f"{len(resultado_pd)} código(s) encontrado(s)")

        # Mostra tabela
        st.dataframe(resultado_pd, use_container_width=True)

        # -----------------------------
        # Download em Excel
        # -----------------------------
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            resultado_pd.to_excel(writer, index=False, sheet_name="Resultados")
            writer.save()
            processed_data = output.getvalue()

        st.download_button(
            label="⬇️ Download Excel",
            data=processed_data,
            file_name="resultado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
