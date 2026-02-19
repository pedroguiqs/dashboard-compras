import streamlit as st
import pandas as pd
from datetime import date
import json
import os
from io import BytesIO
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Compras",
    page_icon="💲",
    layout="wide"
)

# =============================
# LOGIN
# =============================

USUARIOS = {
    "admin": "1234",
    "pedro": "compras2026"
}

if "logado" not in st.session_state:
    st.session_state.logado = False

def tela_login():
    st.title("🔐 Login")
    user = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in USUARIOS and USUARIOS[user] == senha:
            st.session_state.logado = True
            st.success("Login realizado!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

if not st.session_state.logado:
    tela_login()
    st.stop()

if st.sidebar.button("🚪 Logout"):
    st.session_state.logado = False
    st.rerun()

# =============================
# SIDEBAR
# =============================

pagina = st.sidebar.radio(
    "📁 Menu",
    ["Gestão de Faturas","Gestão de Insumos"]
)

if pagina == "Gestão de Insumos":
    st.title("🛠️ Gestão de Insumos")
    st.info("Módulo em criação / manutenção.")
    st.stop()

# =============================
# BASE
# =============================

ARQ="dados_faturas.json"

COLUNAS=[
"status","fornecedor","fatura","vencimento","valor","cnpj",
"codigo_servico","data_abertura","codigo_pedido","data_chamado"
]

def carregar():
    if os.path.exists(ARQ):
        with open(ARQ,"r") as f:
            dados=json.load(f)
            return pd.DataFrame(dados,columns=COLUNAS)
    return pd.DataFrame(columns=COLUNAS)

def salvar(df):
    with open(ARQ,"w") as f:
        json.dump(df.to_dict(orient="records"),f,default=str)

if "df" not in st.session_state:
    st.session_state.df=carregar()

if "edit_id" not in st.session_state:
    st.session_state.edit_id=None

if "mostrar_nova" not in st.session_state:
    st.session_state.mostrar_nova=False

df=st.session_state.df

# =============================
# SLA
# =============================

hoje=pd.Timestamp.today()

def sla(row):
    if row["status"]=="Concluído":
        return "concluido"
    if not row["vencimento"]:
        return "no prazo"
    dias=(pd.to_datetime(row["vencimento"])-hoje).days
    if dias<0: return "vencido"
    if dias<=10: return "vence em breve"
    return "no prazo"

if not df.empty:
    df["sla"]=df.apply(sla,axis=1)
    df["vencimento"]=pd.to_datetime(df["vencimento"],errors="coerce")
    df["valor"]=pd.to_numeric(df["valor"],errors="coerce")

# =============================
# DASHBOARD
# =============================

st.title("📊 Dashboard de Faturas")

# =============================
# CARDS RESTAURADOS
# =============================

if not df.empty:

    total_fat=df[df["status"]=="Concluído"]["valor"].sum()
    total_nf=df[df["status"]!="Concluído"]["valor"].sum()
    geral=df["valor"].sum()

    c1,c2,c3=st.columns(3)

    c1.markdown(f"""
    <div style="padding:20px;border-radius:14px;background:#1f8f4c;color:white">
    <div style="font-size:16px">✅ Total faturado</div>
    <div style="font-size:28px;font-weight:600">R$ {total_fat:,.2f}</div>
    </div>
    """,unsafe_allow_html=True)

    c2.markdown(f"""
    <div style="padding:20px;border-radius:14px;background:#b00020;color:white">
    <div style="font-size:16px">❌ Total não faturado</div>
    <div style="font-size:28px;font-weight:600">R$ {total_nf:,.2f}</div>
    </div>
    """,unsafe_allow_html=True)

    c3.markdown(f"""
    <div style="padding:20px;border-radius:14px;background:#2b2b2b;color:white">
    <div style="font-size:16px">💰 Total geral</div>
    <div style="font-size:28px;font-weight:600">R$ {geral:,.2f}</div>
    </div>
    """,unsafe_allow_html=True)

    st.subheader("SLA de Pagamento")

    venc=len(df[df["sla"]=="vencido"])
    breve=len(df[df["sla"]=="vence em breve"])
    prazo=len(df[df["sla"]=="no prazo"])
    conc=len(df[df["sla"]=="concluido"])

    s1,s2,s3,s4=st.columns(4)

    s1.markdown(f"<div style='border-left:6px solid red;padding:15px;background:#f2f2f2;border-radius:10px'><b>VENCIDO</b><br><h3>{venc}</h3></div>",unsafe_allow_html=True)
    s2.markdown(f"<div style='border-left:6px solid orange;padding:15px;background:#f2f2f2;border-radius:10px'><b>VENCE EM BREVE</b><br><h3>{breve}</h3></div>",unsafe_allow_html=True)
    s3.markdown(f"<div style='border-left:6px solid blue;padding:15px;background:#f2f2f2;border-radius:10px'><b>NO PRAZO</b><br><h3>{prazo}</h3></div>",unsafe_allow_html=True)
    s4.markdown(f"<div style='border-left:6px solid green;padding:15px;background:#f2f2f2;border-radius:10px'><b>CONCLUÍDO</b><br><h3>{conc}</h3></div>",unsafe_allow_html=True)

# =============================
# ALERTA DETALHADO
# =============================

vencidos = df[df["sla"]=="vencido"]

if not vencidos.empty:
    soma = vencidos["valor"].sum()

    nomes = "\n".join([
        f"- {r['fornecedor']} | Fatura: {r['fatura']} | Venc: {pd.to_datetime(r['vencimento']).date()} | R$ {r['valor']:,.2f}"
        for _, r in vencidos.iterrows()
    ])

    st.error(f"""
⚠️ {len(vencidos)} faturas vencidas — Total R$ {soma:,.2f}

{nomes}
""")

# =============================
# GRÁFICO PIZZA MENOR
# =============================

if not df.empty:
    graf=df.groupby("fornecedor")["valor"].sum().sort_values(ascending=False)

    st.subheader("📊 Distribuição de Valores por Fornecedor")

    fig, ax = plt.subplots(figsize=(4,4))  # reduzido
    ax.pie(graf, labels=graf.index, autopct='%1.1f%%', startangle=90)
    ax.axis("equal")

    st.pyplot(fig)
