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
# LEITURA DA PLANILHA CORPORATIVA (WF0031.xlsx)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception as e:
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 1}
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
    pdf.set_text_color(20, 40, 110)
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
        texto = p1 + "\n\n" + p2 + "\n\n" + p3 + "\n\n" + p4 + "\n\n" + p5 + "\n\n" + p6
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
        texto = p1 + "\n\n" + p2 + "\n\n" + p3 + "\n\n" + p4 + "\n\n" + p5 + "\n\n" + p6
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
        texto = p1 + "\n\n" + p2 + "\n\n" + p3 + "\n\n" + p4 + "\n\n" + p5 + "\n\n" + p6
    else:
        pdf.cell(0, 5, "Referente: Encaminhamento Juridico - Justa Causa", 0, 1, "L")
        pdf.ln(2)
        texto = "Encaminhamento formal ao Departamento Juridico para analise de Rescisao por Justa Causa com base no Art. 482, alinea 'e' da CLT."

    pdf.set_font("Arial", "", 8.5)
    pdf.set_x(12)
    pdf.multi_cell(186, 4.2, limpar(texto))
    
    pdf.set_xy(12, 131)
    pdf.set_font("Arial", "", 9)
    pdf.cell(186, 5, "Sorocaba, SP 02/10/2026", 0, 1, "R")
    pdf.cell(186, 5, "ELLENCO", 0, 1, "C")
    
    # Caixa de Assinaturas
    pdf.rect(10, 140, 190, 32)
    pdf.set_xy(12, 142)
    pdf.set_font("Arial", "B", 8.5)
    pdf.cell(95, 5, "Ciente do(a) Empregado(a):", 0, 0, "L")
    pdf.cell(95, 5, "Em: ____ / ____ / ________.", 0, 1, "L")
    pdf.ln(6)
    
    pdf.set_font("Arial", "", 8)
    pdf.cell(95, 4, "_______________________________________", 0, 0, "L")
    pdf.cell(95, 4, "_______________________________________", 0, 1, "R")
    pdf.cell(95, 4, "Testemunha 1", 0, 0, "L")
    pdf.cell(95, 4, nc, 0, 1, "R")
    pdf.cell(95, 4, "_______________________________________", 0, 1, "L")
    pdf.cell(95, 4, "Testemunha 2", 0, 1, "L")
    
    # Caixa do Artigo 482 da CLT
    pdf.rect(10, 174, 190, 48)
    pdf.set_xy(12, 175)
    pdf.set_font("Arial", "B", 7.5)
    pdf.cell(186, 4, "Para seu conhecimento, transcrevemos abaixo o Artigo 482 da CLT:", 0, 1, "L")
    
    pdf.set_font("Arial", "", 5.8)
    pdf.set_x(12)
    clt_text = (
        "Art. 482 Constituem justa causa para rescisao do contrato de trabalho pelo empregador:\n"
        "a) ato de improbidade; (desonestidade, fraude, mau carater)\n"
        "b) incontinencia de conduta ou mau procedimento; (conduta incabivel)\n"
        "c) negociacao habitual por conta propria ou alheia sem permissao do empregador, quando constituir ato de concorrencia a empresa para a qual trabalha o empregado, ou for prejudicial ao servico;\n"
        "d) condenacao criminal do empregado, passada em julgado, caso nao tenha havido suspensao da execucao da pena;\n"
        "e) desidia no desempenho das respectivas funcoes;\n"
        "f) embriaguez habitual ou em servico;\n"
        "g) violacao de segredo da empresa;\n"
        "h) ato de indisciplina ou de insubordinacao;\n"
        "i) abandono de emprego;\n"
        "j) ato lesivo da honra ou da boa fama praticado no servico contra qualquer pessoa, ou ofensas fisicas, nas mesmas condicoes, salvo em caso de legitima defesa, propria ou de outrem;\n"
        "k) ato lesivo da honra ou da boa fama ou ofensas fisicas praticadas contra o empregador e superiores hierarquicos, salvo em caso de legitima defesa, propria ou de outrem;\n"
        "l) pratica constante de jogos de azar.\n"
        "Paragrafo unico - Constitui igualmente justa causa para dispensa de emprego a pratica, devidamente comprovada em inquerito administrativo, de atos atentatorios contra a seguranca nacional."
    )
    pdf.multi_cell(186, 2.5, limpar(clt_text))
    
    # Rodapé Institucional com Endereços Oficiais
    pdf.set_xy(10, 224)
    pdf.set_font("Arial", "", 6)
    pdf.cell(95, 3, "Av. Antonio Bardella, 3 444 - Iporanga - Distrito Industrial", 0, 0, "L")
    pdf.cell(95, 3, "Av. Roberto Simonsen, 47 - Santa Rosalia", 0, 1, "R")
    pdf.set_x(10)
    pdf.cell(95, 3, "CEP 18085-852 - Sorocaba - SP", 0, 0, "L")
    pdf.cell(95, 3, "CEP 18090-000 - Sorocaba - SP", 0, 1, "R")
    pdf.set_x(10)
    pdf.cell(95, 3, "Fone/Fax: (15) 3238 4300", 0, 0, "L")
    pdf.cell(95, 3, "Fone: (15) 3331 6880 / Fax: (15) 3331 6900                   www.ellenco.com.br", 0, 1, "R")

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

