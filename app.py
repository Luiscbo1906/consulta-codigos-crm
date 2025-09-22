import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
import re

st.set_page_config(page_title="Consulta de Códigos CRM", page_icon="📊", layout="wide")

# --- carregar logo/título ---
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

# --- lê o Excel (tudo como string para evitar conversões indesejadas) ---
@st.cache_data
def carregar_excel(path="dados.xlsx"):
    return pd.read_excel(path, dtype=str)

df = carregar_excel("dados.xlsx")

# --- utilitários para identificar nomes das colunas (case-insensitive) ---
def achar_coluna(df_cols, candidatos):
    cols_low = [c.lower().strip() for c in df_cols]
    for cand in candidatos:
        if cand.lower() in cols_low:
            # retorna coluna original (com case original)
            return df_cols[cols_low.index(cand.lower())]
    return None

# candidatos (ajuste se seus cabeçalhos forem diferentes)
prod_id_col = achar_coluna(df.columns, ["Product ID", "ProductID", "Code", "Código", "Codigo"])
desc_col    = achar_coluna(df.columns, ["Product Description", "Description", "Product_Description", "Descrição"])
price_col   = achar_coluna(df.columns, ["Price", "Preco", "Preço", "Valor"])

if prod_id_col is None:
    st.error("Não encontrei a coluna de Product ID no arquivo. Verifique o cabeçalho (ex.: 'Product ID').")
    st.stop()

# --- input de códigos e botões ---
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

codigos_input = st.text_area(
    "Digite ou cole os Product IDs (separados por vírgula, espaço ou quebra de linha):",
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

# --- função para manter preço exatamente como está, só adicionando $ se não tiver ---
def manter_preco_com_dolar(x):
    if x is None:
        return ""
    s = str(x).strip()
    if s == "" or s.lower() in ["nan", "none", "na", "n/a"]:
        return ""
    if s.startswith("$"):
        return s
    return f"${s}"

# --- quando clicar em Buscar ---
if buscar:
    entradas = re.split(r'[\n,;\s]+', codigos_input.strip())
    entradas = [e.strip() for e in entradas if e.strip() != ""]

    if len(entradas) == 0:
        st.warning("Digite ao menos um Product ID.")
    else:
        # filtrar — fazemos comparações como string
        resultado = df[df[prod_id_col].isin(entradas)].copy()

        if resultado.shape[0] == 0:
            st.warning("Nenhum Product ID encontrado.")
        else:
            # resetar índice antigo (remove posição original do Excel)
            resultado.reset_index(drop=True, inplace=True)

            # criar ID sequencial começando em 1
            resultado.insert(0, "ID", range(1, len(resultado) + 1))

            # product description em maiúsculo (se existir)
            if desc_col:
                resultado[desc_col] = resultado[desc_col].fillna("").astype(str).str.upper()

            # price: manter exatamente como está + adicionar $ se não tiver
            if price_col:
                resultado[price_col] = resultado[price_col].apply(manter_preco_com_dolar)

            # selecionar e renomear colunas para exibição (colocar nomes amigáveis)
            colunas_exibir = ["ID", prod_id_col]
            if desc_col:
                colunas_exibir.append(desc_col)
            if price_col:
                colunas_exibir.append(price_col)

            resultado_final = resultado[colunas_exibir].copy()
            # renomear cabeçalhos para padrão visual
            rename_map = {prod_id_col: "Product ID"}
            if desc_col:
                rename_map[desc_col] = "Product Description"
            if price_col:
                rename_map[price_col] = "Price"
            resultado_final.rename(columns=rename_map, inplace=True)

            # --- Construir tabela HTML com zebra e larguras ---
            css = """
            <style>
            .my-table { border-collapse: collapse; width:100%; font-family: Arial, sans-serif; }
            .my-table th, .my-table td { border: 1px solid #e6e6e6; padding: 8px; vertical-align: middle; }
            .my-table th { background-color: #0A4C6A; color: white; text-align:left; }
            .my-table tr:nth-child(even) { background-color: #f9f9f9; }
            .my-table tr:hover { background-color: #f1f1f1; }
            /* larguras das colunas (ajuste conforme necessário) */
            .my-table td:nth-child(1), .my-table th:nth-child(1) { width:80px; text-align:center; }
            .my-table td:nth-child(2), .my-table th:nth-child(2) { width:150px; }
            .my-table td:nth-child(3), .my-table th:nth-child(3) { width:auto; }
            .my-table td:nth-child(4), .my-table th:nth-child(4) { width:120px; text-align:right; font-weight:600; }
            </style>
            """

            # gerar HTML (index=False -> sem índice pandas)
            tabela_html = resultado_final.to_html(index=False, classes="my-table", escape=False)

            st.success(f"🔹 {len(resultado_final)} registro(s) encontrado(s).")
            st.markdown(css + tabela_html, unsafe_allow_html=True)

            # --- downloads ---
            csv_bytes = resultado_final.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar resultado em CSV", csv_bytes, "resultado.csv", mime="text/csv")

            xlsx = BytesIO()
            resultado_final.to_excel(xlsx, index=False, sheet_name="Resultado")
            st.download_button("⬇️ Baixar resultado em Excel", xlsx.getvalue(),
                               "resultado.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
