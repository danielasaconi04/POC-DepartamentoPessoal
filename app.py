import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

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
        margin-bottom: 8px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        color: #ffffff !important;
        font-family: sans-serif;
    }
    .card-nome-solido {
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 4px;
        color: #ffffff !important;
    }
    .card-detalhe-solido {
        font-size: 12px;
        margin-bottom: 3px;
        color: #ffffff !important;
    }
    .card-tag-obra-solida {
        display: inline-block;
        background-color: rgba(0, 0, 0, 0.25);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        margin-top: 4px;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏗️ Ellenco Construções - Gestão Disciplinar DP")

# ---------------------------------------------------------
# LEITURA DOS DADOS (WF0031.xlsx)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception:
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "LUCAS", "CARGO": "Ajudante geral", "SECAO": "SAO ROQUE", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "CARLOS", "CARGO": "Ajudante geral", "SECAO": "SAO ROQUE/SP", "DATA_1": "18/09/2026", "DATA_2": "25/09/2026", "TOTAL_FALTAS": 2},
            {"CHAPA": 3, "FUNCIONARIO": "JOÃO", "CARGO": "Ajudante geral", "SECAO": "CONSERVA", "DATA_1": "20/07/2026", "DATA_2": "03/09/2026", "DATA_3": "15/09/2026", "TOTAL_FALTAS": 3}
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
# FUNÇÃO DE TRATAMENTO DE TEXTO
# ---------------------------------------------------------
def limpar(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# ---------------------------------------------------------
# GERADOR DE PDF DAS MINUTAS OFICIAIS ELLENCO
# ---------------------------------------------------------
def gerar_pdf_ellenco(nome, chapa, cargo, obra, total_faltas, data_1, data_2, data_3):
    pdf = FPDF()
    pdf.add_page()
    
    nome_clean = limpar(nome)
    cargo_clean = limpar(cargo)
    obra_clean = limpar(obra)
    
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "ELLENCO CONSTRUCOES", 0, 1, "L")
    pdf.ln(2)
    
    pdf.set_font("Arial", "B", 11)
    if total_faltas == 1:
        pdf.cell(0, 6, "CARTA DE ADVERTENCIA DISCIPLINAR", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome_clean}, ocupante do cargo de {cargo_clean} da obra {obra_clean}", 0, 1)
        pdf.cell(0, 6, "Referente: 1a FALTA INJUSTIFICADA ISOLADA", 0, 1)
        pdf.ln(4)
        
        d1 = str(data_1) if pd.notna(data_1) else "28/09/2026"
        t = (
            f"A empresa Ellenco Construcoes registra, por meio deste documento, a aplicacao de ADVERTENCIA DISCIPLINAR, em razao de ausencia injustificada ao trabalho.\n\n"
            f"Conforme registros de frequencia, foi constatada a ausencia do empregado no dia {d1} sem que houvesse apresentacao de justificativa legalmente valida ou documento apto a justificar a ausencia.\n\n"
            f"A referida ausencia ocasionou o nao cumprimento da jornada de trabalho prevista para a respectiva data, em desacordo com as obrigacoes decorrentes do contrato de trabalho e das normas internas da empresa.\n\n"
            f"Diante do ocorrido, a empresa aplica a presente ADVERTENCIA DISCIPLINAR, de carater pedagogico.\n\n"
            f"Fica o empregado ciente de que a repeticao de faltas injustificadas podera ensejar a adocao de medidas disciplinares mais severas, inclusive suspensao disciplinar e rescisao do contrato por justa causa (Art. 482 da CLT)."
        )
        pdf.multi_cell(0, 5, limpar(t))
        
    elif total_faltas == 2:
        pdf.cell(0, 7, "CARTA DE SUSPENSAO DISCIPLINAR", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome_clean}, ocupante do cargo de {cargo_clean} da obra {obra_clean}", 0, 1)
        pdf.cell(0, 6, "Referente: Aplicacao de Suspensao Disciplinar (1 dia util)", 0, 1)
        pdf.ln(4)
        
        d2 = str(data_2) if pd.notna(data_2) else "25/09/2026"
        d1 = str(data_1) if pd.notna(data_1) else "18/09/2026"
        t = (
            f"A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR pelo periodo de 1 dia util, em razao da reincidencia reiterada em faltas injustificadas ao trabalho.\n\n"
            f"Foi constatada a ausencia do empregado no dia {d2}, sem apresentacao de justificativa legal valida.\n\n"
            f"Registra-se que o empregado ja havia sido penalizado anteriormente com ADVERTENCIA DISCIPLINAR em razao de falta ocorrida em {d1}.\n\n"
            f"Diante da reincidencia, fica aplicada a presente SUSPENSAO DISCIPLINAR, pelo periodo de 1 dia util.\n\n"
            f"O empregado fica formalmente advertido de que a repeticao podera resultar em rescisao do contrato por justa causa."
        )
        pdf.multi_cell(0, 5, limpar(t))
        
    elif total_faltas == 3:
        pdf.cell(0, 7, "CARTA DE SUSPENSAO DISCIPLINAR AGRAVADA", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome_clean}, ocupante do cargo de {cargo_clean} da obra {obra_clean}", 0, 1)
        pdf.cell(0, 6, "Referente: Aplicacao de Suspensao Disciplinar Agravada (3 dias uteis)", 0, 1)
        pdf.ln(4)
        
        d3 = str(data_3) if pd.notna(data_3) else "15/09/2026"
        d1 = str(data_1) if pd.notna(data
