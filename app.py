import streamlit as st
import pandas as pd
import io

# ==============================
# Configuração da página
# ==============================
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

# ==============================
# Cabeçalho com título e logo
# ==============================
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown(
        "<h2 style='font-family: Calibri; margin-bottom: 0;'>🔍 Consulta de Códigos CRM</h2>", 
        unsafe_allow_html=True
    )
with col2:
    # Logo clicável
    st.markdown(
        f"<a href='https://irmen.com.br/' target='_blank'>"
        f"<img src='logo.png' width='200'></a>", 
        unsafe_allow_html=True
    )

# ==============================
# Carregar dados
# ==============================
@st.cache_data
def carregar_dados():
    return pd.read_excel("dados.xlsx", sheet_name="Planilha1")

df = carregar_dados()

# ==============================
# Caixa de busca
# ==============================
st.markdown("<div style='font-family: Calibri;'>Digite os códigos (um por linha):</div>", unsafe_allow_html=True)
input_area = st.text_area("", height=140, key="input_area")

st.markdown("<br>", unsafe_allow_html=True)
buscar = st.button("Pesquisar", key="buscar_button")

if buscar:
    if not input_area.strip():
        st.warning("Por favor, informe pelo menos 1 código para pesquisar.")
    else:
        codigos_digitados = [c.strip() for c in input_area.splitlines() if c.strip()]
        resultado = df[df["Product ID"].isin(codigos_digitados)].copy()

        if resultado.empty:
            st.warning("Nenhum código encontrado.")
        else:
            # Selecionar apenas as 3 colunas desejadas
            resultado = resultado[["Product ID", "Product Description", "Price"]]

            # Product Description em maiúsculo
            resultado["Product Description"] = resultado["Product Description"].str.upper()

            # Preço com símbolo do dólar
            resultado["Price"] = "$" + resultado["Price"].astype(str)

            # ==============================
            # Mensagem de quantos códigos encontrados
            # ==============================
            st.success(f"Foram encontrados {len(resultado)} código(s).")

            # ==============================
            # Exibir resultado com linhas zebradas
            # ==============================
            st.markdown(
                resultado.style
                .set_table_styles([
                    {"selector": "thead", "props": [("background-color", "#4CAF50"), 
                                                    ("color", "white"),
                                                    ("font-family", "Calibri")]},
                    {"selector": "tbody tr:nth-child(even)", "props": [("background-color", "#f2f2f2")]},
                    {"selector": "tbody tr:nth-child(odd)", "props": [("background-color", "white")]}
                ])
                .set_properties(**{"font-family": "Calibri"})
                .hide_index()
                .to_html(), unsafe_allow_html=True
            )

            # ==============================
            # Download Excel
            # ==============================
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                resultado.to_excel(writer, index=False, sheet_name="Resultados")
            output.seek(0)

            st.download_button(
                label="📥 Baixar resultado em Excel",
                data=output,
                file_name="resultado_codigos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
