import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (WIDE MODE)
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco - Kanban Disciplinar", layout="wide")

# Estilização CSS leve para otimizar os espaços
st.markdown("""
    <style>
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
        # Dados de fallback para testes caso o arquivo não seja encontrado
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
# BARRA LATERAL - FILTROS DE PESQUISA (COM TRATAMENTO)
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Pesquisa")

# 1. Busca por texto
busca_texto = st.sidebar.text_input("Pesquisar Colaborador / Chapa", "")

# 2. Filtro por Seção / Obra (padrão: todas selecionadas)
secoes_disponiveis = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
filtro_secao = st.sidebar.multiselect(
    "Filtrar por Obra / Seção", 
    options=secoes_disponiveis, 
    default=secoes_disponiveis
)

# 3. Filtro por Cargo (padrão: todos selecionados)
cargos_disponiveis = sorted(df["CARGO"].dropna().astype(str).unique().tolist())
filtro_cargo = st.sidebar.multiselect(
    "Filtrar por Cargo", 
    options=cargos_disponiveis, 
    default=cargos_disponiveis
)

# Aplicação dos Filtros
df_filtrado = df.copy()

if busca_texto:
    busca_upper = busca_texto.upper()
    df_filtrado = df_filtrado[
        df_filtrado["FUNCIONARIO"].astype(str).str.upper().str.contains(busca_upper, na=False) |
        df_filtrado["CHAPA"].astype(str).str.contains(busca_upper, na=False)
    ]

# Aplica filtro de seção apenas se algo for selecionado
if filtro_secao:
    df_filtrado = df_filtrado[df_filtrado["SECAO"].astype(str).isin(filtro_secao)]

# Aplica filtro de cargo apenas se algo for selecionado
if filtro_cargo:
    df_filtrado = df_filtrado[df_filtrado["CARGO"].astype(str).isin(filtro_cargo)]

# ---------------------------------------------------------
# MONTAGEM DO KANBAN VISÍVEL (4 COLUNAS NATIVAS)
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
        
        # Título da coluna com badge de contagem
        st.subheader(f"{etapa}")
        st.caption(f"👥 Total: **{len(df_etapa)}** colaborador(es)")
        st.markdown("---")
        
        if df_etapa.empty:
            st.info("Nenhum colaborador nesta etapa.")
        
        for _, row in df_etapa.iterrows():
            # Cartão usando container nativo do Streamlit (Garante renderização visível)
            with st.container(border=True):
                st.markdown(f"👤 **{row['FUNCIONARIO']}**")
                st.markdown(f"🔢 **Chapa:** {row['CHAPA']} | **Faltas:** {row['TOTAL_FALTAS']}")
                st.markdown(f"💼 **Cargo:** {row.get('CARGO', '-')}")
                st.markdown(f"🏗️ **Obra:** `{row.get('SECAO', '-')}`")

# ---------------------------------------------------------
# RESUMO DAS OBRAS ABAIXO DO KANBAN
# ---------------------------------------------------------
st.divider()
st.markdown("##### 📍 Obras/Seções Selecionadas")
if filtro_secao:
    st.write(" | ".join([f"`{s}`" for s in filtro_secao]))