CORES_RESERVA = ["#FF7A6C", "#FFA500", "#4CAF50", "#2196F3", "#9C27B0", "#00BCD4", "#E91E63", "#3F51B5"]

def obter_cor(obra):
    o = str(obra).strip()
    if o in PALETA:
        return PALETA[o]
    return CORES_RESERVA[abs(hash(o)) % len(CORES_RESERVA)]

# ---------------------------------------------------------
# BARRA LATERAL - FILTROS DE PESQUISA
# ---------------------------------------------------------
st.sidebar.header("🔍 Filtros de Pesquisa")
busca_texto = st.sidebar.text_input("Pesquisar Colaborador / Chapa", "")

secoes_disp = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
filtro_secao = st.sidebar.multiselect("Filtrar por Obra / Seção", options=secoes_disp, default=secoes_disp)

cargos_disp = sorted(df["CARGO"].dropna().astype(str).unique().tolist())
filtro_cargo = st.sidebar.multiselect("Filtrar por Cargo", options=cargos_disp, default=cargos_disp)

df_f = df.copy()

if busca_texto:
    b_up = busca_texto.upper()
    df_f = df_f[
        df_f["FUNCIONARIO"].astype(str).str.upper().str.contains(b_up, na=False) |
        df_f["CHAPA"].astype(str).str.contains(b_up, na=False)
    ]

if filtro_secao:
    df_f = df_f[df_f["SECAO"].astype(str).isin(filtro_secao)]

if filtro_cargo:
    df_f = df_f[df_f["CARGO"].astype(str).isin(filtro_cargo)]

# ---------------------------------------------------------
# QUADRO KANBAN OPERACIONAL
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
            st.info("Nenhum colaborador nesta etapa.")
        
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
            
            pdf_bytes = gerar_pdf_perfeito_ellenco(
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

# ---------------------------------------------------------
# LEGENDA DE CORES NO RODAPÉ
# ---------------------------------------------------------
st.divider()
st.markdown("##### 🎨 Legenda de Cores por Obra")
obras_presentes = sorted(df["SECAO"].dropna().astype(str).unique().tolist())
cols_leg = st.columns(min(len(obras_presentes), 6) if len(obras_presentes) > 0 else 1)

for idx, obra in enumerate(obras_presentes):
    cor = obter_cor(obra)
    with cols_leg[idx % len(cols_leg)]:
        st.markdown(f'<div style="background-color:{cor}; padding:4px; border-radius:4px; text-align:center; color:white; font-weight:bold;"><small>{obra}</small></div>', unsafe_allow_html=True)
