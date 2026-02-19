import streamlit as st
import pandas as pd
import sqlite3

# ==========================
# CONFIGURAÇÃO
# ==========================

st.set_page_config(page_title="Gestão de Fornecedores", layout="wide")
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


def atualizar_fatura(id_fatura, fornecedor, competencia, vencimento, valor, pago):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE faturas
        SET fornecedor=?, competencia=?, vencimento=?, valor=?, pago=?
        WHERE id=?
    """, (fornecedor, competencia, vencimento, valor, pago, id_fatura))
    conn.commit()
    conn.close()


def deletar_fatura(id_fatura):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM faturas WHERE id=?", (id_fatura,))
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
# INSERÇÃO INICIAL
# ==========================

def inserir_dados_iniciais():
    dados = [
        ("BERKLEY", "22/01/2026", "15/02/2026", "1.073,80"),
        ("THEODORO GÁS", "29/01/2026", "13/02/2026", "391,00"),
        ("FUSION", "03/02/2026", "23/02/2026", "1.249,96"),
        ("BRASIL SERVIÇOS", "04/02/2026", "25/02/2026", "20.603,00"),
        ("NISSEYS", "04/02/2026", "24/02/2026", "8.042,98"),
        ("BUONNY", "03/02/2026", "24/02/2026", "74,99"),
        ("E-SALES", "03/02/2026", "25/02/2026", "5.603,52"),
        ("BUONNY", "03/02/2026", "24/02/2026", "135,99"),
    ]

    conn = conectar()
    cursor = conn.cursor()

    for fornecedor, comp, venc, valor in dados:

        valor_convertido = float(valor.replace(".", "").replace(",", "."))

        cursor.execute("""
            INSERT INTO faturas (fornecedor, competencia, vencimento, valor, pago)
            VALUES (?, ?, ?, ?, ?)
        """, (
            fornecedor,
            pd.to_datetime(comp, dayfirst=True).strftime("%Y-%m-%d"),
            pd.to_datetime(venc, dayfirst=True).strftime("%Y-%m-%d"),
            valor_convertido,
            0  # EM ANDAMENTO
        ))

    conn.commit()
    conn.close()

# ==========================
# STATUS
# ==========================

def classificar_status(row):
    if row["pago"] == 1:
        return "PAGO", "#2ecc71"
    return "EM ANDAMENTO", "#f1c40f"


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

if carregar_faturas().empty:
    inserir_dados_iniciais()

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
                        border:1px solid #ccc;
                        border-left:8px solid {cor};
                        margin-bottom:20px;
                        background-color:white;
                        color:black;
                    ">
                        <h4>{row['fornecedor']}</h4>
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

    with st.form("form_fatura", clear_on_submit=True):

        fornecedor = st.text_input("Fornecedor")
        competencia = st.date_input("Competência", format="DD/MM/YYYY")
        vencimento = st.date_input("Vencimento", format="DD/MM/YYYY")
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        pago = st.checkbox("Pago?")

        salvar = st.form_submit_button("Salvar")

        if salvar:
            inserir_fatura(
                fornecedor,
                competencia.strftime("%Y-%m-%d"),
                vencimento.strftime("%Y-%m-%d"),
                valor,
                1 if pago else 0
            )
            st.success("Fatura cadastrada com sucesso.")
            st.rerun()

    st.divider()

    if not df.empty:

        st.subheader("Faturas Registradas")

        for _, row in df.iterrows():

            with st.expander(f"{row['fornecedor']} - {row['competencia'].strftime('%d/%m/%Y')}"):

                novo_fornecedor = st.text_input("Fornecedor", row["fornecedor"], key=f"f_{row['id']}")
                nova_comp = st.date_input("Competência", row["competencia"], format="DD/MM/YYYY", key=f"c_{row['id']}")
                novo_venc = st.date_input("Vencimento", row["vencimento"], format="DD/MM/YYYY", key=f"v_{row['id']}")
                novo_valor = st.number_input("Valor", value=float(row["valor"]), format="%.2f", key=f"val_{row['id']}")
                novo_pago = st.checkbox("Pago?", value=bool(row["pago"]), key=f"p_{row['id']}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Atualizar", key=f"up_{row['id']}"):
                        atualizar_fatura(
                            row["id"],
                            novo_fornecedor,
                            nova_comp.strftime("%Y-%m-%d"),
                            novo_venc.strftime("%Y-%m-%d"),
                            novo_valor,
                            1 if novo_pago else 0
                        )
                        st.success("Atualizado com sucesso.")
                        st.rerun()

                with col2:
                    if st.button("Remover", key=f"del_{row['id']}"):
                        deletar_fatura(row["id"])
                        st.warning("Fatura removida.")
                        st.rerun()
