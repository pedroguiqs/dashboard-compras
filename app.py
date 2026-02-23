import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(layout="wide")
st.title("Gestão de Faturas")

# ==========================
# BANCO
# ==========================

conn = sqlite3.connect("faturas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT,
    numero_fatura TEXT,
    valor REAL,
    vencimento TEXT,
    numero_heflo TEXT,
    numero_v360 TEXT
)
""")
conn.commit()

# ==========================
# LISTAS
# ==========================

FORNECEDORES = [
    "E-SALES",
    "PAES E DOCES JARDIM THELMA",
    "PALLEFORT COMERCIO",
    "BRASIL SERVIÇOS",
    "EZ TOOLS",
    "NISSEYS",
    "FUSION"
]

# ==========================
# ESTADO
# ==========================

if "modo_form" not in st.session_state:
    st.session_state.modo_form = None  # None | novo | editar

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None

# ==========================
# FUNÇÕES
# ==========================

def limpar_campos():
    for key in [
        "fornecedor",
        "numero_fatura",
        "valor",
        "vencimento",
        "numero_heflo",
        "numero_v360"
    ]:
        if key in st.session_state:
            del st.session_state[key]

# ==========================
# BOTÃO NOVA FATURA
# ==========================

if st.button("Nova Fatura"):
    st.session_state.modo_form = "novo"
    st.session_state.edit_id = None
    limpar_campos()
    st.rerun()

# ==========================
# FORMULÁRIO UNIFICADO
# ==========================

if st.session_state.modo_form in ["novo", "editar"]:

    st.subheader("Cadastro de Fatura")

    fornecedor = st.selectbox(
        "Fornecedor",
        FORNECEDORES,
        key="fornecedor"
    )

    numero_fatura = st.text_input("Número da Fatura", key="numero_fatura")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f", key="valor")
    vencimento = st.date_input("Vencimento", key="vencimento")
    numero_heflo = st.text_input("Número Heflo", key="numero_heflo")
    numero_v360 = st.text_input("Número Chamado V360", key="numero_v360")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Salvar" if st.session_state.modo_form == "novo" else "Atualizar"):

            if st.session_state.modo_form == "novo":
                cursor.execute("""
                    INSERT INTO invoices (
                        fornecedor, numero_fatura, valor,
                        vencimento, numero_heflo, numero_v360
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    fornecedor, numero_fatura, valor,
                    vencimento, numero_heflo, numero_v360
                ))
            else:
                cursor.execute("""
                    UPDATE invoices
                    SET fornecedor=?, numero_fatura=?, valor=?,
                        vencimento=?, numero_heflo=?, numero_v360=?
                    WHERE id=?
                """, (
                    fornecedor, numero_fatura, valor,
                    vencimento, numero_heflo, numero_v360,
                    st.session_state.edit_id
                ))

            conn.commit()

            limpar_campos()
            st.session_state.modo_form = None
            st.session_state.edit_id = None
            st.rerun()

    with col2:
        if st.button("Cancelar"):
            limpar_campos()
            st.session_state.modo_form = None
            st.session_state.edit_id = None
            st.rerun()

# ==========================
# TABELA
# ==========================

st.divider()
st.subheader("Faturas Registradas")

df = pd.read_sql_query("SELECT * FROM invoices", conn)

if not df.empty:

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="tabela"
    )

    # DETECTAR EXCLUSÕES
    ids_originais = set(df["id"])
    ids_atuais = set(edited_df["id"])

    ids_removidos = ids_originais - ids_atuais

    if ids_removidos:
        for id_del in ids_removidos:
            cursor.execute("DELETE FROM invoices WHERE id=?", (id_del,))
        conn.commit()
        st.rerun()

    # DETECTAR CLIQUE PARA EDITAR
    if st.button("Editar Selecionado"):
        if len(edited_df) > 0:
            selected_row = edited_df.iloc[0]  # primeira linha

            st.session_state.modo_form = "editar"
            st.session_state.edit_id = selected_row["id"]

            st.session_state.fornecedor = selected_row["fornecedor"]
            st.session_state.numero_fatura = selected_row["numero_fatura"]
            st.session_state.valor = selected_row["valor"]
            st.session_state.vencimento = pd.to_datetime(selected_row["vencimento"]).date()
            st.session_state.numero_heflo = selected_row["numero_heflo"]
            st.session_state.numero_v360 = selected_row["numero_v360"]

            st.rerun()

else:
    st.info("Nenhuma fatura cadastrada.")
