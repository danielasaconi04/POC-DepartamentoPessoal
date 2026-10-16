import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco - Kanban Disciplinar", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .card-kanban-solido {
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .card-nome-solido {
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 6px;
        color: #ffffff !important;
        text-shadow: 0px 1px 2px rgba(0,0,0,0.3);
    }
    .card-detalhe-solido {
        font-size: 12px;
        margin-bottom: 3px;
        color: #ffffff !important;
        opacity: 0.95;
    }
    .card-tag-obra-solida {
        display: inline-block;
        background-color: rgba(0, 0, 0, 0.25);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        margin-top: 6px;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.4);
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
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "TOTAL_FALTAS": 1}
        ])

df = carregar_dados()

# Mapeamento limpo sem quebra de linhas nas aspas
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
# PALETA DE CORES VIBRANTES POR OBRA
# ---------------------------------------------------------
PALETA_CORES_VIBRANTES = {
    "DER/SP - TATUI": "#FF7A6C",
    "CCR - SÃO ROQUE": "#FFA500",
    "DER/PR - PARANÁ": "#4CAF50",
    "CONSERVA": "#2196F3",
    "SAO ROQUE/SP": "#9C27B0",
    "SAO ROQUE": "#00BCD4"
}

CORES_SOLIDADAS_RESERVA = ["#FF7A6C", "#FFA500", "#4CAF50", "#2196F3", "#9C27B0", "#00BCD4", "#E91E63", "#3F51B5"]

def obter_cor_solida_obra(obra):
    obra_str = str(obra).strip()
    if obra_str in PALETA_CORES_VIBRANTES:
        return PALETA_CORES_VIBRANTES[obra_str]
    idx = abs(hash(obra_str)) % len(CORES_SOLIDADAS_RESERVA)
    return CORES_SOLIDADAS_RESERVA[idx]

# ---------------------------------------------------------
# BARRA LATERAL - FILTROS DE PESQUISA
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Pesquisa")

busca_texto = st.sidebar.text_input("Pesquisar Colaborador / Chapa", "")

secoes_disponiveis = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
filtro_secao = st.sidebar.multiselect("Filtrar por Obra / Seção", options=secoes_disponiveis, default=secoes_disponiveis)

cargos_disponiveis = sorted(df["CARGO"].dropna().astype(str).unique().tolist())
filtro_cargo = st.sidebar.multiselect("Filtrar por Cargo", options=cargos_disponiveis, default=cargos_disponiveis)

df_filtrado = df.copy()

if busca_texto:
    busca_upper = busca_texto.upper()
    df_filtrado = df_filtrado[
        df_filtrado["FUNCIONARIO"].astype(str).str.upper().str.contains(busca_upper, na=False) |
        df_filtrado["CHAPA"].astype(str).str.contains(busca_upper, na=False)
    ]

if filtro_secao:
    df_filtrado = df_filtrado[df_filtrado["SECAO"].astype(str).isin(filtro_secao)]

if filtro_cargo:
    df_filtrado = df_filtrado[df_filtrado["CARGO"].astype(str).isin(filtro_cargo)]

# ---------------------------------------------------------
# QUADRO KANBAN
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
        df_etapa = df_filtrado[df_filtrado["ETAPA"] == etapa]
        
        st.subheader(f"{etapa}")
        st.caption(f"👥 Total: **{len(df_etapa)}** colaborador(es)")
        st.markdown("---")
        
        if df_etapa.empty:
            st.info("Nenhum colaborador nesta etapa.")
        
        for _, row in df_etapa.iterrows():
            obra_nome = str(row.get("SECAO", "-")).strip()
            cor_fundo = obter_cor_solida_obra(obra_nome)
            
            card_html = f"""<div class="card-kanban-solido" style="background-color: {cor_fundo};"><div class="card-nome-solido">👤 {row['FUNCIONARIO']}</div><div class="card-detalhe-solido">🔢 <b>Chapa:</b> {row['CHAPA']} | <b>Faltas:</b> {row['TOTAL_FALTAS']}</div><div class="card-detalhe-solido">💼 <b>Cargo:</b> {row.get('CARGO', '-')}</div><div class="card-tag-obra-solida">🏗️ {obra_nome}</div></div>"""
            st.markdown(card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# LEGENDA DE CORES NO RODAPÉ
# ---------------------------------------------------------
st.divider()
st.markdown("##### 🎨 Legenda de Cores por Obra / Seção")

obras_presentes = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
cols_legenda = st.columns(min(len(obras_presentes), 6) if len(obras_presentes) > 0 else 1)

for idx, obra in enumerate(obras_presentes):
    cor = obter_cor_solida_obra(obra)
    with cols_legenda[idx % len(cols_legenda)]:
        st.markdown(f'<div style="background-color:{cor}; padding:6px 10px; border-radius:6px; text-align:center; color:white; font-weight:bold;"><small>{obra}</small></div>', unsafe_allow_html=True)
