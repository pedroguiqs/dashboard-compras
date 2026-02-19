import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Controle de Fornecedores", layout="wide")

ARQUIVO_DADOS = "dados_fornecedores.json"

# =========================
# FORNECEDORES PADRÃO
# =========================
FORNECEDORES_PADRAO = [
    "E-SALES",
    "PAES E DOCES JARDIM THELMA",
    "PALLEFORT COMERCIO",
    "BRASIL SERVIÇOS",
    "EZ TOOLS",
    "NISSEYS",
    "FUSION",
    "BUONNY",
    "KM STAFF",
    "PANIFICADORA MM",
    "NUNES TRANSPORTES",
    "THEODORO GÁS",
    "BERKLEY"
]

# =========================
# MESES
# =========================
MESES = [
    "JAN", "FEV", "MAR", "ABR",
    "MAI", "JUN", "JUL", "AGO",
    "SET", "OUT", "NOV", "DEZ"
]

# =========================
# FUNÇÕES DE SALVAMENTO
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
# FORMULÁRIO
# =========================
st.title("Controle de Fornecedores")

col1, col2, col3, col4 = st.columns(4)

with col1:
    nome = st.selectbox("Nome", FORNECEDORES_PADRAO)

with col2:
    ultimo_vencimento = st.selectbox("Último Vencimento", MESES)

with col3:
    valor = st.number_input("Valor", min_value=0.0, step=0.01, format="%.2f")

with col4:
    status = st.selectbox("Status", ["CONCLUÍDO", "EM ANDAMENTO"])

if st.button("Adicionar"):
    novo = pd.DataFrame([{
        "Nome": nome,
        "Último Vencimento": ultimo_vencimento,
        "Valor": valor,
        "Status": status
    }])

    st.session_state.df = pd.concat([st.session_state.df, novo], ignore_index=True)
    salvar_dados(st.session_state.df)
    st.rerun()

# =========================
# VISÃO RÁPIDA (CARDS)
# =========================
st.markdown("---")
st.subheader("Visão Rápida")

if not df.empty:

    colunas = st.columns(4)

    for i, row in df.iterrows():

        coluna = colunas[i % 4]

        if row["Status"] == "CONCLUÍDO":
            cor = "#2ea043"
            texto = "white"
        else:
            cor = "#fbbc04"
            texto = "black"

        coluna.markdown(
            f"""
            <div style="
                background-color:{cor};
                padding:25px;
                border-radius:20px;
                margin-bottom:20px;
                font-weight:600;
                color:{texto};
                font-size:18px;">
                
                <div style="font-size:20px; font-weight:700;">
                    {row['Nome']}
                </div>
                <br>
                Último Vencimento: {row['Último Vencimento']}
                <br><br>
                Valor: R$ {row['Valor']:,.2f}
                <br><br>
                {row['Status']}
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.info("Nenhum fornecedor cadastrado ainda.")
