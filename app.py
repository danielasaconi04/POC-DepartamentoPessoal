import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (WIDE MODE)
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco - Kanban Disciplinar", layout="wide")

# Estilização CSS para cartões com fundo preenchido por cor
st.markdown("""
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .card-kanban-obra {
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        color: #111111;
        font-family: sans-serif;
    }
    .card-nome {
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 4px;
    }
    .card-detalhe {
        font-size: 12px;
        margin-bottom: 2px;
        opacity: 0.9;
    }
    .card-tag-obra {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.7);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        margin-top: 4px;
        color: #000000;
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
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "TOTAL_FALTAS": 1},
            {"CHAPA": 3, "FUNCIONARIO": "DANILO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 1},
            {"CHAPA": 4, "FUNCIONARIO": "ALBERTO", "CARGO": "Auxiliar Administrativo", "SECAO": "DER/PR - PARANÁ", "TOTAL_FALTAS": 1}
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
# PALETA DE CORES SUAVES E VISÍVEIS POR OBRA (PASTEL/HIGHLIGHT)
# ---------------------------------------------------------
PALETA_CORES_OBRA = {
    "DER/SP - TATUI": "#E3F2FD",      # Azul Claro
    "CCR - SÃO ROQUE": "#FFF3E0",     # Laranja Claro
    "DER/PR - PARANÁ": "#E8F5E9",     # Verde Claro
    "CONSERVA": "#F3E5F5",             # Roxo Claro
    "SAO ROQUE/SP": "#FFEBEE",         # Rosa Claro
    "SAO ROQUE": "#FFF8E1"             # Amarelo Claro
}

CORES_PADRAO = ["#E3F2FD", "#FFF3E0", "#E8F5E9", "#F3E5F5", "#FFEBEE", "#FFF8E1", "#E0F2F1", "#FCE4EC"]

def obter_cor_fundo_obra(obra):
    obra_str = str(obra).strip()
    if obra_str in PALETA_CORES_OBRA:
        return PALETA_CORES_OBRA[obra_str]
    # Se for uma obra nova, gera uma cor pastel baseada no hash do nome
    idx = abs(hash(obra_str)) % len(CORES_PADRAO)
    return CORES_PADRAO[idx]

# ---------------------------------------------------------
# BARRA LATERAL - FILTROS DE PESQUISA
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Pesquisa")

busca_texto = st.sidebar.text_input("Pesquisar Colaborador / Chapa", "")

secoes_disponiveis = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
filtro_secao = st.sidebar.multiselect(
    "Filtrar por Obra / Seção", 
    options=secoes_disponiveis, 
    default=secoes_disponiveis
)

cargos_disponiveis = sorted(df["CARGO"].dropna().astype(str).unique().tolist())
filtro_cargo = st.sidebar.multiselect(
    "Filtrar por Cargo", 
    options=cargos_disponiveis, 
    default=cargos_disponiveis
)

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
            cor_fundo = obter_cor_fundo_obra(obra_nome)
            
            # HTML do cartão totalmente colorido de acordo com a obra
            card_html = f"""
            <div class="card-kanban-obra" style="background-color: {cor_fundo}; border: 1px solid rgba(0,0,0,0.1);">
                <div class="card-nome">👤 {row['FUNCIONARIO']}</div>
                <div class="card-detalhe">🔢 <b>Chapa:</b> {row['CHAPA']} | <b>Faltas:</b> {row['TOTAL_FALTAS']}</div>
                <div class="card-detalhe">💼 <b>Cargo:</b> {row.get('CARGO', '-')}</div>
                <div class="card-tag-obra">🏗️ {obra_nome}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# LEGENDA DE CORES NO RODAPÉ
# ---------------------------------------------------------
st.divider()
st.markdown("##### 🎨 Legenda de Cores das Obras")

obras_presentes = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
cols_legenda = st.columns(min(len(obras_presentes), 6) if len(obras_presentes) > 0 else 1)

for idx, obra in enumerate(obras_presentes):
    cor = obter_cor_fundo_obra(obra)
    with cols_legenda[idx % len(cols_legenda)]:
        st.markdown(
            f'<div style="background-color:{cor}; padding:4px 8px; border-radius:4px; text-align:center; border:1px solid #ccc;">'
            f'<small><b>{obra}</b></small></div>', 
            unsafe_allow_html=True
        )
