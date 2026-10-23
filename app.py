import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (LAYOUT CORPORATIVO COM TRANSPARÊNCIAS)
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco Construções - Gestão Disciplinar", layout="wide")

st.markdown("""
    <style>
    /* Fundo Geral */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Cabeçalho Empresarial Ellenco */
    .header-empresarial {
        background-color: #0F172A;
        padding: 18px 25px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-bottom: 4px solid #1E40AF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-titulo {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .header-sub {
        color: #94A3B8;
        font-size: 13px;
        margin: 0;
    }
    
    /* Reformulação da Barra de Filtros Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        color: #FFFFFF !important;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 6px;
    }
    
    /* Cartões / Catálogos do Kanban com Cores Suaves e Transparência (RGBA) */
    .card-kanban-suave {
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        font-family: sans-serif;
        backdrop-filter: blur(4px);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card-kanban-suave:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.08);
    }
    .card-nome-suave {
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 6px;
        color: #0F172A !important;
    }
    .card-detalhe-suave {
        font-size: 12px;
        margin-bottom: 4px;
        color: #334155 !important;
    }
    .card-tag-obra-suave {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.7);
        color: #0F172A !important;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        margin-top: 6px;
        border: 1px solid rgba(15, 23, 42, 0.15);
    }
    
    /* Estilo das Colunas do Kanban */
    div[data-testid="column"] {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CABEÇALHO EMPRESARIAL
# ---------------------------------------------------------
st.markdown("""
    <div class="header-empresarial">
        <div>
            <p class="header-titulo">🏗️ ELLENCO CONSTRUÇÕES</p>
            <p class="header-sub">Departamento Pessoal — Gestão Disciplinar Corporativa</p>
        </div>
        <div style="text-align: right;">
            <span style="background-color: #1E40AF; color: white; padding: 6px 14px; border-radius: 4px; font-weight: bold; font-size: 12px; letter-spacing: 1px;">PORTAL DP</span>
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
    pdf.set_text_color(15, 23, 42)
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
        pdf.cell(190, 6, "CARTA DE SUSPENSAO DISCIPLINAR", 0, 1, "C")
    else:
        pdf.cell(190, 6, "ENCAMINHAMENTO AO DEPARTAMENTO JURIDICO", 0, 1, "C")
        
    pdf.ln(4)
    
    # Caixa Principal do Texto
    pdf.rect(10, 30, 190, 105)
    pdf.set_xy(12, 32)
    
    pdf.set_font("Arial", "B", 9.5)
    pdf.cell(0, 5, limpar(f"Ilmo(a) Sr(a): {nc}, ocupante do cargo de {cc} da obra {oc}"), 0, 1, "L")
    pdf.set_x(12)
    
    if total_faltas == 1:
        pdf.cell(0, 5, "Referente: 1a FALTA INJUSTIFICADA ISOLADA", 0, 1, "L")
        pdf.ln(2)
        d1 = str(data_1) if pd.notna(data_1) else "28/09/2026"
        p1 = "A empresa Ellenco Construcoes registra, por meio deste documento, a aplicacao de ADVERTENCIA DISCIPLINAR, em razao de ausencia injustificada ao trabalho."
        p2 = f"Conforme registros de frequencia, foi constatada a ausencia do empregado no dia {d1} sem que houvesse apresentacao de justificativa legalmente valida ou documento apto a justificar a ausencia."
        p3 = "A referida ausencia ocasionou o nao cumprimento da jornada de trabalho prevista para a respectiva data, em desacordo com as obrigacoes decorrentes do contrato de trabalho e das normas internas da empresa."
        p4 = "Registra-se que, ate o momento da aplicacao desta penalidade, nao foi apresentada justificativa legal capaz de afastar a caracterizacao da falta."
        p5 = "Diante do ocorrido, a empresa aplica a presente ADVERTENCIA DISCIPLINAR, de carater pedagogico, para que o(a) empregado(a) observe rigorosamente sua jornada de trabalho e comunique previamente a empresa eventual impossibilidade de comparecimento, apresentando, quando cabivel, a respectiva justificativa."
        p6 = "Fica o empregado ciente de que a repeticao de faltas injustificadas podera ensejar a adocao de medidas disciplinares mais severas, de acordo com a gravidade e a reiteracao da conduta, inclusive suspensao disciplinar e, em situacoes que assim o justifiquem, a rescisao do contrato por justa causa, nos termos do art. 482 da CLT."
        texto = f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}\n\n{p6}"
    elif total_faltas == 2:
        pdf.cell(0, 5, "Referente: Aplicacao de Suspensao Disciplinar", 0, 1, "L")
        pdf.ln(2)
        d_atual = str(data_2) if pd.notna(data_2) else "25/09/2026"
        d_ant = str(data_1) if pd.notna(data_1) else "18/09/2026"
        p1 = "A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR pelo periodo de 1 dia util, em razao da reincidencia reiterada em faltas injustificadas ao trabalho."
        p2 = f"Foi constatada a ausencia do empregado nos dias {d_atual}, sem apresentacao de justificativa legal valida."
        p3 = f"Registra-se que o empregado ja havia sido penalizado anteriormente com ADVERTENCIA DISCIPLINAR, aplicada em {d_ant}, em razao de falta injustificada ocorrida."
        p4 = "Apesar da orientacao e da penalidade anteriormente aplicada, houve nova ocorrencia de ausencia injustificada, demonstrando a repeticao da conduta."
        p5 = "Diante da reincidencia, fica aplicada a presente SUSPENSAO DISCIPLINAR, pelo periodo de 1 dia util, sem prejuizo dos efeitos legais decorrentes da suspensao."
        p6 = "O empregado fica formalmente advertido de que a repeticao de faltas injustificadas podera resultar na aplicacao de penalidades disciplinares mais severas, inclusive suspensao por periodo superior e rescisao do contrato por justa causa."
        texto = f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}\n\n{p6}"
    elif total_faltas == 3:
        pdf.cell(0, 5, "Referente: Aplicacao de Suspensao Disciplinar Agravada", 0, 1, "L")
        pdf.ln(2)
        d3 = str(data_3) if pd.notna(data_3) else "15/09/2026"
        d1 = str(data_1) if pd.notna(data_1) else "20/07/2026"
        d2 = str(data_2) if pd.notna(data_2) else "03/09/2026"
        p1 = "A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR AGRAVADA pelo periodo de 3 dias uteis, em razao da reincidencia reiterada em faltas injustificadas ao trabalho."
        p2 = f"Conforme registros de frequencia, foi constatada nova ausencia injustificada do empregado no dia {d3}, sem apresentacao de justificativa legalmente valida."
        p3 = f"A presente ocorrencia nao constitui fato isolado. O empregado ja foi anteriormente penalizado por faltas injustificadas, tendo recebido:\na) Advertencia disciplinar, aplicada em {d1}, em razao da ausencia anterior; e\nb) Suspensao disciplinar de 1 dia, aplicada em {d2}, em razao da ausencia anterior."
        p4 = "Mesmo apos as medidas disciplinares anteriormente aplicadas e a ciencia expressa acerca da necessidade de observancia da jornada de trabalho, ocorreu nova falta injustificada."
        p5 = "Diante da persistencia da conduta, a empresa aplica a presente SUSPENSAO DISCIPLINAR DE 3 DIAS UTEIS."
        p6 = "O empregado fica expressamente ciente de que a continuidade ou reiteracao de faltas injustificadas podera ensejar a adocao de medida disciplinar maxima, inclusive a rescisao do contrato por justa causa."
        texto = f"{p1}\n\n{p2}\n\n{p3}\n\n{p4}\n\n{p5}\n\n{p6}"
    else:
        pdf.cell(0, 5, "Referente: Encaminhamento Juridico - Justa Causa", 0, 1, "L")
