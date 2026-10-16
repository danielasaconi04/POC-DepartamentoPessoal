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
# TRATAMENTO DE CARACTERES E GERADOR DE PDF
# ---------------------------------------------------------
def limpar(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

def gerar_pdf_ellenco(nome, chapa, cargo, obra, total_faltas, data_1, data_2, data_3):
    pdf = FPDF()
    pdf.add_page()
    
    nc = limpar(nome)
    cc = limpar(cargo)
    oc = limpar(obra)
    
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "ELLENCO CONSTRUCOES", 0, 1, "L")
    pdf.ln(2)
    
    pdf.set_font("Arial", "B", 11)
    if total_faltas == 1:
        pdf.cell(0, 6, "CARTA DE ADVERTENCIA DISCIPLINAR", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nc}, ocupante do cargo de {cc} da obra {oc}", 0, 1)
        pdf.cell(0, 6, "Referente: 1a FALTA INJUSTIFICADA ISOLADA", 0, 1)
        pdf.ln(4)
        d1 = str(data_1) if pd.notna(data_1) else "28/09/2026"
        t = (
            f"A empresa Ellenco Construcoes registra, por meio deste documento, a aplicacao de ADVERTENCIA DISCIPLINAR, "
            f"em razao de ausencia injustificada ao trabalho.\n\n"
            f"Conforme registros de frequencia, foi constatada a ausencia do empregado no dia {d1} sem que houvesse "
            f"apresentacao de justificativa legalmente valida ou documento apto a justificar a ausencia.\n\n"
            f"Diante do ocorrido, a empresa aplica a presente ADVERTENCIA DISCIPLINAR, de carater pedagogico, para que "
            f"o(a) empregado(a) observe rigorosamente sua jornada de trabalho."
        )
        pdf.multi_cell(0, 5, limpar(t))
        
    elif total_faltas == 2:
        pdf.cell(0, 7, "CARTA DE SUSPENSAO DISCIPLINAR", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nc}, ocupante do cargo de {cc} da obra {oc}", 0, 1)
        pdf.cell(0, 6, "Referente: Aplicacao de Suspensao Disciplinar (1 dia util)", 0, 1)
        pdf.ln(4)
        d2 = str(data_2) if pd.notna(data_2) else "25/09/2026"
        d1 = str(data_1) if pd.notna(data_1) else "18/09/2026"
        t = (
            f"A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR "
            f"pelo periodo de 1 dia util, em razao da reincidencia reiterada em faltas injustificadas ao trabalho[cite: 12].\n\n"
            f"Foi constatada a ausencia do empregado no dia {d2}, sem apresentacao de justificativa legal valida[cite: 12].\n\n"
            f"Registra-se que o empregado ja havia sido penalizado anteriormente com ADVERTENCIA DISCIPLINAR, aplicada em {d1}[cite: 12].\n\n"
            f"Diante da reincidencia, fica aplicada a presente SUSPENSAO DISCIPLINAR, pelo periodo de 1 dia util[cite: 12]."
        )
        pdf.multi_cell(0, 5, limpar(t))
        
    elif total_faltas == 3:
        pdf.cell(0, 7, "CARTA DE SUSPENSAO DISCIPLINAR AGRAVADA", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nc}, ocupante do cargo de {cc} da obra {oc}", 0, 1)
        pdf.cell(0, 6, "Referente: Aplicacao de Suspensao Disciplinar Agravada (3 dias uteis)", 0, 1)
        pdf.ln(4)
        d3 = str(data_3) if pd.notna(data_3) else "15/09/2026"
        d1 = str(data_1) if pd.notna(data_1) else "20/07/2026"
        d2 = str(data_2) if pd.notna(data_2) else "03/09/2026"
        t = (
            f"A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR AGRAVADA "
            f"pelo periodo de 3 dias uteis, em razao da reincidencia reiterada em faltas injustificadas ao trabalho[cite: 11].\n\n"
            f"Conforme registros de frequencia, foi constatada nova ausencia injustificada do empregado em {d3}[cite: 11].\n\n"
            f"O empregado ja foi anteriormente penalizado, tendo recebido:\n"
            f"a) Advertencia disciplinar, aplicada em {d1};\n"
            f"b) Suspensao disciplinar de 1 dia, aplicada em {d2}[cite: 11].\n\n"
            f"Diante da persistencia, aplica-se a SUSPENSAO DISCIPLINAR DE 3 DIAS UTEIS[cite: 11]."
        )
        pdf.multi_cell(0, 5, limpar(t))
        
    else:
        pdf.cell(0, 7, "ENCAMINHAMENTO AO JURIDICO - JUSTA CAUSA", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nc}, ocupante do cargo de {cc} da obra {oc}", 0, 1)
        pdf.ln(4)
        t = "Encaminhamento formal ao Departamento Juridico para analise de Rescisao por Justa Causa (Art. 482, alinea 'e' da CLT)."
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
        "a) ato de improbidade; b) incontinencia de conduta; c) negociacao habitual; "
        "d) condenacao criminal; e) desidia no desempenho das respectivas funcoes; f) embriaguez habitual; "
        "g) violacao de segredo; h) ato de indisciplina ou insubordinacao; i) abandono de emprego."
    )
    pdf.multi_cell(0, 3, limpar(clt_text))
    
    res = pdf.output(dest='S')
    return res.encode('latin1') if isinstance(res, str) else bytes(res)

