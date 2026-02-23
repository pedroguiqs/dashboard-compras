import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor TEXT,
    numero TEXT,
    valor REAL
)
""")

st.title("Sistema de Faturas")

with st.form("nova_fatura"):
    fornecedor = st.text_input("Fornecedor")
    numero = st.text_input("Número da Fatura")
    valor = st.number_input("Valor")

    submitted = st.form_submit_button("Salvar")

    if submitted:
        cursor.execute(
            "INSERT INTO invoices (fornecedor, numero, valor) VALUES (?, ?, ?)",
            (fornecedor, numero, valor)
        )
        conn.commit()
        st.success("Fatura salva com sucesso!")

df = pd.read_sql("SELECT * FROM invoices", conn)
st.dataframe(df)
