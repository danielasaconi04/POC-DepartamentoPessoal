import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco - Kanban Disciplinar", layout="wide")

st.markdown("""
    <style>
    /* Estilização do Kanban */
    .kanban-card {
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 6px solid #333;
        background-color: #ffffff;
        color: #1e1e1e;
    }
    .card-title {
        font-weight: bold;
        font-size: 15px;
        margin-bottom: 4px;
        color: #111;
    }
    .card-info {
        font-size: 13px;
        color: #444;
        margin-bottom: 2px;
    }
    .badge-obra {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        color: white;
        margin-top: 6px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ Ellenco Construções - Gestão Disciplinar DP")
st.subheader("📋 Quadro Kanban Operacional (Faltas Injustificadas)")

# ---------------------------------------------------------
# PALETA DE CORES AUTOMÁTICA POR OBRA / SEÇÃO
# ---------------------------------------------------------
CORES_OBRAS = [
    "#2E86AB", "#A23B52", "#F18F01", "#C73E1D", "#3BCEAC", 
    "#8338EC", "#FF006E", "#3A86FF", "#FB5607", "#06D6A0"
]

def obter_cor_obra(obra, lista_obras):
    if obra not in lista_obras:
        lista_obras.append(obra)
    idx = lista_obras.index(obra) % len(CORES_OBRAS)
    return CORES_OBRAS[idx]

# ---------------------------------------------------------
# LEITURA DA PLANILHA (WF0031.xlsx)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception as e:
        # Dados de backup para demonstração caso o arquivo ainda não esteja no GitHub
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "TOTAL_FALTAS": 2},
            {"CHAPA": 3, "FUNCIONARIO": "DANILO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 3},
            {"CHAPA": 4, "FUNCIONARIO": "ALBERTO", "CARGO": "Auxiliar Administrativo", "SECAO": "DER/PR - PARANÁ", "TOTAL_FALTAS": 4}
        ])

df = carregar_dados()

# Mapeia as colunas conforme a régua disciplinar (1ª Falta, 2ª Falta, etc.)
def classificar_etapa(total_faltas):
    if total_faltas == 1:
        return "1ª Falta (Advertência)"
    elif total_faltas == 2:
        return "2ª Falta (Suspensão 1 a 2 dias)"
    elif total_faltas == 3:
        return "3ª Falta (Suspensão Agravada 3 a 5 dias)"
    else:
        return "4ª Falta (Análise Jurídico / Justa Causa)"

df["ETAPA"] = df["TOTAL_FALTAS"].apply(classificar_etapa)

# Mapeia obras únicas para associar cores
obras_unicas = list(df["SECAO"].unique())

# ---------------------------------------------------------
# MONTAGEM VISUAL DAS COLUNAS KANBAN
# ---------------------------------------------------------
etapas_kanban = [
    "1ª Falta (Advertência)",
    "2ª Falta (Suspensão 1 a 2 dias)",
    "3ª Falta (Suspensão Agravada 3 a 5 dias)",
    "4ª Falta (Análise Jurídico / Justa Causa)"
]

cols = st.columns(4)

for i, etapa in enumerate(etapas_kanban):
    with cols[i]:
        st.markdown(f"### {etapa}")
        df_etapa = df[df["ETAPA"] == etapa]
        
        if df_etapa.empty:
            st.caption("Nenhum colaborador nesta etapa.")
        
        for _, row in df_etapa.iterrows():
            obra_nome = str(row.get("SECAO", "NÃO INFORMADA"))
            cor_card = obter_cor_obra(obra_nome, obras_unicas)
            
            # HTML customizado do cartão do colaborador
            card_html = f"""
            <div class="kanban-card" style="border-left-color: {cor_card};">
                <div class="card-title">👤 {row['FUNCIONARIO']}</div>
                <div class="card-info"><b>Chapa:</b> {row['CHAPA']}</div>
                <div class="card-info"><b>Cargo:</b> {row.get('CARGO', '-')}</div>
                <div class="card-info"><b>Total de Faltas:</b> {row['TOTAL_FALTAS']}</div>
                <span class="badge-obra" style="background-color: {cor_card};">{obra_nome}</span>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# LEGENDA DAS OBRAS
# ---------------------------------------------------------
st.divider()
st.subheader("🎨 Legenda de Cores por Obra/Seção")
cols_legenda = st.columns(len(obras_unicas) if len(obras_unicas) > 0 else 1)

for idx, obra in enumerate(obras_unicas):
    cor = obter_cor_obra(obra, obras_unicas)
    with cols_legenda[idx % len(cols_legenda)]:
        st.markdown(f'<span style="color:{cor}; font-size:20px;">■</span> **{obra}**', unsafe_allow_html=True)
