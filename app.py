import streamlit as st
import polars as pl
import pandas as pd
import io

# ==============================
# Configuração da página
# ==============================
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

st.markdown(
    """
    <h2 style="font-family: Arial; margin-bottom: 20px;">
        🔍 Consulta de Códigos CRM
    </h2>
    """,
    unsafe_allow_html=True,
)

# ==============================
# Carregar dados
# ==============================
@st.cache_data
def carregar_dados():
    return pl.read_excel("dados.xlsx", sheet_name="Planilha1")

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
# Lógica de pesquisa
# ==============================
if buscar and input_area.strip():
    codigos_digitados = [c.strip() for c in input_area.splitlines() if c.strip()]

    resultado = df.filter(pl.col("Product ID").is_in(codigos_digitados))

    if resultado.is_empty():
        st.warning("Nenhum código encontrado.")
    else:
        # Seleciona apenas as 3 colunas certas
        resultado = resultado.select(["Product ID", "Product Description", "Price"])

        # Adiciona símbolo do dólar sem alterar valor original
        resultado = resultado.with_columns(
            (pl.lit("$") + pl.col("Price").cast(pl.Utf8)).alias("Price")
        )

        # Converte para Pandas
        resultado_pd = resultado.to_pandas()

        # ==============================
        # Exibição na tabela
        # ==============================
        st.subheader("Resultado da Pesquisa")
        st.dataframe(resultado_pd, use_container_width=True, height=400)

        # ==============================
        # Botão para download em Excel formatado (openpyxl)
        # ==============================
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            resultado_pd.to_excel(writer, index=False, sheet_name="Resultados")
            worksheet = writer.sheets["Resultados"]

            # Ajusta largura das colunas automaticamente
            for col in worksheet.columns:
                max_length = 0
                col_letter = col[0].column_letter
                for cell in col:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = max_length + 2
                worksheet.column_dimensions[col_letter].width = adjusted_width

        output.seek(0)

        st.download_button(
            label="📥 Baixar resultado em Excel",
            data=output,
            file_name="resultado_codigos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
