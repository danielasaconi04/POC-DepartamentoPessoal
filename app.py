import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (LAYOUT EMPRESARIAL / TONS NUDES)
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco Construções - Gestão Disciplinar", layout="wide")

st.markdown("""
    <style>
    /* Cores Globais e Fundo Corporativo */
    .stApp {
        background-color: #F7F5F0;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Topo / Header Empresarial */
    .header-empresarial {
        background-color: #2C3333;
        padding: 20px 30px;
        border-radius: 6px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        border-bottom: 4px solid #A3865E;
    }
    .header-titulo {
        color: #F7F5F0;
        font-size: 24px;
        font-weight: 700;
        margin: 0;
    }
    .header-sub {
        color: #C2B6A9;
        font-size: 13px;
        margin: 0;
    }
    
    /* Cards do Kanban em Tons Nudes / Sóbrios */
    .card-kanban-nude {
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        color: #2C3333 !important;
        font-family: sans-serif;
    }
    .card-nome-nude {
        font-weight: 700;
        font-size: 14px;
        margin-bottom: 6px;
        color: #1A1C1C !important;
    }
    .card-detalhe-nude {
        font-size: 12px;
        margin-bottom: 4px;
        color: #3F4444 !important;
    }
    .card-tag-obra-nude {
        display: inline-block;
        background-color: rgba(163, 134, 94, 0.15);
        color: #5C4A32 !important;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        margin-top: 6px;
        border: 1px solid rgba(163, 134, 94, 0.3);
    }
    
    /* Colunas do Kanban */
    div[data-testid="column"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E5E0D8;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CABEÇALHO EMPRESARIAL COM NOME / LOGO ELLENCO
# ---------------------------------------------------------
st.markdown("""
    <div class="header-empresarial">
        <div>
            <p class="header-titulo">🏗️ ELLENCO CONSTRUÇÕES</p>
            <p class="header-sub">Departamento Pessoal — Gestão Disciplinar Corporativa</p>
        </div>
        <div style="text-align: right;">
            <span style="background-color: #A3865E; color: white; padding: 6px 14px; border-radius: 4px; font-weight: bold; font-size: 12px; letter-spacing: 1px;">PORTAL DP</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LEITURA DA PLANILHA CORPORATIVA (WF0031.xlsx)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception:
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 2}
        ])

if "df_dados" not in st.session_state:
    st.session_state.df_dados = carregar_dados()

df = st.session_state.df_dados

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
# TRATAMENTO DE TEXTO (LATIN-1 ENCODING)
# ---------------------------------------------------------
def limpar(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# ---------------------------------------------------------
# GERADOR DE PDF FIEL COM CAIXAS, ENDEREÇOS E ART. 482
# ---------------------------------------------------------
def gerar_pdf_perfeito_ellenco(nome, chapa, cargo, obra, total_faltas, data_1, data_2, data_3):
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    
    nc = limpar(nome)
    cc = limpar(cargo)
    oc = limpar(obra)
    
    # Cabeçalho Ellenco
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(44, 51, 51)
    pdf.cell(130, 8, "", 0, 0)
    pdf.cell(50, 8, "Ellenco", 0, 1, "R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    
    # Caixa de Título
    pdf.set_font("Arial", "B", 11)
    pdf.rect(10, 20, 190, 8)
    pdf.set_xy(10, 21)
    if total_faltas == 1:
        pdf.cell(190, 6, "CARTA DE ADVERTENCIA DISCIPLINAR", 0, 1, "C")
    elif total_faltas in [2, 3]:
