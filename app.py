import streamlit as st
import polars as pl
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import io

# ==============================
# Configuração da página
# ==============================
st.set_page_config(page_title="Consulta de Códigos CRM", layout="wide")

st.markdown(
    """
    <h2 style="display: flex; align-items: center; font-family: Arial; margin-bottom: 20px;">
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
        # Configuração AgGrid
        # ==============================
        gb = GridOptionsBuilder.from_dataframe(resultado_pd)
        gb.configure_default_column(
            resizable=True, filter=True, sortable=True, wrapText=True, autoHeight=True
        )
        gb.configure_grid_options(
            getRowStyle="""function(params) {
                if (params.node.rowIndex % 2 === 0) {
                    return { 'backgroundColor': '#f9f9f9' }
                }
                return { 'backgroundColor': 'white' }
            }"""
        )
        gridOptions = gb.build()

        st.subheader("Resultado da Pesquisa")
        AgGrid(
            resultado_pd,
            gridOptions=gridOptions,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=True,
            height=400,
            theme="balham",
        )

        # ==============================
        # Botão para download em Excel formatado
        # ==============================
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            resultado_pd.to_excel(writer, index=False, sheet_name="Resultados")
            workbook  = writer.book
            worksheet = writer.sheets["Resultados"]

            # Formato do cabeçalho
            header_format = workbook.add_format({
                "bold": True,
                "text_wrap": True,
                "valign": "center",
                "fg_color": "#D9D9D9",
                "border": 1
            })

            # Aplica estilo no cabeçalho
            for col_num, value in enumerate(resultado_pd.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, len(value) + 15)

            # Ajusta largura conforme conteúdo
            for i, col in enumerate(resultado_pd.columns):
                col_width = max(resultado_pd[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, col_width)

        output.seek(0)

        st.download_button(
            label="📥 Baixar resultado em Excel",
            data=output,
            file_name="resultado_codigos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
