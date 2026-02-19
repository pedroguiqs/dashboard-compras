import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Controle Financeiro", layout="wide")

# =========================
# FORNECEDORES
# =========================
FORNECEDORES_PADRAO = sorted(list(set([
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
])))

FORNECEDORES_PERMITEM_DUPLICIDADE = ["BUONNY"]

# =========================
# SESSION STATE
# =========================
if "registros" not in st.session_state:
    st.session_state.registros = []

if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = True

# =========================
# CSS PARA CARDS (contraste claro/escuro)
# =========================
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 16px;
    background-color: var(--secondary-background-color);
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    text-align: center;
}
.card h3 {
    margin: 0;
    font-size: 18px;
}
.card p {
    font-size: 24px;
    font-weight: bold;
    margin: 5px 0 0 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# ABAS
# =========================
aba1, aba2 = st.tabs(["Controle de Faturas", "Dashboard"])

# ============================================================
# ABA 1 - CONTROLE DE FATURAS
# ============================================================
with aba1:

    st.title("Controle de Faturas")

    if not st.session_state.mostrar_form:
        if st.button("Novo Registro"):
            st.session_state.mostrar_form = True
            st.rerun()

    if st.session_state.mostrar_form:

        with st.form("form_fatura"):

            col1, col2 = st.columns(2)

            with col1:
                fornecedor = st.selectbox("Fornecedor", FORNECEDORES_PADRAO)
                numero_fatura = st.text_input("Número da Fatura")

            with col2:
                data_vencimento = st.date_input("Data de Vencimento", format="DD/MM/YYYY")
                valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

            status = st.selectbox("Status", ["Pendente", "Pago"])

            salvar = st.form_submit_button("Salvar")

        if salvar:

            mes_referencia = data_vencimento.strftime("%m/%Y")

            fornecedores_mes = [
                r["fornecedor"]
                for r in st.session_state.registros
                if r["mes"] == mes_referencia
            ]

            if fornecedor in fornecedores_mes and fornecedor not in FORNECEDORES_PERMITEM_DUPLICIDADE:
                st.warning("Fornecedor já lançado neste mês.")
                st.stop()

            novo_registro = {
                "fornecedor": fornecedor,
                "numero": numero_fatura,
                "data": data_vencimento.strftime("%d/%m/%Y"),
                "valor": valor,
                "status": status,
                "mes": mes_referencia
            }

            st.session_state.registros.append(novo_registro)

            st.success("Registro salvo com sucesso!")

            st.session_state.mostrar_form = False
            st.rerun()

# ============================================================
# ABA 2 - DASHBOARD
# ============================================================
with aba2:

    st.title("Dashboard Financeiro")

    total_faturas = len(st.session_state.registros)
    total_valor = sum(r["valor"] for r in st.session_state.registros)
    pendentes = sum(1 for r in st.session_state.registros if r["status"] == "Pendente")
    pagas = sum(1 for r in st.session_state.registros if r["status"] == "Pago")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>Total de Faturas</h3>
            <p>{total_faturas}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>Valor Total</h3>
            <p>R$ {total_valor:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="card">
            <h3>Pendentes</h3>
            <p>{pendentes}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="card">
            <h3>Pagas</h3>
            <p>{pagas}</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    if st.session_state.registros:
        st.dataframe(st.session_state.registros, use_container_width=True)
    else:
        st.info("Nenhum registro cadastrado ainda.")
