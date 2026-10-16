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
        margin-bottom: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
        color: #ffffff !important;
        font-family: sans-serif;
    }
    .card-nome-solido {
        font-weight: 800;
        font-size: 14px;
        margin-bottom: 4px;
        color: #ffffff !important;
        text-shadow: 0px 1px 2px rgba(0,0,0,0.3);
    }
    .card-detalhe-solido {
        font-size: 11px;
        margin-bottom: 2px;
        color: #ffffff !important;
        opacity: 0.95;
    }
    .card-tag-obra-solida {
        display: inline-block;
        background-color: rgba(0, 0, 0, 0.25);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
        margin-top: 4px;
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
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportار Planilha" if "Exportar Planilha" in pd.ExcelFile("WF0031.xlsx").sheet_names else 0)
        return df
    except Exception as e:
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "TOTAL_FALTAS": 2}
        ])

df = carregar_dados()

# Simulação de data de envio da medida para demonstração (Caso não exista na planilha)
if "DATA_ENVIO" not in df.columns:
    df["DATA_ENVIO"] = "02/10/2026"

# Mapeia as etapas do processo disciplinar conforme reincidência
def classificar_etapa(row):
    total_faltas = row["TOTAL_FALTAS"]
    if total_faltas == 1:
        return "1ª Falta (Advertência)"
    elif total_faltas == 2:
        return "2ª Falta (Suspensão 1 a 2 dias)"
    elif total_faltas == 3:
        return "3ª Falta (Suspensão Agravada 3 a 5 dias)"
    else:
        return "4ª Falta (Análise Jurídico / Justa Causa)"

df["ETAPA"] = df.apply(classificar_etapa, axis=1)

# ---------------------------------------------------------
# FUNÇÃO PARA GERAR O PDF OFICIAL DA ELLENCO
# ---------------------------------------------------------
def gerar_pdf_documento(nome, chapa, cargo, obra, etapa, data_envio):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    
    # Cabeçalho
    pdf.cell(0, 10, "ELLENCO CONSTRUÇÕES - DEPARTAMENTO PESSOAL", 0, 1, "C")
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"DOCUMENTO DISCIPLINAR: {etapa.upper()}", 0, 1, "C")
    pdf.ln(5)
    
    # Dados do Colaborador
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Colaborador(a): {nome} (Chapa: {chapa})", 0, 1)
    pdf.cell(0, 6, f"Cargo: {cargo} | Obra/Seção: {obra}", 0, 1)
    pdf.cell(0, 6, f"Data de Emissão / Envio: {data_envio}", 0, 1)
    pdf.ln(10)
    
    # Corpo do Texto
    pdf.set_font("Arial", "", 10)
    texto_corpo = (
        f"A empresa Ellenco Construções registra por meio deste documento a medida disciplinar "
        f"correspondente a '{etapa}', aplicada em decorrência de ausências injustificadas ao trabalho. "
        f"O(a) colaborador(a) fica ciente de que o cumprimento rigoroso da jornada de trabalho é dever contratual "
        f"e que a reiteração da conduta poderá resultar em sanções mais severas, inclusive rescisão por justa causa "
        f"nos termos do Artigo 482 da CLT."
    )
    pdf.multi_cell(0, 6, texto_corpo)
    pdf.ln(10)
    
    # Rodapé Legal Art. 482 CLT
    pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Referência legal: Art. 482 da CLT (Desídia no desempenho das respectivas funções, indisciplina, insubordinação, etc.).")
    
    return pdf.output(dest="S").encode("latin1")

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
CORES_RESERVA = ["#FF7A6C", "#FFA500", "#4CAF50", "#2196F3", "#9C27B0", "#00BCD4", "#E91E63", "#3F51B5"]

def obter_cor(obra):
    obra_str = str(obra).strip()
    if obra_str in PALETA_CORES_VIBRANTES:
        return PALETA_CORES_VIBRANTES[obra_str]
    return CORES_RESERVA[abs(hash(obra_str)) % len(CORES_RESERVA)]

# ---------------------------------------------------------
# BARRA LATERAL - FILTROS
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
st.markdown("### 📊 Quadro Kanban Operacional (Janela de 12 Meses)")

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
        st.caption(f"👥 Total: **{len(df_etapa)}**")
        st.markdown("---")
        
        if df_etapa.empty:
            st.info("Nenhum registro.")
        
        for _, row in df_etapa.iterrows():
            obra_nome = str(row.get("SECAO", "-")).strip()
            cor_fundo = obter_cor(obra_nome)
            data_envio = row.get("DATA_ENVIO", "2026-10-02")
            
            # HTML do cartão exibindo nome, chapa, faltas e a data do envio da medida
            card_html = f"""
            <div class="card-kanban-solido" style="background-color: {cor_fundo};">
                <div class="card-nome-solido">👤 {row['FUNCIONARIO']}</div>
                <div class="card-detalhe-solido">🔢 <b>Chapa:</b> {row['CHAPA']} | <b>Faltas:</b> {row['TOTAL_FALTAS']}</div>
                <div class="card-detalhe-solido">💼 <b>Cargo:</b> {row.get('CARGO', '-')}</div>
                <div class="card-detalhe-solido">📅 <b>Envio da Medida:</b> {data_envio}</div>
                <div class="card-tag-obra-solida">🏗️ {obra_nome}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Botão de Download do PDF gerado automaticamente dentro do encarte
            pdf_bytes = gerar_pdf_documento(
                nome=row['FUNCIONARIO'],
                chapa=row['CHAPA'],
                cargo=row.get('CARGO', '-'),
                obra=obra_nome,
                etapa=etapa,
                data_envio=str(data_envio)
            )
            st.download_button(
                label=f"📥 Baixar PDF ({row['CHAPA']})",
                data=pdf_bytes,
                file_name=f"Medida_Disciplinar_Chapa_{row['CHAPA']}.pdf",
                mime="application/pdf",
                key=f"pdf_{row['CHAPA']}_{i}"
            )
            st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)
