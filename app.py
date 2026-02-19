import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Compras", page_icon="💲", layout="wide")

# ==============================
# LOGIN
# ==============================

USUARIOS = {"admin": "1234"}

if "logado" not in st.session_state:
    st.session_state.logado = False

def login():
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in USUARIOS and USUARIOS[user] == senha:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

if not st.session_state.logado:
    login()
    st.stop()

# ==============================
# BASE
# ==============================

ARQ = "dados_faturas.json"

COLUNAS = [
"status","fornecedor","fatura","vencimento","valor","cnpj",
"codigo_servico","data_abertura","codigo_pedido","data_chamado"
]

def carregar():
    if os.path.exists(ARQ):
        with open(ARQ,"r") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame(columns=COLUNAS)

def salvar(df):
    with open(ARQ,"w") as f:
        json.dump(df.to_dict(orient="records"),f,default=str)

if "df" not in st.session_state:
    st.session_state.df = carregar()

df = st.session_state.df

# ==============================
# SLA
# ==============================

hoje = pd.Timestamp.today()

def calcular_sla(row):
    if row["status"] == "Concluído":
        return "concluido"
    dias = (pd.to_datetime(row["vencimento"]) - hoje).days
    if dias < 0: return "vencido"
    if dias <= 10: return "vence em breve"
    return "no prazo"

if not df.empty:
    df["vencimento"] = pd.to_datetime(df["vencimento"], errors="coerce")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df["sla"] = df.apply(calcular_sla, axis=1)

# ==============================
# DASHBOARD
# ==============================

st.title("📊 Dashboard de Faturas")

if not df.empty:

    total_faturado = df[df["status"]=="Concluído"]["valor"].sum()
    total_nao_faturado = df[df["status"]!="Concluído"]["valor"].sum()
    total_geral = df["valor"].sum()

    # ===== CARDS SUPERIORES =====
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div style="background:#118d57;padding:25px;border-radius:15px;color:white">
    <h4>✔ Total faturado</h4>
    <h2>R$ {total_faturado:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div style="background:#c0001a;padding:25px;border-radius:15px;color:white">
    <h4>✖ Total não faturado</h4>
    <h2>R$ {total_nao_faturado:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div style="background:#1f1f1f;padding:25px;border-radius:15px;color:white">
    <h4>💰 Total geral</h4>
    <h2>R$ {total_geral:,.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("SLA de Pagamento")

    vencido = len(df[df["sla"]=="vencido"])
    breve = len(df[df["sla"]=="vence em breve"])
    prazo = len(df[df["sla"]=="no prazo"])
    concluido = len(df[df["sla"]=="concluido"])

    c1,c2,c3,c4 = st.columns(4)

    c1.markdown(f"<div style='border-left:6px solid red;padding:15px;background:#f2f2f2;border-radius:10px'><b>VENCIDO</b><br><h3>{vencido}</h3></div>", unsafe_allow_html=True)
    c2.markdown(f"<div style='border-left:6px solid orange;padding:15px;background:#f2f2f2;border-radius:10px'><b>VENCE EM BREVE</b><br><h3>{breve}</h3></div>", unsafe_allow_html=True)
    c3.markdown(f"<div style='border-left:6px solid blue;padding:15px;background:#f2f2f2;border-radius:10px'><b>NO PRAZO</b><br><h3>{prazo}</h3></div>", unsafe_allow_html=True)
    c4.markdown(f"<div style='border-left:6px solid green;padding:15px;background:#f2f2f2;border-radius:10px'><b>CONCLUÍDO</b><br><h3>{concluido}</h3></div>", unsafe_allow_html=True)

    # ===== GRÁFICO MENOR =====
    st.subheader("📊 Valor por Fornecedor")

    graf = df.groupby("fornecedor")["valor"].sum()

    fig, ax = plt.subplots(figsize=(5,4))
    ax.bar(graf.index, graf.values)
    plt.xticks(rotation=45)
    st.pyplot(fig)

# ==============================
# FORMULÁRIO COM 3 ABAS
# ==============================

st.divider()
st.subheader("Nova Fatura")

tab1, tab2, tab3 = st.tabs([
    "Registro da Fatura",
    "Pedido de Compra",
    "Chamado V360"
])

with tab1:
    fornecedor = st.text_input("Fornecedor")
    fatura = st.text_input("Número da Fatura")
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    vencimento = st.date_input("Vencimento")
    cnpj = st.text_input("CNPJ")
    status = st.selectbox("Status", ["Em andamento","Concluído"])

with tab2:
    codigo_servico = st.text_input("Pedido de compras Heflo")
    data_abertura = st.date_input("Data Abertura")

with tab3:
    codigo_pedido = st.text_input("Código Chamado V360")
    data_chamado = st.date_input("Data Chamado")

if st.button("Salvar"):

    nova = {
        "status":status,
        "fornecedor":fornecedor,
        "fatura":fatura,
        "vencimento":str(vencimento),
        "valor":valor,
        "cnpj":cnpj,
        "codigo_servico":codigo_servico,
        "data_abertura":str(data_abertura),
        "codigo_pedido":codigo_pedido,
        "data_chamado":str(data_chamado)
    }

    df = pd.concat([df,pd.DataFrame([nova])],ignore_index=True)
    salvar(df)
    st.session_state.df = df
    st.success("Salvo com sucesso!")
    st.rerun()
