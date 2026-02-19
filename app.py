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

if "etapa" not in st.session_state:
    st.session_state.etapa=1

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

cfa, cfb, cfc = st.columns(3)

with cfa:
    forn_sel=st.selectbox(
        "Fornecedor",
        ["Todos"]+sorted(df["fornecedor"].dropna().unique().tolist())
        if not df.empty else ["Todos"]
    )

with cfb:
    status_sel=st.selectbox(
        "Status",
        ["Todos","Em andamento","Concluído"]
    )

with cfc:
    sla_sel=st.selectbox(
        "SLA",
        ["Todos","vencido","vence em breve","no prazo","concluido"]
    )

df_view=df.copy()

if forn_sel!="Todos":
    df_view=df_view[df_view["fornecedor"]==forn_sel]

if status_sel!="Todos":
    df_view=df_view[df_view["status"]==status_sel]

if sla_sel!="Todos":
    df_view=df_view[df_view["sla"]==sla_sel]

prioridade={"vencido":0,"vence em breve":1,"no prazo":2,"concluido":3}
if not df_view.empty:
    df_view["ord"]=df_view["sla"].map(prioridade)
    df_view=df_view.sort_values(["ord","vencimento"])

# =============================
# ALERTA DETALHADO
# =============================

vencidos = df_view[df_view["sla"]=="vencido"]

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
# GRÁFICO PIZZA
# =============================

if not df_view.empty:
    graf=df_view.groupby("fornecedor")["valor"].sum().sort_values(ascending=False)

    st.subheader("📊 Distribuição de Valores por Fornecedor")

    fig, ax = plt.subplots()
    ax.pie(
        graf,
        labels=graf.index,
        autopct='%1.1f%%',
        startangle=90
    )
    ax.axis("equal")

    st.pyplot(fig)

# =============================
# REGISTROS VISUAIS
# =============================

st.divider()
st.subheader("📁 Registros")

if not df_view.empty:

    status_cor = {
        "Concluído": "#1f8f4c",
        "Em andamento": "#fbc02d"
    }

    sla_cor = {
        "vencido": "#e53935",
        "vence em breve": "#fbc02d",
        "no prazo": "#1e88e5",
        "concluido": "#43a047"
    }

    for i,row in df_view.iterrows():

        with st.expander(f"📄 {row['fornecedor']} — {row['vencimento'].date()}"):

            st.markdown(f"""
<div style="padding:15px;border-radius:12px;
border-left:8px solid {status_cor.get(row['status'],'gray')};
background:#f9f9f9">

<b>Status:</b> <span style="color:{status_cor.get(row['status'],'black')};font-weight:600">
{row['status']}
</span><br>

<b>SLA:</b> <span style="color:{sla_cor.get(row['sla'],'black')};font-weight:600">
{row['sla']}
</span><br><br>

<b>Fatura:</b> {row['fatura']}<br>
<b>Valor:</b> R$ {row['valor']:,.2f}<br>
<b>CNPJ:</b> {row['cnpj']}<br>
<b>Pedido de compras Heflo:</b> {row['codigo_servico']}<br>
<b>Data Abertura:</b> {row['data_abertura']}<br>
<b>Código Pedido:</b> {row['codigo_pedido']}<br>
<b>Data Chamado:</b> {row['data_chamado']}
</div>
""", unsafe_allow_html=True)

            if st.button("✏️ Editar",key=f"e{i}"):
                st.session_state.edit_id=i
                st.session_state.temp=row.to_dict()
                st.session_state.etapa=1
                st.session_state.mostrar_nova=True
                st.rerun()

            if st.button("🗑️ Excluir",key=f"d{i}"):
                df.drop(i,inplace=True)
                salvar(df)
                st.rerun()

# =============================
# NOVA FATURA / EDIÇÃO
# =============================

st.divider()

if st.button("Nova Fatura +"):
    st.session_state.mostrar_nova=True
    st.session_state.edit_id=None

if st.session_state.mostrar_nova:

    st.subheader("🧾 Cadastro / Edição de Fatura")

    temp = st.session_state.get("temp", {})

    status=st.selectbox("Status",["Em andamento","Concluído"],
                        index=0 if temp.get("status","Em andamento")=="Em andamento" else 1)

    forn=st.text_input("Fornecedor",value=temp.get("fornecedor",""))
    fat=st.text_input("Fatura",value=temp.get("fatura",""))
    venc=st.date_input("Vencimento",
                       pd.to_datetime(temp.get("vencimento",date.today())))

    val=st.number_input("Valor",value=float(temp.get("valor",0.0)))
    cnpj=st.text_input("CNPJ",value=temp.get("cnpj",""))

    cod=st.text_input("Pedido de compras Heflo",
                      value=temp.get("codigo_servico",""))

    dab=st.date_input("Data abertura",
                      pd.to_datetime(temp.get("data_abertura",date.today())))

    ped=st.text_input("Código Pedido",
                      value=temp.get("codigo_pedido",""))

    dch=st.date_input("Data chamado",
                      pd.to_datetime(temp.get("data_chamado",date.today())))

    if st.button("💾 Salvar"):
        nova_linha={
            "status":status,
            "fornecedor":forn,
            "fatura":fat,
            "vencimento":str(venc),
            "valor":val,
            "cnpj":cnpj,
            "codigo_servico":cod,
            "data_abertura":str(dab),
            "codigo_pedido":ped,
            "data_chamado":str(dch)
        }

        if st.session_state.edit_id is not None:
            df.loc[st.session_state.edit_id]=nova_linha
        else:
            df=pd.concat([df,pd.DataFrame([nova_linha])],ignore_index=True)

        salvar(df)
        st.session_state.df=df
        st.session_state.mostrar_nova=False
        st.success("Salvo com sucesso!")
        st.rerun()