# ---------------------------------------------------------
# PALETA DE CORES POR OBRA
# ---------------------------------------------------------
PALETA = {
    "DER/SP - TATUI": "#FF7A6C",
    "CCR - SÃO ROQUE": "#FFA500",
    "DER/PR - PARANÁ": "#4CAF50",
    "CONSERVA": "#2196F3",
    "SAO ROQUE/SP": "#9C27B0",
    "SAO ROQUE": "#00BCD4"
}
def obter_cor(obra):
    return PALETA.get(str(obra).strip(), "#333333")

# ---------------------------------------------------------
# FILTROS LATERAIS
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Pesquisa")
busca_texto = st.sidebar.text_input("Pesquisar Colaborador / Chapa", "")

secoes_disp = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
filtro_secao = st.sidebar.multiselect("Filtrar por Obra / Seção", options=secoes_disp, default=secoes_disp)

cargos_disp = sorted(df["CARGO"].dropna().astype(str).unique().tolist())
filtro_cargo = st.sidebar.multiselect("Filtrar por Cargo", options=cargos_disp, default=cargos_disp)

df_f = df.copy()
if busca_texto:
    df_f = df_f[df_f["FUNCIONARIO"].astype(str).str.upper().str.contains(busca_texto.upper(), na=False)]
if filtro_secao:
    df_f = df_f[df_f["SECAO"].astype(str).isin(filtro_secao)]
if filtro_cargo:
    df_f = df_f[df_f["CARGO"].astype(str).isin(filtro_cargo)]

# ---------------------------------------------------------
# KANBAN OPERACIONAL
# ---------------------------------------------------------
st.markdown("### 📊 Quadro Kanban Operacional")

cols = st.columns(4)
etapas_kanban = [
    "1ª Falta (Advertência)",
    "2ª Falta (Suspensão 1 a 2 dias)",
    "3ª Falta (Suspensão Agravada 3 a 5 dias)",
    "4ª Falta (Análise Jurídico / Justa Causa)"
]

for i, etapa in enumerate(etapas_kanban):
    with cols[i]:
        dfe = df_f[df_f["ETAPA"] == etapa]
        st.subheader(etapa)
        st.caption(f"Total: {len(dfe)} colaborador(es)")
        st.markdown("---")
        
        if dfe.empty:
            st.info("Nenhum colaborador.")
        
        for idx_row, row in dfe.iterrows():
            obra_nome = str(row.get("SECAO", "-")).strip()
            cor_fundo = obter_cor(obra_nome)
            chapa_val = row["CHAPA"]
            total_f = int(row["TOTAL_FALTAS"])
            d_falta = str(row.get("DATA_1", "28/09/2026"))
            
            card_html = f"""
            <div class="card-kanban-solido" style="background-color: {cor_fundo};">
                <div class="card-nome-solido">👤 {row['FUNCIONARIO']}</div>
                <div class="card-detalhe-solido">🔢 <b>Chapa:</b> {chapa_val} | <b>Faltas:</b> {total_f}</div>
                <div class="card-detalhe-solido">💼 <b>Cargo:</b> {row.get('CARGO', '-')}</div>
                <div class="card-detalhe-solido">📅 <b>Data:</b> {d_falta}</div>
                <div class="card-tag-obra-solida">🏗️ {obra_nome}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Geração segura isolada de variáveis do botão
            pdf_bytes = gerar_pdf_ellenco(
                nome=str(row['FUNCIONARIO']),
                chapa=str(chapa_val),
                cargo=str(row.get('CARGO', '-')),
                obra=obra_nome,
                total_faltas=total_f,
                data_1=row.get('DATA_1'),
                data_2=row.get('DATA_2'),
                data_3=row.get('DATA_3')
            )
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                st.download_button(
                    label="📄 Baixar PDF",
                    data=pdf_bytes,
                    file_name=f"Medida_Chapa_{chapa_val}.pdf",
                    mime="application/pdf",
                    key=f"dl_{chapa_val}_{idx_row}"
                )
            with c_btn2:
                if st.button("➕ Reg. Falta", key=f"add_{chapa_val}_{idx_row}"):
                    st.session_state.df_dados.loc[st.session_state.df_dados["CHAPA"] == chapa_val, "TOTAL_FALTAS"] += 1
                    st.rerun()
            
            st.markdown("<hr style='margin:4px 0 10px 0;'>", unsafe_allow_html=True)
