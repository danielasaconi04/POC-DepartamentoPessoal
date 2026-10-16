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
# CARREGAMENTO E GERENCIAMENTO DE ESTADO (SESSION STATE)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados_iniciais():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception as e:
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "TOTAL_FALTAS": 2},
            {"CHAPA": 3, "FUNCIONARIO": "DANILO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 3}
        ])

if "df_dados" not in st.session_state:
    df_temp = carregar_dados_iniciais()
    if "DATA_MEDIDA" not in df_temp.columns:
        df_temp["DATA_MEDIDA"] = datetime.now().strftime("%d/%m/%Y")
    st.session_state.df_dados = df_temp

df = st.session_state.df_dados

# Classificação automática do Kanban
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
def gerar_pdf_medida(nome, chapa, cargo, obra, etapa, data_envio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "ELLENCO CONSTRUÇÕES", 0, 1, "C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"CARTA DE MEDIDA DISCIPLINAR: {etapa.upper()}", 0, 1, "C")
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome} (Chapa: {chapa})", 0, 1)
    pdf.cell(0, 6, f"Cargo: {cargo} | Obra/Seção: {obra}", 0, 1)
    pdf.cell(0, 6, f"Data de Emissão: {data_envio}", 0, 1)
    pdf.ln(8)
    
    texto = (
        f"A empresa Ellenco Construções aplica, por meio deste documento, a penalidade correspondente a {etapa}, "
        f"em razão de ausência(s) injustificada(s) ao trabalho. "
        f"O colaborador fica advertido de que a reincidência em faltas injustificadas poderá ensejar a adoção "
        f"de medidas mais severas, inclusive a rescisão por justa causa nos termos do Art. 482 da CLT."
    )
    pdf.multi_cell(0, 6, texto)
    pdf.ln(10)
    
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Transcrição legal: Artigo 482 da CLT - Constituem justa causa para rescisão do contrato de trabalho pelo empregador: e) desídia no desempenho das respectivas funções; h) ato de indisciplina ou insubordinação.")
    
    return pdf.output(dest="S").encode("latin1")

# ---------------------------------------------------------
# CORES POR OBRA
# ---------------------------------------------------------
PALETA = {
    "DER/SP - TATUI": "#FF7A6C",
    "CCR - SÃO ROQUE": "#FFA500",
    "DER/PR - PARANÁ": "#4CAF50",
    "CONSERVA": "#2196F3",
    "SAO ROQUE/SP": "#9C27B0"
}
RESERVA = ["#FF7A6C", "#FFA500", "#4CAF50", "#2196F3", "#9C27B0", "#00BCD4"]

def obter_cor(obra):
    o = str(obra).strip()
    return PALETA.get(o, RESERVA[abs(hash(o)) % len(RESERVA)])

# ---------------------------------------------------------
# FILTROS LATERAIS
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
# KANBAN OPERACIONAL
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
        
        for idx_row, row in df_etapa.iterrows():
            obra_nome = str(row.get("SECAO", "-")).strip()
            cor_fundo = obter_cor(obra_nome)
            chapa_val = row["CHAPA"]
            data_medida = row.get("DATA_MEDIDA", datetime.now().strftime("%d/%m/%Y"))
            
            # 1. Encarte Visual Colorido
            card_html = f"""
            <div class="card-kanban-solido" style="background-color: {cor_fundo};">
                <div class="card-nome-solido">👤 {row['FUNCIONARIO']}</div>
                <div class="card-detalhe-solido">🔢 <b>Chapa:</b> {chapa_val} | <b>Total Faltas:</b> {row['TOTAL_FALTAS']}</div>
                <div class="card-detalhe-solido">💼 <b>Cargo:</b> {row.get('CARGO', '-')}</div>
                <div class="card-detalhe-solido">📅 <b>Data da Medida:</b> {data_medida}</div>
                <div class="card-tag-obra-solida">🏗️ {obra_nome}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # 2. Botão de Download do PDF Gerado
            pdf_data = gerar_pdf_medida(
                nome=row['FUNCIONARIO'],
                chapa=chapa_val,
                cargo=row.get('CARGO', '-'),
                obra=obra_nome,
                etapa=etapa,
                data_envio=str(data_medida)
            )
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                st.download_button(
                    label="📄 Baixar PDF",
                    data=pdf_data,
                    file_name=f"Medida_Chapa_{chapa_val}.pdf",
                    mime="application/pdf",
                    key=f"dl_{chapa_val}_{i}"
                )
            with c_btn2:
                # Botão para simular nova falta e mover o card para a próxima coluna automaticamente
                if st.button("➕ Reg. Falta", key=f"add_{chapa_val}_{i}"):
                    st.session_state.df_dados.loc[st.session_state.df_dados["CHAPA"] == chapa_val, "TOTAL_FALTAS"] += 1
                    st.session_state.df_dados.loc[st.session_state.df_dados["CHAPA"] == chapa_val, "DATA_MEDIDA"] = datetime.now().strftime("%d/%m/%Y")
                    st.rerun()
            
            st.markdown("<hr style='margin:6px 0 12px 0;'>", unsafe_allow_html=True)

# ---------------------------------------------------------
# LEGENDA
# ---------------------------------------------------------
st.divider()
st.markdown("##### 🎨 Legenda de Cores por Obra")
obras_presentes = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
cols_leg = st.columns(min(len(obras_presentes), 6) if len(obras_presentes) > 0 else 1)

for idx, obra in enumerate(obras_presentes):
    cor = obter_cor(obra)
    with cols_leg[idx % len(cols_leg)]:
        st.markdown(f'<div style="background-color:{cor}; padding:4px; border-radius:4px; text-align:center; color:white; font-weight:bold;"><small>{obra}</small></div>', unsafe_allow_html=True)
