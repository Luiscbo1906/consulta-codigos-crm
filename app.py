import streamlit as st
import pandas as pd
from io import BytesIO
import re
from PIL import Image

# --- Configurações da página ---
st.set_page_config(
    page_title="Consulta de Códigos CRM",
    page_icon="📊",
    layout="wide"
)

# --- Cabeçalho com logo maior e título centralizado ---
try:
    logo = Image.open("logo.png")
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.image(logo, width=200)  # tamanho maior do logo
    
    with col2:
        # Título centralizado verticalmente
        st.markdown("""
            <div style="display: flex; align-items: center; height: 100%;">
                <h1 style="color: #0A4C6A;">🔎 Consulta de Códigos CRM</h1>
            </div>
        """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown('<h1 style="color: #0A4C6A;">🔎 Consulta de Códigos CRM</h1>', unsafe_allow_html=True)

st.markdown("---")  # linha horizontal

# --- Ler Excel embutido ---
df = pd.read_excel("dados.xlsx")
# st.write("✅ Arquivo carregado automaticamente!")  # mensagem ocultada

# --- Campo de entrada ---
codigos_input = st.text_area(
    "Digite ou cole os Product IDs (de qualquer fonte, separados por vírgula, espaço ou tabulação):"
)

# --- Botão Buscar ---
if st.button("🔍 Buscar"):
    if codigos_input.strip() == "":
        st.warning("Digite ou cole pelo menos um Product ID.")
    else:
        # Separadores múltiplos
        lista_codigos = re.split(r'[\s,;]+', codigos_input.strip())
        lista_codigos = [c.strip() for c in lista_codigos if c.strip() != ""]

        # Filtrar dados
        df['Product ID'] = df['Product ID'].astype(str)
        codigos_set = set(lista_codigos)
        resultado = df[df['Product ID'].isin(codigos_set)]

        if not resultado.empty:
            st.success(f"🔹 {len(resultado)} registro(s) encontrado(s).")
            st.dataframe(resultado)

            # --- Botão CSV ---
            csv = resultado.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Baixar resultado em CSV",
                data=csv,
                file_name="resultado.csv",
                mime="text/csv",
            )

            # --- Botão Excel ---
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                resultado.to_excel(writer, index=False, sheet_name="Resultado")
            st.download_button(
                label="⬇️ Baixar resultado em Excel",
                data=output.getvalue(),
                file_name="resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.warning("Nenhum Product ID encontrado.")
