import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import re
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Consulta de Códigos CRM", page_icon="📊", layout="wide")

# --- Cabeçalho ---
col1, col2 = st.columns([5,1])
with col1:
    st.markdown('<h1 style="color:#0A4C6A; margin:0;">🔎 Consulta de Códigos CRM</h1>', unsafe_allow_html=True)
with col2:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=140)
    except FileNotFoundError:
        pass

st.markdown("---")

# --- Carregar Excel ---
@st.cache_data
def carregar_excel(path="dados.xlsx"):
    return pd.read_excel(path, dtype=str)

df = carregar_excel("dados.xlsx")

# --- Detectar colunas ---
def achar_coluna(df_cols, candidatos):
    cols_low = [c.lower().strip() for c in df_cols]
    for cand in candidatos:
        if cand.lower() in cols_low:
            return df_cols[cols_low.index(cand.lower())]
    return None

prod_id_col = achar_coluna(df.columns, ["Product ID", "ProductID", "Code", "Código", "Codigo"])
desc_col    = achar_coluna(df.columns, ["Product Description", "Description", "Descrição"])
price_col   = achar_coluna(df.columns, ["Price", "Preco", "Preço", "Valor"])

if prod_id_col is None:
    st.error("Não encontrei a coluna de Product ID no arquivo.")
    st.stop()

# --- Entrada ---
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

codigos_input = st.text_area(
    "Digite os Product IDs:",
    value=st.session_state["input_area"],
    key="input_area",
    height=110
)

col_a, col_b, _ = st.columns([1,1,8])
with col_a:
    buscar = st.button("🔍 Buscar")
with col_b:
    if st.button("🆕 Nova Pesquisa"):
        st.session_state["input_area"] = ""
        st.experimental_rerun()

# --- Função para preço ---
def manter_preco_com_dolar(x):
    if x is None:
        return ""
    s = str(x).strip()
    if s == "" or s.lower() in ["nan", "none", "na", "n/a"]:
        return ""
    if s.startswith("$"):
        return s
    return f"${s}"

# --- Buscar ---
if buscar:
    entradas = re.split(r'[\n,;\s]+', codigos_input.strip())
    entradas = [e.strip() for e in entradas if e.strip() != ""]

    if len(entradas) == 0:
        st.warning("Digite ao menos um Product ID.")
    else:
        resultado = df[df[prod_id_col].isin(entradas)].copy()

        if resultado.empty:
            st.warning("Nenhum Product ID encontrado.")
        else:
            resultado.reset_index(drop=True, inplace=True)
            resultado.insert(0, "ID", range(1, len(resultado)+1))

            if desc_col:
                resultado[desc_col] = resultado[desc_col].fillna("").astype(str).str.upper()
            if price_col:
                resultado[price_col] = resultado[price_col].apply(manter_preco_com_dolar)

            colunas_exibir = ["ID", prod_id_col]
            if desc_col: colunas_exibir.append(desc_col)
            if price_col: colunas_exibir.append(price_col)

            resultado_final = resultado[colunas_exibir].copy()
            rename_map = {prod_id_col: "Product ID"}
            if desc_col: rename_map[desc_col] = "Product Description"
            if price_col: rename_map[price_col] = "Price"
            resultado_final.rename(columns=rename_map, inplace=True)

            # --- AgGrid com zebra ---
            gb = GridOptionsBuilder.from_dataframe(resultado_final)
            gb.configure_grid_options(domLayout='normal')
            gb.configure_column("ID", width=80)
            gridOptions = gb.build()

            AgGrid(
                resultado_final,
                gridOptions=gridOptions,
                height=400,
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False,
                theme="alpine"
            )

            # --- downloads ---
            csv_bytes = resultado_final.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ CSV", csv_bytes, "resultado.csv", mime="text/csv")

            xlsx = BytesIO()
            resultado_final.to_excel(xlsx, index=False, sheet_name="Resultado")
            st.download_button("⬇️ Excel", xlsx.getvalue(),
                               "resultado.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
