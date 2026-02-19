import streamlit as st
import pandas as pd
import json
import os

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(page_title="Controle de Fornecedores", layout="wide")

ARQUIVO_DADOS = "dados_fornecedores.json"

# =========================
# FUNÇÕES DE PERSISTÊNCIA
# =========================
def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    else:
        return pd.DataFrame(columns=["Nome", "Último Vencimento", "Valor", "Status"])

def salvar_dados(df):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, ensure_ascii=False, indent=4)

# =========================
# INICIALIZAÇÃO
# =========================
if "df" not in st.session_state:
    st.session_state.df = carregar_dados()

df = st.session_state.df

# =========================
# LISTA DE MESES FIXA
# =========================
MESES = [
    "JAN/2026", "FEV/2026", "MAR/2026", "ABR/2026",
    "MAI/2026", "JUN/2026", "JUL/2026", "AGO/2026",
    "SET/2026", "OUT/2026", "NOV/2026", "DEZ/2026"
]

# =========================
# INTERFACE
# =========================
st.title("Controle Visual de Fornecedores")

col1, col2, col3, col4 = st.columns(4)

with col1:
    nome = st.text_input("Nome")

with col2:
    ultimo_vencimento = st.selectbox("Último Vencimento", MESES)

with col3:
    valor = st.number_input("Valor", min_value=0.0, step=0.01, format="%.2f")

with col4:
    status = st.selectbox("Status", ["CONCLUÍDO", "EM ANDAMENTO"])

if st.button("Adicionar"):
    if nome.strip() != "":
        novo = pd.DataFrame([{
            "Nome": nome,
            "Último Vencimento": ultimo_vencimento,
            "Valor": valor,
            "Status": status
        }])

        st.session_state.df = pd.concat([st.session_state.df, novo], ignore_index=True)
        salvar_dados(st.session_state.df)
        st.success("Fornecedor adicionado com sucesso!")

# =========================
# VISUALIZAÇÃO COM REGRA DE COR
# =========================
st.markdown("---")

def colorir_status(val):
    if val == "CONCLUÍDO":
        return "background-color: #d4edda; color: #155724; font-weight: bold;"
    elif val == "EM ANDAMENTO":
        return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
    return ""

if not st.session_state.df.empty:
    st.dataframe(
        st.session_state.df.style.map(colorir_status, subset=["Status"]),
        use_container_width=True
    )
else:
    st.info("Nenhum fornecedor cadastrado ainda.")
