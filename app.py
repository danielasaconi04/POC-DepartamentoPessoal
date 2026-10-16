import streamlit as st
import pandas as pd
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (WIDE MODE)
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco - Kanban Disciplinar", layout="wide")

# Estilização CSS para cartões compactos e elegantes
st.markdown("""
    <style>
    .kanban-card {
        border-radius: 6px;
        padding: 8px 10px;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        border-left: 5px solid #333;
        background-color: #ffffff;
        color: #1e1e1e;
    }
    .card-title {
        font-weight: bold;
        font-size: 13px;
        margin-bottom: 2px;
        color: #111;
    }
    .card-info {
        font-size: 11px;
        color: #555;
        margin-bottom: 1px;
    }
    .badge-obra {
        display: inline-block;
        padding: 1px 6px;
        border-radius: 3px;
        font-size: 10px;
        font-weight: bold;
        color: white;
        margin-top: 4px;
    }
    /* Compactar espaçamentos do Streamlit */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ Ellenco Construções - Gestão Disciplinar DP")

# ---------------------------------------------------------
# LEITURA DA PLANILHA (WF0031.xlsx)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception as e:
        # Dados de fallback caso o Excel não esteja carregado
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "TOTAL_FALTAS": 2},
            {"CHAPA": 3, "FUNCIONARIO": "DANILO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 3},
            {"CHAPA": 4, "FUNCIONARIO": "ALBERTO", "CARGO": "Auxiliar Administrativo", "SECAO": "DER/PR - PARANÁ", "TOTAL_FALTAS": 4}
        ])

df = carregar_dados()

# Mapeia as etapas do processo disciplinar
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

# ---------------------------------------------------------
# BARRA LATERAL - FILTROS DE PESQUISA
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Pesquisa")

# Filtro de Busca por Nome ou Chapa
busca_texto = st.sidebar.text_input("Pesquisar Colaborador / Chapa", "")

# Filtro por Seção / Obra
secoes_disponiveis = sorted(df["SECAO"].dropna().unique().tolist())
filtro_secao = st.sidebar.multiselect("Filtrar por Obra / Seção", options=secoes_disponiveis, default=secoes_disponiveis)

# Filtro por Cargo
cargos_disponiveis = sorted(df["CARGO"].dropna().unique().tolist())
filtro_cargo = st.sidebar.multiselect("Filtrar por Cargo", options=cargos_disponiveis, default=cargos_disponiveis)

# Aplicando os filtros ao DataFrame
df_filtrado = df.copy()

if busca_texto:
    busca_upper = busca_texto.upper()
    df_filtrado = df_filtrado[
        df_filtrado["FUNCIONARIO"].str.upper().str.contains(busca_upper, na=False) |
        df_filtrado["CHAPA"].astype(str).str.contains(busca_upper, na=False)
    ]

if filtro_secao:
    df_filtrado = df_filtrado[df_filtrado["SECAO"].isin(filtro_secao)]

if filtro_cargo:
    df_filtrado = df_filtrado[df_filtrado["CARGO"].isin(filtro_cargo)]

# ---------------------------------------------------------
# PALETA DE CORES DINÂMICA POR OBRA
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

obras_unicas = list(df["SECAO"].unique())

# ---------------------------------------------------------
# MONTAGEM DO KANBAN COMPACTO (4 COLUNAS)
# ---------------------------------------------------------
st.markdown("### 📊 Quadro Kanban Operacional")

etapas_kanban = [
    "1ª Falta (Advertência)",
    "2ª Falta (Suspensão 1 a 2 dias)",
    "3ª Falta (Suspensão Agravada 3 a 5 dias)",
    "4ª Falta (Análise Jurídico / Justa Causa)"
]

cols = st.columns(4)

for i, etapa in enumerate(etapas_kanban):
    with cols[i]:
        # Cabeçalho da coluna com contador de colaboradores
        df_etapa = df_filtrado[df_filtrado["ETAPA"] == etapa]
        st.markdown(f"**{etapa}** ({len(df_etapa)})")
