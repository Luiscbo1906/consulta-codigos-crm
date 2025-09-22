import streamlit as st
import pandas as pd
from io import BytesIO
import re

# Título da aba do navegador
st.set_page_config(
    page_title="Consulta de Códigos CRM",
    layout="wide"
)

st.title("🔎 Consulta de Códigos CRM")

# --- Ler o Excel embutido ---
df = pd.read_excel("dados.xlsx")
st.write("✅ Arquivo carregado automaticamente!")
st.write("Visualização inicial da tabela:")
st.dataframe(df.head())

# Entrada de Product IDs
codigos_input = st.text_area(
    "Digite ou cole os Product IDs (de qualquer fonte, separados por vírgula, espaço ou tabulação):"
)

# Botão para buscar
if st.button("🔍 Buscar"):
    if codigos_input.strip() == "":
        st.warning("Digite ou cole pelo menos um Product ID.")
    else:
        # Substituir tabs, quebras de linha e espaços por vírgula
        lista_codigos = re.split(r'[\s,;]+', codigos_input.strip())
        lista_codigos = [c.strip() for c in lista_codigos if c.strip() != ""]

        # Transformar coluna em string e filtrar
        df['Product ID'] = df['Product ID'].astype(str)
        codigos_set = set(lista_codigos)
        resultado = df[df['Product ID'].isin(codigos_set)]

        if not resultado.empty:
            st.success(f"🔹 {len(resultado)} registro(s) encontrado(s).")
            st.dataframe(resultado)

            # --- Botão para baixar CSV ---
            csv = resultado.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Baixar resultado em CSV",
                data=csv,
                file_name="resultado.csv",
                mime="text/csv",
            )

            # --- Botão para baixar Excel ---
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

