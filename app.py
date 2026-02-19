import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ==========================
# CONFIGURAÇÃO
# ==========================

st.set_page_config(
    page_title="Gestão de Fornecedores",
    layout="wide"
)

DB_NAME = "fornecedores.db"

# ==========================
# BANCO DE DADOS
# ==========================

def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fornecedor TEXT NOT NULL,
            competencia DATE NOT NULL,
            vencimento DATE NOT NULL,
            valor REAL NOT NULL,
            pago INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def inserir_fatura(fornecedor, competencia, vencimento, valor, pago):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO faturas (fornecedor, competencia, vencimento, valor, pago)
        VALUES (?, ?, ?, ?, ?)
    """, (fornecedor, competencia, vencimento, valor, pago))
    conn.commit()
    conn.close()


def carregar_faturas():
    conn = conectar()
    df = pd.read_sql("SELECT * FROM faturas", conn)
    conn.close()
    if not df.empty:
        df["competencia"] = pd.to_datetime(df["competencia"])
        df["vencimento"] = pd.to_datetime(df["vencimento"])
    return df


# ==========================
# LÓGICA DE STATUS
# ==========================

def classificar_status(row):
    hoje = pd.Timestamp.today().normalize()

    if row["pago"] == 1:
        return "PAGO", "#2ecc71"

    if row["vencimento"] < hoje:
        return "ATRASADO", "#e74c3c"

    return "PENDENTE", "#f39c12"


def ultima_fatura_por_fornecedor(df):
    return (
        df.sort_values("competencia")
        .groupby("fornecedor")
        .tail(1)
        .reset_index(drop=True)
    )


# ==========================
# INICIALIZAÇÃO
# ==========================

criar_tabela()

if "mostrar_form" not in st.session_state:
    st.session_state.mostrar_form = True

df = carregar_faturas()

aba1, aba2 = st.tabs(["📊 Dashboard", "📑 Controle de Faturas"])

# ==========================
# DASHBOARD
# ==========================

with aba1:

    st.title("📊 Status Geral dos Fornecedores")

    if df.empty:
        st.info("Nenhuma fatura cadastrada.")
    else:
        df_status = ultima_fatura_por_fornecedor(df)
        colunas = st.columns(3)

        for i, row in df_status.iterrows():
            status, cor = classificar_status(row)

            with colunas[i % 3]:
                st.markdown(
                    f"""
                    <div style="
                        padding:20px;
                        border-radius:12px;
                        background-color: var(--background-color);
                        border:1px solid #ccc;
                        border-left:8px solid {cor};
                        margin-bottom:20px;
                        color: var(--text-color);
                    ">
                        <h4 style="margin-bottom:10px;">{row['fornecedor']}</h4>
                        <p><b>Última competência:</b> {row['competencia'].strftime('%d/%m/%Y')}</p>
                        <p><b>Vencimento:</b> {row['vencimento'].strftime('%d/%m/%Y')}</p>
                        <p><b>Valor:</b> R$ {row['valor']:,.2f}</p>
                        <p><b>Status:</b> {status}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# ==========================
# CONTROLE DE FATURAS
# ==========================

with aba2:

    st.title("📑 Controle de Faturas")

    if not st.session_state.mostrar_form:
        if st.button("➕ Novo Registro"):
            st.session_state.mostrar_form = True
            st.rerun()

    if st.session_state.mostrar_form:

        fornecedor = st.text_input("Fornecedor", key="fornecedor")
        competencia = st.date_input(
            "Competência",
            format="DD/MM/YYYY",
            key="competencia"
        )
        vencimento = st.date_input(
            "Data de Vencimento",
            format="DD/MM/YYYY",
            key="vencimento"
        )
        valor = st.number_input(
            "Valor",
            min_value=0.0,
            format="%.2f",
            key="valor"
        )
        pago = st.checkbox("Já está pago?", key="pago")

        if st.button("Salvar"):

            if fornecedor == "":
                st.warning("Informe o nome do fornecedor.")
            else:
                inserir_fatura(
                    fornecedor=fornecedor,
                    competencia=competencia.strftime("%Y-%m-%d"),
                    vencimento=vencimento.strftime("%Y-%m-%d"),
                    valor=valor,
                    pago=1 if pago else 0
                )

                st.success("Fatura cadastrada com sucesso.")

                # Limpa campos
                st.session_state.fornecedor = ""
                st.session_state.valor = 0.0
                st.session_state.pago = False

                # Esconde formulário
                st.session_state.mostrar_form = False
                st.rerun()
