import streamlit as st
import pandas as pd
from datetime import date
import json
import os
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Compras",
    page_icon="💲",
    layout="wide"
)

# =============================
# SIDEBAR NAVEGAÇÃO (ADICIONADO)
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
# SEU CÓDIGO ORIGINAL CONTINUA
# =============================

ARQ="dados_faturas.json"

COLUNAS=[
"status","fornecedor","fatura","vencimento","valor","cnpj",
"codigo_servico","data_abertura","codigo_pedido","data_chamado"
]

# =============================
# Persistência
# =============================
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

# ---------- FILTROS ----------
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

# ---------- ORDENAÇÃO ----------
prioridade={"vencido":0,"vence em breve":1,"no prazo":2,"concluido":3}
if not df_view.empty:
    df_view["ord"]=df_view["sla"].map(prioridade)
    df_view=df_view.sort_values(["ord","vencimento"])

# ---------- ALERTA ----------
vencidos=df_view[df_view["sla"]=="vencido"]
if not vencidos.empty:
    soma=vencidos["valor"].sum()
    st.error(f"⚠️ {len(vencidos)} faturas vencidas somando R$ {soma:,.2f}")

# ---------- CARDS ----------
def card_total(titulo,valor,cor):
    st.markdown(f"""
    <div style="padding:18px;border-radius:14px;background:{cor};color:white">
    <div style="font-size:15px">{titulo}</div>
    <div style="font-size:28px;font-weight:600">{valor}</div>
    </div>
    """,unsafe_allow_html=True)

def card_sla(titulo,valor,perc,cor):
    st.markdown(f"""
    <div style="background:#f2f2f2;padding:18px;border-radius:14px;border-left:10px solid {cor}">
    <div style="font-weight:600;color:#555">{titulo.upper()}</div>
    <div style="font-size:26px;font-weight:700;color:#444">{valor} ({perc}%)</div>
    </div>
    """,unsafe_allow_html=True)

if not df_view.empty:

    total_fat=df_view[df_view["status"]=="Concluído"]["valor"].sum()
    total_nf=df_view[df_view["status"]!="Concluído"]["valor"].sum()
    geral=df_view["valor"].sum()

    venc=len(df_view[df_view["sla"]=="vencido"])
    breve=len(df_view[df_view["sla"]=="vence em breve"])
    prazo=len(df_view[df_view["sla"]=="no prazo"])
    conc=len(df_view[df_view["status"]=="Concluído"])

    tot=len(df_view)
    pv=lambda x: round((x/tot)*100,1) if tot else 0

    c1,c2,c3=st.columns(3)
    with c1: card_total("✅ Total faturado",f"R$ {total_fat:,.2f}","#1f8f4c")
    with c2: card_total("❌ Total não faturado",f"R$ {total_nf:,.2f}","#b00020")
    with c3: card_total("💰 Total geral",f"R$ {geral:,.2f}","#2b2b2b")

    st.subheader("SLA de Pagamento")

    s1,s2,s3,s4=st.columns(4)
    with s1: card_sla("Vencido",venc,pv(venc),"#e53935")
    with s2: card_sla("Vence em Breve",breve,pv(breve),"#fbc02d")
    with s3: card_sla("No Prazo",prazo,pv(prazo),"#1e88e5")
    with s4: card_sla("Concluído",conc,pv(conc),"#43a047")

# ---------- EXPORTAÇÃO ----------
if not df_view.empty:
    output=BytesIO()
    df_view.to_excel(output,index=False)
    st.download_button(
        "📥 Exportar Excel",
        data=output.getvalue(),
        file_name="faturas.xlsx"
    )

# ---------- GRÁFICO ----------
if not df_view.empty:
    graf=df_view.groupby("fornecedor")["valor"].sum().sort_values(ascending=False)
    st.subheader("📊 Valor por Fornecedor")
    st.bar_chart(graf)

# =============================
# REGISTROS
# =============================
st.divider()
st.subheader("📁 Registros")

if not df_view.empty:
    for i,row in df_view.iterrows():
        with st.expander(f"📄 {row['fornecedor']} — {row['vencimento'].date()}"):

            st.write(f"**Status:** {row['status']}")
            st.write(f"**Fatura:** {row['fatura']}")
            st.write(f"**Valor:** R$ {row['valor']:,.2f}")
            st.write(f"**CNPJ:** {row['cnpj']}")
            st.write(f"**Código Serviço:** {row['codigo_servico']}")
            st.write(f"**Data Abertura:** {row['data_abertura']}")
            st.write(f"**Código Pedido:** {row['codigo_pedido']}")
            st.write(f"**Data Chamado:** {row['data_chamado']}")

            if row["status"]!="Concluído":
                if st.button("✏️ Editar",key=f"e{i}"):
                    st.session_state.edit_id=i
                    st.session_state.etapa=1
                    st.session_state.mostrar_nova=True
                    st.rerun()

            if st.button("🗑️ Excluir",key=f"d{i}"):
                df.drop(i,inplace=True)
                salvar(df)
                st.rerun()

# =============================
# WIZARD
# =============================
st.divider()

if st.button("Nova Fatura +"):
    st.session_state.mostrar_nova=True

if st.session_state.mostrar_nova:

    st.subheader("🧾 Nova Fatura")

    if st.session_state.etapa==1:

        status=st.selectbox("Status",["Em andamento","Concluído"])
        forn=st.text_input("Fornecedor")
        fat=st.text_input("Fatura")
        venc=st.date_input("Vencimento",date.today())
        val=st.number_input("Valor")
        cnpj=st.text_input("CNPJ")

        if st.button("Salvar Etapa 1"):
            st.session_state.temp={
            "status":status,"fornecedor":forn,"fatura":fat,
            "vencimento":str(venc),"valor":val,"cnpj":cnpj,
            "codigo_servico":"","data_abertura":"",
            "codigo_pedido":"","data_chamado":""}
            st.session_state.etapa=2
            st.rerun()

    elif st.session_state.etapa==2:

        cod=st.text_input("Código Serviço")
        dab=st.date_input("Data abertura",date.today())

        if st.button("Salvar Etapa 2"):
            st.session_state.temp["codigo_servico"]=cod
            st.session_state.temp["data_abertura"]=str(dab)
            st.session_state.etapa=3
            st.rerun()

        if st.button("⬅️ Voltar"):
            st.session_state.etapa=1
            st.rerun()

    elif st.session_state.etapa==3:

        ped=st.text_input("Código Pedido")
        dch=st.date_input("Data chamado",date.today())

        if st.button("Salvar"):
            st.session_state.temp["codigo_pedido"]=ped
            st.session_state.temp["data_chamado"]=str(dch)

            nova_linha=pd.DataFrame([st.session_state.temp],columns=COLUNAS)

            if st.session_state.edit_id is not None:
                df.loc[st.session_state.edit_id]=nova_linha.iloc[0]
            else:
                df=pd.concat([df,nova_linha],ignore_index=True)

            salvar(df)
            st.session_state.df=df
            st.session_state.edit_id=None
            st.session_state.etapa=1
            st.success("Salvo com sucesso!")
            st.rerun()

        if st.button("⬅️ Voltar"):
            st.session_state.etapa=2
            st.rerun()
