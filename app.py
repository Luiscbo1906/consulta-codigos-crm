import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import re

# --- Configurações da página ---
st.set_page_config(
    page_title="Consulta de Códigos CRM",
    page_icon="📊",
    layout="wide"
)

# --- Inicializar session_state ---
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

# --- Estilo profissional ---
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
    font-family: Arial, sans-serif;
}
.stButton>button {
    background-color: #0A4C6A;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    height: 40px;
    min-width: 140px;
    white-space: nowrap;
}
.stTextArea>div>div>textarea {
    border-radius: 5px;
    border: 1px solid #0A4C6A;
    height: 120px !important;
}
.stDataFrame > div[data-testid="stDataFrame"] table {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho ---
col1, col2 = st.columns([5,1])
with col1:
    st.markdown('<h1 style="color:#0A4C6A; margin:0;">🔎 Consulta de Códigos CRM</h1>', unsafe_allow_html=True)
with col2:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=180)
    except FileNotFoundError:
        pass

st.markdown("---")

# --- Ler Excel com Pandas ---
df = pd.read_excel("dados.xlsx", dtype=str)  # lê tudo como string

# --- Função para Nova Pesquisa ---
def limpar_input():
    st.session_state["input_area"] = ""

# --- Campo de input ---
codigos_input = st.text_area(
    "Digite ou cole os Product IDs (separados por vírgula, espaço ou tabulação):",
    placeholder="Ex: 12345, 67890",
    key="input_area",
)

# --- Botões lado a lado ---
btn_col1, btn_col2, _ = st.columns([1,1,8])
with btn_col1:
    buscar = st.button("🔍 Buscar")
with btn_col2:
    nova_pesquisa = st.button("🆕 Nova Pesquisa", on_click=limpar_input)

# --- Função para adicionar $ mantendo valor original ---
def add_dolar(x):
    if x and x.strip() != "":
        return f"${x.strip()}"
    else:
        return ""

# --- Ação Buscar ---
if buscar:
    if codigos_input.strip() == "":
        st.warning("Digite ou cole pelo menos um Product ID.")
    else:
        # separar os códigos por vírgula, espaço ou tab
        lista_codigos = re.split(r'[\s,;]+', codigos_input.strip())
        lista_codigos = [c.strip() for c in lista_codigos if c.strip() != ""]

        # Filtrar na planilha
        resultado_pd = df[df["Product ID"].isin(lista_codigos)].copy()

        if len(resultado_pd) > 0:
            # Product Description em maiúsculo
            if "Product Description" in resultado_pd.columns:
                resultado_pd["Product Description"] = resultado_pd["Product Description"].str.upper()

            # Price com $
            if "Price" in resultado_pd.columns:
                resultado_pd["Price"] = resultado_pd["Price"].apply(add_dolar)

            # Adicionar coluna ID sequencial no início
            resultado_pd.insert(0, "ID", range(1, len(resultado_pd)+1))

            st.success(f"🔹 {len(resultado_pd)} registro(s) encontrado(s).")

            # Exibir DataFrame sem índice do Pandas
            st.dataframe(resultado_pd.style.hide_index(), use_container_width=True)

            # --- Botão CSV ---
            csv_bytes = resultado_pd.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Baixar resultado em CSV",
                data=csv_bytes,
                file_name="resultado.csv",
                mime="text/csv",
            )

            # --- Botão Excel ---
            output = BytesIO()
            resultado_pd.to_excel(output, index=False, sheet_name="Resultado")
            st.download_button(
                label="⬇️ Baixar resultado em Excel",
                data=output.getvalue(),
                file_name="resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("Nenhum Product ID encontrado.")
