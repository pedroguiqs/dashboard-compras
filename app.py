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
# ESTRUTURA PADRÃO DO DATAFRAME
# =========================
COLUNAS_PADRAO = [
    "Fornecedor",
    "Mes_Competencia",
    "Mes_Vencimento",
    "Mes_Referencia",
    "Valor",
    "Status"
]

# =========================
# GARANTIR ESTRUTURA CORRETA
# =========================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=COLUNAS_PADRAO)
else:
    if list(st.session_state.dados.columns) != COLUNAS_PADRAO:
        st.session_state.dados = pd.DataFrame(columns=COLUNAS_PADRAO)

if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = False

if "editar_index" not in st.session_state:
    st.session_state.editar_index = None

# =========================
# TÍTULO
# =========================
st.title("🧾 Controle Geral de Faturas")

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
        competencia = st.text_input("Mês de Competência (ex: JAN/2026)")
        vencimento = st.text_input("Mês de Vencimento (ex: FEV/2026)")
        referencia = st.text_input("Mês de Referência (ex: JAN/2026)")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        status = st.selectbox("Status", ["CONCLUÍDO", "EM ANDAMENTO"])

        salvar = st.form_submit_button("Salvar")

        if salvar:

            novo = {
                "Fornecedor": fornecedor,
                "Mes_Competencia": competencia,
                "Mes_Vencimento": vencimento,
                "Mes_Referencia": referencia,
                "Valor": valor,
                "Status": status
            }

            # EDIÇÃO
            if st.session_state.editar_index is not None:
                st.session_state.dados.loc[
                    st.session_state.editar_index
                ] = novo
                st.session_state.editar_index = None

            else:
                # REGRA: Atualiza se for mesmo fornecedor + mesma competência + mesma referência
                filtro = (
                    (st.session_state.dados["Fornecedor"] == fornecedor) &
                    (st.session_state.dados["Mes_Competencia"] == competencia) &
                    (st.session_state.dados["Mes_Referencia"] == referencia)
                )

                if filtro.any():
                    st.session_state.dados.loc[filtro, :] = novo
                else:
                    st.session_state.dados = pd.concat(
                        [st.session_state.dados, pd.DataFrame([novo])],
                        ignore_index=True
                    )

            st.session_state.mostrar_form = False
            st.rerun()

st.divider()

# =========================
# CARDS NO TOPO
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
                font-size:14px;">
                {row['Fornecedor']}<br><br>
                Competência: {row['Mes_Competencia']}<br>
                Vencimento: {row['Mes_Vencimento']}<br>
                Referência: {row['Mes_Referencia']}<br>
                Valor: R$ {row['Valor']:,.2f}
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# =========================
# LISTA DETALHADA
# =========================
st.subheader("Lista Completa")

if not df.empty:

    for i, row in df.iterrows():

        col1, col2, col3 = st.columns([6,1,1])

        with col1:
            st.write(
                f"**{row['Fornecedor']}** | "
                f"Comp: {row['Mes_Competencia']} | "
                f"Venc: {row['Mes_Vencimento']} | "
                f"Ref: {row['Mes_Referencia']} | "
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
else:
    st.info("Nenhum registro cadastrado ainda.")
