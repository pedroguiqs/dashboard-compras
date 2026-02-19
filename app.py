import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Controle de Faturas", layout="wide")

ARQUIVO = "dados_faturas.csv"

# =========================
# FORNECEDORES
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
    "JAN", "FEV", "MAR", "ABR", "MAI", "JUN",
    "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"
]

# =========================
# ESTRUTURA PADRÃO
# =========================
COLUNAS_PADRAO = [
    "Fornecedor",
    "Ultimo_Vencimento",
    "Status"
]

# =========================
# FUNÇÃO PARA SALVAR
# =========================
def salvar_csv(df):
    df.to_csv(ARQUIVO, index=False)

# =========================
# CARREGAR DADOS
# =========================
if "dados" not in st.session_state:

    if os.path.exists(ARQUIVO):
        st.session_state.dados = pd.read_csv(ARQUIVO)
    else:
        st.session_state.dados = pd.DataFrame(columns=COLUNAS_PADRAO)

if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = False

if "editar_index" not in st.session_state:
    st.session_state.editar_index = None

# =========================
# TÍTULO
# =========================
st.title("🧾 Controle de Faturas")

# =========================
# BOTÃO NOVO REGISTRO
# =========================
if not st.session_state.mostrar_form:
    if st.button("Novo Registro"):
        st.session_state.mostrar_form = True

# =========================
# FORMULÁRIO
# =========================
if st.session_state.mostrar_form:

    with st.form("form_fatura", clear_on_submit=True):

        fornecedor = st.selectbox("Fornecedor", FORNECEDORES_PADRAO)
        vencimento = st.selectbox("Último Vencimento", MESES)
        status = st.selectbox("Status", ["CONCLUÍDO", "EM ANDAMENTO"])

        salvar = st.form_submit_button("Salvar")

        if salvar:

            novo = {
                "Fornecedor": fornecedor,
                "Ultimo_Vencimento": vencimento,
                "Status": status
            }

            if st.session_state.editar_index is not None:
                st.session_state.dados.loc[
                    st.session_state.editar_index
                ] = novo
                st.session_state.editar_index = None

            else:
                filtro = (
                    st.session_state.dados["Fornecedor"] == fornecedor
                )

                if filtro.any():
                    st.session_state.dados.loc[filtro, :] = novo
                else:
                    st.session_state.dados = pd.concat(
                        [st.session_state.dados, pd.DataFrame([novo])],
                        ignore_index=True
                    )

            salvar_csv(st.session_state.dados)

            st.session_state.mostrar_form = False
            st.rerun()

st.divider()

# =========================
# CARDS
# =========================
df = st.session_state.dados

if not df.empty:

    st.subheader("Visão Rápida")

    colunas = st.columns(4)

    for idx, row in df.iterrows():

        coluna = colunas[idx % 4]

        if row["Status"] == "CONCLUÍDO":
            cor = "#28a745"
            texto_cor = "white"
        else:
            cor = "#ffc107"
            texto_cor = "black"

        coluna.markdown(
            f"""
            <div style="
                background-color:{cor};
                padding:18px;
                border-radius:12px;
                margin-bottom:15px;
                font-weight:600;
                color:{texto_cor};
                font-size:16px;">
                {row['Fornecedor']}<br><br>
                Último Vencimento: {row['Ultimo_Vencimento']}<br><br>
                {row['Status']}
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# =========================
# LISTA
# =========================
st.subheader("Lista Completa")

if not df.empty:

    for i, row in df.iterrows():

        col1, col2, col3 = st.columns([6,1,1])

        with col1:
            st.write(
                f"**{row['Fornecedor']}** | "
                f"Vencimento: {row['Ultimo_Vencimento']} | "
                f"{row['Status']}"
            )

        with col2:
            if st.button("✏️", key=f"edit_{i}"):
                st.session_state.editar_index = i
                st.session_state.mostrar_form = True

        with col3:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.dados = (
                    st.session_state.dados
                    .drop(i)
                    .reset_index(drop=True)
                )
                salvar_csv(st.session_state.dados)
                st.rerun()
else:
    st.info("Nenhum registro cadastrado ainda.")
