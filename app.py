import streamlit as st
import pandas as pd

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
# ABAS NO TOPO
# =========================
aba_dashboard, aba_controle = st.tabs(["Dashboard", "Controle de Faturas"])

# =========================
# DASHBOARD
# =========================
with aba_dashboard:

    st.title("📊 Dashboard de Faturas")

    df = st.session_state.dados

    if df.empty:
        st.info("Nenhuma fatura cadastrada ainda.")
    else:
        for i, row in df.iterrows():

            if row["Status"] == "CONCLUÍDO":
                cor = "#28a745"  # Verde
                texto_cor = "white"
            else:
                cor = "#ffc107"  # Amarelo
                texto_cor = "black"

            st.markdown(
                f"""
                <div style="
                    background-color:{cor};
                    padding:20px;
                    border-radius:12px;
                    margin-bottom:12px;
                    font-weight:600;
                    color:{texto_cor};
                    font-size:16px;">
                    {row['Fornecedor']}<br>
                    {row['Mês']} | R$ {row['Valor']:,.2f}<br>
                    {row['Status']}
                </div>
                """,
                unsafe_allow_html=True
            )

# =========================
# CONTROLE DE FATURAS
# =========================
with aba_controle:

    st.title("🧾 Controle de Faturas")

    # Botão Novo Registro
    if not st.session_state.mostrar_form:
        if st.button("Novo Registro"):
            st.session_state.mostrar_form = True

    # FORMULÁRIO
    if st.session_state.mostrar_form:

        with st.form("form_fatura", clear_on_submit=True):

            fornecedor = st.selectbox("Fornecedor", FORNECEDORES_PADRAO)
            mes = st.text_input("Mês (ex: JAN/2026)")
            valor = st.number_input("Valor", min_value=0.0, format="%.2f")
            status = st.selectbox("Status", ["CONCLUÍDO", "EM ANDAMENTO"])

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
                    # Permite duplicidade no mesmo mês (ex: BUONNY)
                    st.session_state.dados = pd.concat(
                        [st.session_state.dados, pd.DataFrame([novo_registro])],
                        ignore_index=True
                    )

                st.session_state.mostrar_form = False
                st.rerun()

    st.divider()

    # LISTAGEM COM EDITAR / REMOVER
    df = st.session_state.dados

    if not df.empty:
        for i, row in df.iterrows():

            col1, col2, col3 = st.columns([6,1,1])

            with col1:
                st.write(
                    f"**{row['Fornecedor']}** | "
                    f"{row['Mês']} | "
                    f"R$ {row['Valor']:,.2f} | "
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
                    st.rerun()
