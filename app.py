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
# LEITURA E CARREGAMENTO DOS DADOS (WF0031.xlsx)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception:
        # Fallback de segurança para demonstração em caso de falha de arquivo
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "LUCAS", "CARGO": "Ajudante geral", "SECAO": "SAO ROQUE", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "CARLOS", "CARGO": "Ajudante geral", "SECAO": "SAO ROQUE/SP", "DATA_1": "18/09/2026", "DATA_2": "25/09/2026", "TOTAL_FALTAS": 2},
            {"CHAPA": 3, "FUNCIONARIO": "JOÃO", "CARGO": "Ajudante geral", "SECAO": "CONSERVA", "DATA_1": "20/07/2026", "DATA_2": "03/09/2026", "DATA_3": "15/09/2026", "TOTAL_FALTAS": 3}
        ])

if "df_dados" not in st.session_state:
    st.session_state.df_dados = carregar_dados()

df = st.session_state.df_dados

# Mapeia as colunas conforme a regra disciplinar
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
# GERADOR DE PDF DAS MINUTAS OFICIAIS ELLENCO
# ---------------------------------------------------------
def limpar(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

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
            f"A empresa Ellenco Construcoes registra, por meio deste documento, a aplicacao de ADVERTENCIA DISCIPLINAR, "
            f"em razao de ausencia injustificada ao trabalho.\n\n"
            f"Conforme registros de frequencia, foi constatada a ausencia do empregado no dia {d1} sem que houvesse "
            f"apresentacao de justificativa legalmente valida ou documento apto a justificar a ausencia.\n\n"
            f"A referida ausencia ocasionou o nao cumprimento da jornada de trabalho prevista para a respectiva data, em "
            f"desacordo com as obrigacoes decorrentes do contrato de trabalho e das normas internas da empresa.\n\n"
            f"Diante do ocorrido, a empresa aplica a presente ADVERTENCIA DISCIPLINAR, de carater pedagogico.\n\n"
            f"Fica o empregado ciente de que a repeticao de faltas injustificadas podera ensejar a adocao de medidas "
            f"disciplinares mais severas, inclusive suspensao disciplinar e rescisao do contrato por justa causa (Art. 482 da CLT)."
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
            f"A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR "
            f"pelo periodo de 1 dia util, em razao da reincidencia reiterada em faltas injustificadas ao trabalho.\n\n"
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
        d1 = str(data_1) if pd.notna(data_1) else "20/07/2026"
        d2 = str(data_2) if pd.notna(data_2) else "03/09/2026"
        t = (
            f"A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR AGRAVADA "
            f"pelo periodo de 3 dias uteis, em razao da reincidencia reiterada em faltas injustificadas ao trabalho.\n\n"
            f"Conforme registros de frequencia, foi constatada nova ausencia injustificada do empregado em {d3}.\n\n"
            f"A presente ocorrencia nao constitui fato isolado. O empregado ja foi anteriormente penalizado por faltas injustificadas, tendo recebido:\n"
            f"a) Advertencia disciplinar em razao da ausencia em {d1}; e\n"
            f"b) Suspensao disciplinar de 1 dia em razao da ausencia em {d2}.\n\n"
            f"Diante da persistencia da conduta, a empresa aplica a presente SUSPENSAO DISCIPLINAR DE 3 DIAS UTEIS.\n\n"
            f"O empregado fica ciente de que a continuidade podera ensejar rescisao por justa causa (Art. 482 da CLT)."
        )
        pdf.multi_cell(0, 5, limpar(t))
        
    else:
        pdf.cell(0, 7, "ENCAMINHAMENTO AO JURIDICO - JUSTA CAUSA", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome_clean}, ocupante do cargo de {cargo_clean} da obra {obra_clean}", 0, 1)
        pdf.ln(4)
        t = "Encaminhamento formal ao Departamento Juridico para analise de Rescisao por Justa Causa (Art. 482, 'e' da CLT)."
        pdf.multi_cell(0, 5, limpar(t))
        
    pdf.ln(6)
    pdf.cell(0, 5, "Sorocaba, SP", 0, 1, "R")
    pdf.ln(6)
    
    pdf.cell(90, 5, "Ciente do(a) Empregado(a):", 0, 1, "L")
    pdf.ln(6)
    pdf.cell(90, 5, "_______________________________________", 0, 0, "L")
    pdf.cell(90, 5, "_______________________________________", 0, 1, "R")
    pdf.cell(90, 5, "Testemunha 1", 0, 0, "L")
    pdf.cell(90, 5, "Testemunha 2", 0, 1, "R")
    pdf.ln(6)
    
    pdf.set_font("Arial", "B", 7.5)
    pdf.cell(0, 3.5, "Para seu conhecimento, transcrevemos abaixo o Artigo 482 da CLT:", 0, 1)
    pdf.set_font("Arial", "", 6.5)
    clt_text = (
        "Art. 482 Constituem justa causa para rescisao do contrato de trabalho pelo empregador:\n"
        "a) ato de improbidade; b) incontinencia de conduta ou mau procedimento; c) negociacao habitual; "
        "d) condenacao criminal; e) desidia no desempenho das respectivas funcoes; f) embriaguez habitual; "
        "g) violacao de segredo da empresa; h) ato de indisciplina ou insubordinacao; i) abandono de emprego."
    )
    pdf.multi_cell(0, 3, limpar(clt_text))
    
    res = pdf.output(dest='S')
    if isinstance(res, str):
        return res.encode('latin1')
    return bytes(res)

# ---------------------------------------------------------
# PALETA DE CORES VIBRANTES POR OBRA
# ---------------------------------------------------------
PALETA = {
    "DER/SP - TATUI": "#FF7A6C",
    "CCR - SÃO ROQUE": "#FFA500",
    "DER/PR - PARANÁ": "#4CAF50",
    "CONSERVA": "#2196F3",
    "SAO ROQUE/SP": "#9C27B0",
    "SAO ROQUE": "#00BCD4"
}
RESERVA = ["#FF7A6C", "#FFA500", "#4CAF50", "#2196F3", "#9C27B0", "#00BCD4"]

def obter_cor(obra):
    o = str(obra).strip()
    return PALETA.get(o, RESERVA[abs(hash(o)) % len(RESERVA)])

# ---------------------------------------------------------
# BARRA LATERAL - FILTROS DE PESQUISA
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Pesquisa")
busca_texto = st.sidebar.text_input("Pesquisar Colaborador / Chapa", "")

secoes_disp = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
filtro_secao = st.sidebar.multiselect("Filtrar por Obra / Seção", options=secoes_disp, default=secoes_disp)

cargos_disp = sorted(df["CARGO"].dropna().astype(str).unique().tolist())
filtro_cargo = st.sidebar.multiselect("Filtrar por Cargo", options=cargos_disp, default=cargos_disp)

df_filtrado = df.copy()

if busca_texto:
    b_up = busca_texto.upper()
    df_filtrado = df_filtrado[
        df_filtrado["FUNCIONARIO"].astype(str).str.upper().str.contains(b_up, na=False) |
        df_filtrado["CHAPA"].astype(str).str.contains(b_up, na=False)
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
        st.caption(f"👥
