import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

st.markdown(
    "<h2 style='font-family: Arial;'>🔍 Consulta de Códigos CRM</h2>", 
    unsafe_allow_html=True
)

# ==============================
# Carregar dados com Pandas
# ==============================
@st.cache_data
def carregar_dados():
    return pd.read_excel("dados.xlsx", sheet_name="Planilha1")

df = carregar_dados()

# ==============================
# Caixa de busca + botão
# ==============================
col1, col2 = st.columns([6, 1])
with col1:
    input_area = st.text_area("Digite os códigos (um por linha):", height=120)
with col2:
    st.markdown("<div style='height:25px;'></div>", unsafe_allow_html=True)
    buscar = st.button("Pesquisar", use_container_width=True)

# ==============================
# Pesquisa
# ==============================
if buscar and input_area.strip():
    codigos_digitados = [c.strip() for c in input_area.splitlines() if c.strip()]
    resultado = df[df["Product ID"].isin(codigos_digitados)].copy()

    if resultado.empty:
        st.warning("Nenhum código encontrado.")
    else:
        # Colunas que queremos
        resultado = resultado[["Product ID", "Product Description", "Price"]]

        # Coluna Price com símbolo do dólar
        resultado["Price"] = "$" + resultado["Price"].astype(str)

        # Exibir resultado
        st.subheader("Resultado da Pesquisa")
        st.dataframe(resultado, use_container_width=True, height=400)

        # Botão download Excel
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
