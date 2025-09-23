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
    st.markdown("<h2 style='font-family: Calibri;'>🔍 Consulta de Códigos CRM</h2>", unsafe_allow_html=True)
with col2:
    st.image("logo.png", width=200)

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
input_area = st.text_area("Digite os códigos (um por linha):", height=120)
buscar = st.button("Pesquisar")

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
            # Exibir resultado com linhas zebradas, cabeçalho fixo e scroll
            # ==============================
            def render_table_scroll_fixed_header(df, max_rows=20):
                row_height = 40  # px por linha
                table_height = min(len(df), max_rows) * row_height
                html = f"""
                <div style='overflow-y: auto; max-height: {table_height}px; border: 1px solid #ccc;'>
                    <table style='border-collapse: collapse; font-family: Calibri; width: 100%;'>
                        <thead style='position: sticky; top: 0; background-color: #4CAF50; color: white; z-index: 1;'>
                            <tr>"""
                for col in df.columns:
                    html += f"<th style='padding: 8px; text-align: left; border-bottom: 1px solid #ccc;'>{col}</th>"
                html += "</tr></thead><tbody>"
                
                for i, row in df.iterrows():
                    bg = "#f9f9f9" if i % 2 == 0 else "#ffffff"
                    html += f"<tr style='background-color: {bg};'>"
                    for val in row:
                        html += f"<td style='padding: 8px; border-bottom: 1px solid #eee;'>{val}</td>"
                    html += "</tr>"
                html += "</tbody></table></div>"
                return html

            st.markdown(render_table_scroll_fixed_header(resultado), unsafe_allow_html=True)

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
