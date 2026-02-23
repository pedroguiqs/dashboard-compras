import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ==============================
# CONFIGURAÇÃO INICIAL
# ==============================

st.set_page_config(layout="wide")
st.title("Gestão de Faturas")

# ==============================
# BANCO DE DADOS
# ==============================

conn = sqlite3.connect("faturas.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT,
    numero_fatura TEXT,
    valor REAL,
    vencimento TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS heflos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    numero_heflo TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chamados_v360 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    numero_v360 TEXT
)
""")

conn.commit()

# ==============================
# LISTAS (BLOCO 2)
# ==============================

FORNECEDORES = [
    "E-SALES",
    "PAES E DOCES JARDIM THELMA",
    "PALLEFORT COMERCIO",
    "BRASIL SERVIÇOS",
    "EZ TOOLS",
    "NISSEYS",
    "FUSION"
]

# ==============================
# ESTADO
# ==============================

if "mostrar_formulario" not in st.session_state:
    st.session_state.mostrar_formulario = False

if "invoice_id" not in st.session_state:
    st.session_state.invoice_id = None

# ==============================
# BOTÃO NOVA FATURA
# ==============================

if st.button("Nova Fatura"):
    st.session_state.mostrar_formulario = True
    st.session_state.invoice_id = None

# ==============================
# FORMULÁRIO
# ==============================

if st.session_state.mostrar_formulario:

    abas = st.tabs(["Cadastro de Fatura", "Requisição Heflo", "Chamado V360"])

    # ==============================
    # ABA 1
    # ==============================
    with abas[0]:
        fornecedor = st.selectbox("Fornecedor", FORNECEDORES)
        numero_fatura = st.text_input("Número da Fatura")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        vencimento = st.date_input("Vencimento", value=date.today())

        if st.button("Salvar Fatura"):
            cursor.execute("""
                INSERT INTO invoices (fornecedor, numero_fatura, valor, vencimento)
                VALUES (?, ?, ?, ?)
            """, (fornecedor, numero_fatura, valor, vencimento))
            conn.commit()

            st.session_state.invoice_id = cursor.lastrowid
            st.success("Fatura salva com sucesso!")
            st.rerun()

    # ==============================
    # ABA 2
    # ==============================
    with abas[1]:
        if st.session_state.invoice_id:
            numero_heflo = st.text_input("Número Heflo")

            if st.button("Salvar Heflo"):
                cursor.execute("""
                    INSERT INTO heflos (invoice_id, numero_heflo)
                    VALUES (?, ?)
                """, (st.session_state.invoice_id, numero_heflo))
                conn.commit()
                st.success("Heflo salvo com sucesso!")
                st.rerun()
        else:
            st.info("Salve a Fatura primeiro.")

    # ==============================
    # ABA 3
    # ==============================
    with abas[2]:
        if st.session_state.invoice_id:
            numero_v360 = st.text_input("Número Chamado V360")

            if st.button("Salvar V360"):
                cursor.execute("""
                    INSERT INTO chamados_v360 (invoice_id, numero_v360)
                    VALUES (?, ?)
                """, (st.session_state.invoice_id, numero_v360))
                conn.commit()
                st.success("Chamado V360 salvo com sucesso!")
                st.rerun()
        else:
            st.info("Finalize o Heflo antes.")

# ==============================
# TABELA INFERIOR (SEMPRE VISÍVEL)
# ==============================

st.divider()
st.subheader("Faturas Registradas")

query = """
SELECT 
    i.id,
    i.fornecedor,
    i.numero_fatura,
    i.valor,
    i.vencimento,
    h.numero_heflo,
    v.numero_v360
FROM invoices i
LEFT JOIN heflos h ON i.id = h.invoice_id
LEFT JOIN chamados_v360 v ON i.id = v.invoice_id
"""

df = pd.read_sql_query(query, conn)

if not df.empty:
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")

    if st.button("Salvar Alterações"):
        for _, row in edited_df.iterrows():
            cursor.execute("""
                UPDATE invoices
                SET fornecedor = ?, numero_fatura = ?, valor = ?, vencimento = ?
                WHERE id = ?
            """, (
                row["fornecedor"],
                row["numero_fatura"],
                row["valor"],
                row["vencimento"],
                row["id"]
            ))
        conn.commit()
        st.success("Alterações salvas com sucesso!")
        st.rerun()
else:
    st.info("Nenhuma fatura cadastrada ainda.")
