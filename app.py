import streamlit as st
import polars as pl

# ========================================
# Carregar Excel com Polars (muito mais rápido que Pandas)
# ========================================
@st.cache_data
def carregar_dados(caminho):
    return pl.read_excel(caminho)

df = carregar_dados("dados.xlsx")

# ========================================
# Layout da tela
# ========================================
st.title("Consulta de Códigos CRM")

# Caixa de input
codigos_input = st.text_area("Digite os códigos (um por linha):", height=150, key="input_area")

# Colunas para os botões
col1, col2 = st.columns([1, 1])

with col1:
    buscar = st.button("🔍 Buscar")
with col2:
    nova_pesquisa = st.button("🧹 Nova pesquisa")

# Resetar pesquisa
if nova_pesquisa:
    st.session_state.input_area = ""
    st.rerun()

# ========================================
# Lógica de busca
# ========================================
if buscar and codigos_input.strip():
    # Lista de PNs digitados
    codigos = [c.strip() for c in codigos_input.split("\n") if c.strip()]

    # Filtrar no Polars
    resultado = df.filter(pl.col("Product ID").is_in(codigos))

    if not resultado.is_empty():
        # Selecionar apenas as colunas desejadas
        resultado = resultado.select([
            pl.Series("ID", range(1, len(resultado) + 1)),
            pl.col("Product ID"),
            pl.col("Description"),
            pl.col("Price")
        ])

        # Converter para pandas apenas para exibir no Streamlit
        resultado_pd = resultado.to_pandas()

        # Estilo: cores alternadas + largura ajustada
        styled = (
            resultado_pd.style
            .hide(axis="index")  # oculta índice fantasma
            .set_table_styles([
                {"selector": "th.col0", "props": "width: 50px;"},
                {"selector": "th.col1", "props": "width: 150px;"},
                {"selector": "th.col2", "props": "width: 300px;"},
                {"selector": "th.col3", "props": "width: 120px;"},
            ])
            .apply(lambda x: ['background-color: #f9f9f9' if i % 2 == 0 else '' 
                              for i in range(len(x))], axis=0)
        )

        st.dataframe(styled, use_container_width=True)
    else:
        st.warning("Nenhum código encontrado.")
