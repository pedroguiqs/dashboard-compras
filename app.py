import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# ==============================
# CONFIGURAÇÃO
# ==============================

st.set_page_config(layout="wide")
st.title("Gestão de Faturas")

# ==============================
# BANCO
# ==============================

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

if "etapa" not in st.session_state:
    st.session_state.etapa = 1

# ==============================
# BOTÃO NOVA FATURA
# ==============================

if st.button("Nova Fatura"):
    st.session_state.mostrar_formulario = True
    st.session_state.etapa = 1

# ==============================
# FORMULÁRIO SEQUENCIAL
# ==============================

if st.session_state.mostrar_formulario:

    abas = st.tabs(["Cadastro de Fatura", "Requisição Heflo", "Chamado V360"])

    # ==============================
    # ABA 1
    # ==============================
    with abas[0]:
        fornecedor = st.selectbox("Fornecedor", FORNECEDORES, key="fornecedor")
        numero_fatura = st.text_input("Número da Fatura", key="numero_fatura")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f", key="valor")
        vencimento = st.date_input("Vencimento", value=date.today(), key="vencimento")

        if st.button("Próximo → Heflo"):
            st.session_state.etapa = 2
            st.rerun()

    # ==============================
    # ABA 2
    # ==============================
    with abas[1]:
        if st.session_state.etapa >= 2:
            numero_heflo = st.text_input("Número Heflo", key="numero_heflo")

            if st.button("Próximo → V360"):
                st.session_state.etapa = 3
                st.rerun()
        else:
            st.info("Preencha a Aba 1 primeiro.")

    # ==============================
    # ABA 3
    # ==============================
    with abas[2]:
        if st.session_state.etapa >= 3:
            numero_v360 = st.text_input("Número Chamado V360", key="numero_v360")

            if st.button("Salvar Fatura Completa"):
                cursor.execute("""
                    INSERT INTO invoices (
                        fornecedor,
                        numero_fatura,
                        valor,
                        vencimento,
                        numero_heflo,
                        numero_v360
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    st.session_state.fornecedor,
                    st.session_state.numero_fatura,
                    st.session_state.valor,
                    st.session_state.vencimento,
                    st.session_state.numero_heflo,
                    st.session_state.numero_v360
                ))
                conn.commit()

                # LIMPAR CAMPOS
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

                st.session_state.mostrar_formulario = False
                st.session_state.etapa = 1

                st.success("Fatura salva com sucesso!")
                st.rerun()
        else:
            st.info("Finalize a Aba 2 primeiro.")

# ==============================
# TABELA
# ==============================

st.divider()
st.subheader("Faturas Registradas")

df = pd.read_sql_query("SELECT * FROM invoices", conn)

if not df.empty:

    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic"
    )

    # SALVAR ALTERAÇÕES
    if st.button("Salvar Alterações"):
        for _, row in edited_df.iterrows():
            cursor.execute("""
                UPDATE invoices
                SET fornecedor = ?, numero_fatura = ?, valor = ?, vencimento = ?,
                    numero_heflo = ?, numero_v360 = ?
                WHERE id = ?
            """, (
                row["fornecedor"],
                row["numero_fatura"],
                row["valor"],
                row["vencimento"],
                row["numero_heflo"],
                row["numero_v360"],
                row["id"]
            ))
        conn.commit()
        st.success("Alterações salvas.")
        st.rerun()

    # EXCLUIR REGISTROS REMOVIDOS
    ids_atuais = set(df["id"])
    ids_editados = set(edited_df["id"])

    ids_removidos = ids_atuais - ids_editados

    if ids_removidos:
        for id_removido in ids_removidos:
            cursor.execute("DELETE FROM invoices WHERE id = ?", (id_removido,))
        conn.commit()
        st.rerun()

else:
    st.info("Nenhuma fatura cadastrada ainda.")
