import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Controle de Faturas", layout="wide")

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
# SESSION STATE
# =========================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=[
        "Fornecedor", "Mês", "Valor", "Status"
    ])

if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = False

if "editar_index" not in st.session_state:
    st.session_state.editar_index = None

# =========================
# SIDEBAR
# =========================
menu = st.sidebar.radio("Menu", ["Dashboard", "Controle de Faturas"])

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    st.title("📊 Dashboard Financeiro")

    df = st.session_state.dados

    col1, col2 = st.columns(2)

    total_pago = df[df["Status"] == "PAGO"]["Valor"].sum()
    total_andamento = df[df["Status"] == "EM ANDAMENTO"]["Valor"].sum()

    with col1:
        st.metric("Total Pago", f"R$ {total_pago:,.2f}")

    with col2:
        st.metric("Em Andamento", f"R$ {total_andamento:,.2f}")

    st.divider()

    if not df.empty:
        for i, row in df.iterrows():

            if row["Status"] == "PAGO":
                cor = "#28a745"  # Verde
            else:
                cor = "#ffc107"  # Amarelo

            st.markdown(
                f"""
                <div style="
                    background-color:{cor};
                    padding:15px;
                    border-radius:10px;
                    margin-bottom:10px;
                    color:black;
                    font-weight:600;">
                    {row['Fornecedor']} | {row['Mês']} <br>
                    R$ {row['Valor']:,.2f} - {row['Status']}
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================
# CONTROLE DE FATURAS
# =========================
if menu == "Controle de Faturas":

    st.title("🧾 Controle de Faturas")

    # Botão Novo Registro
    if not st.session_state.mostrar_form:
        if st.button("Novo Registro"):
            st.session_state.mostrar_form = True

    # Formulário
    if st.session_state.mostrar_form:

        with st.form("form_fatura", clear_on_submit=True):

            fornecedor = st.selectbox("Fornecedor", FORNECEDORES_PADRAO)
            mes = st.text_input("Mês (ex: JAN/2026)")
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")
            status = st.selectbox("Status", ["PAGO", "EM ANDAMENTO"])

            salvar = st.form_submit_button("Salvar")

            if salvar:

                novo_registro = {
                    "Fornecedor": fornecedor,
                    "Mês": mes,
                    "Valor": valor,
                    "Status": status
                }

                # Se estiver editando
                if st.session_state.editar_index is not None:
                    st.session_state.dados.loc[
                        st.session_state.editar_index
                    ] = novo_registro
                    st.session_state.editar_index = None
                else:
                    # Permite duplicar fornecedor no mesmo mês
                    st.session_state.dados = pd.concat(
                        [st.session_state.dados, pd.DataFrame([novo_registro])],
                        ignore_index=True
                    )

                st.session_state.mostrar_form = False
                st.rerun()

    st.divider()

    # =========================
    # LISTAGEM COM EDITAR / REMOVER
    # =========================
    df = st.session_state.dados

    if not df.empty:
        for i, row in df.iterrows():

            col1, col2, col3 = st.columns([5,1,1])

            with col1:
                st.write(f"**{row['Fornecedor']}** - {row['Mês']} - R$ {row['Valor']:,.2f} - {row['Status']}")

            with col2:
                if st.button("✏️", key=f"edit_{i}"):
                    st.session_state.editar_index = i
                    st.session_state.mostrar_form = True

            with col3:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.dados = st.session_state.dados.drop(i).reset_index(drop=True)
                    st.rerun()
