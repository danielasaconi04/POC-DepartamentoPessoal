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
# CARREGAMENTO DOS DADOS (WF0031.xlsx)
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
# TRATAMENTO DE TEXTO PARA ACOMPANHAR O PADRÃO FPDF
# ---------------------------------------------------------
def limpar(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# ---------------------------------------------------------
# GERADOR DE PDF IDÊNTICO AOS MODELOS OFICIAIS DA ELLENCO
# ---------------------------------------------------------
def gerar_pdf_identico_ellenco(nome, chapa, cargo, obra, total_faltas, data_1, data_2, data_3):
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    nc = limpar(nome)
    cc = limpar(cargo)
    oc = limpar(obra)
    
    # Cabeçalho Oficial
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 6, "Ellenco", 0, 1, "L")
    pdf.ln(4)
    
    # Título do Documento Exato Conforme os PDFs Oficiais
    pdf.set_font("Arial", "B", 12)
    if total_faltas == 1:
        pdf.cell(0, 6, "CARTA DE ADVERTÊNCIA DISCIPLINAR", 0, 1, "C")
    elif total_faltas == 2:
        pdf.cell(0, 6, "CARTA DE SUSPENSÃO DISCIPLINAR", 0, 1, "C")
    elif total_faltas == 3:
        pdf.cell(0, 6, "CARTA DE SUSPENSÃO DISCIPLINAR", 0, 1, "C")
    else:
        pdf.cell(0, 6, "ENCAMINHAMENTO AO DEPARTAMENTO JURÍDICO", 0, 1, "C")
    pdf.ln(4)
    
    # Identificação do Colaborador (Linha idêntica aos modelos)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 5, limpar(f"Ilmo(a) Sr(a): {nc}, ocupante do cargo de {cc} da obra {oc}"), 0, 1, "L")
    
    pdf.set_font("Arial", "B", 10)
    if total_faltas == 1:
        pdf.cell(0, 5, "Referente: 1ª FALTA INJUSTIFICADA ISOLADA", 0, 1, "L")
    elif total_faltas == 2:
        pdf.cell(0, 5, "Referente: Aplicação de Suspensão Disciplinar", 0, 1, "L")
    elif total_faltas == 3:
        pdf.cell(0, 5, "Referente: Aplicação de Suspensão Disciplinar Agravada", 0, 1, "L")
    else:
        pdf.cell(0, 5, "Referente: Reincidência Habitual e Justa Causa", 0, 1, "L")
    pdf.ln(5)
    
    # Corpo do Texto Exato dos Modelos Oficiais
    pdf.set_font("Arial", "", 10)
    
    if total_faltas == 1:
        d1 = str(data_1) if pd.notna(data_1) else "28/09/2026"
        texto = (
            f"A empresa Ellenco Construções registra, por meio deste documento, a aplicação de ADVERTÊNCIA DISCIPLINAR, "
            f"em razão de ausência injustificada ao trabalho[cite: 13].\n\n"
            f"Conforme registros de frequência, foi constatada a ausência do empregado no dia {d1} sem que houvesse "
            f"apresentação de justificativa legalmente válida ou documento apto a justificar a ausência[cite: 13].\n\n"
            f"A referida ausência ocasionou o não cumprimento da jornada de trabalho prevista para a respectiva data, em "
            f"desacordo com as obrigações decorrentes do contrato de trabalho e das normas internas da empresa[cite: 13].\n\n"
            f"Registra-se que, até o momento da aplicação desta penalidade, não foi apresentada justificativa legal capaz de "
            f"afastar a caracterização da falta[cite: 13].\n\n"
            f"Diante do ocorrido, a empresa aplica a presente ADVERTÊNCIA DISCIPLINAR, de caráter pedagógico, para que "
            f"o(a) empregado(a) observe rigorosamente sua jornada de trabalho e comunique previamente à empresa eventual "
            f"impossibilidade de comparecimento, apresentando, quando cabível, a respectiva justificativa[cite: 13].\n\n"
            f"Fica o empregado ciente de que a repetição de faltas injustificadas poderá ensejar a adoção de medidas "
            f"disciplinares mais severas, de acordo com a gravidade e a reiteração da conduta, inclusive suspensão disciplinar e, "
            f"em situações que assim o justifiquem, a rescisão do contrato por justa causa, nos termos do art. 482 da CLT[cite: 13]."
        )
    elif total_faltas == 2:
        d_atual = str(data_2) if pd.notna(data_2) else "25/09/2026"
        d_ant = str(data_1) if pd.notna(data_1) else "18/09/2026"
        texto = (
            f"A empresa Ellenco Construções aplica, por meio deste documento, a penalidade de SUSPENSÃO DISCIPLINAR "
            f"pelo período de 1 dia útil, em razão da reincidência reiterada em faltas injustificadas ao trabalho[cite: 12].\n\n"
            f"Foi constatada a ausência do empregado nos dias {d_atual}, sem apresentação de justificativa legal válida[cite: 12].\n\n"
            f"Registra-se que o empregado já havia sido penalizado anteriormente com ADVERTÊNCIA DISCIPLINAR, aplicada "
            f"em {d_ant}, em razão de falta injustificada ocorrida[cite: 12].\n\n"
            f"Apesar da orientação e da penalidade anteriormente aplicada, houve nova ocorrência de ausência injustificada, "
            f"demonstrando a repetição da conduta[cite: 12].\n\n"
            f"Diante da reincidência, fica aplicada a presente SUSPENSÃO DISCIPLINAR, pelo período de 1 dia útil, "
            f"sem prejuízo dos efeitos legais decorrentes da suspensão[cite: 12].\n\n"
            f"O empregado fica formalmente advertido de que a repetição de faltas injustificadas poderá resultar na aplicação de "
            f"penalidades disciplinares mais severas, inclusive suspensão por período superior e rescisão do contrato por justa causa[cite: 12]."
        )
    elif total_faltas == 3:
        d3 = str(data_3) if pd.notna(data_3) else "15/09/2026"
        d1 = str(data_1) if pd.notna(data_1) else "20/07/2026"
        d2 = str(data_2) if pd.notna(data_2) else "03/09/2026"
        texto = (
            f"A empresa Ellenco Construções aplica, por meio deste documento, a penalidade de SUSPENSÃO DISCIPLINAR AGRAVADA "
            f"pelo período de 3 dias úteis, em razão da reincidência reiterada em faltas injustificadas ao trabalho[cite: 11].\n\n"
            f"Conforme registros de frequência, foi constatada nova ausência injustificada do empregado no dia {d3}, "
            f"sem apresentação de justificativa legalmente válida[cite: 11].\n\n"
            f"A presente ocorrência não constitui fato isolado. O empregado já foi anteriormente penalizado por faltas "
            f"injustificadas, tendo recebido:\n"
            f"a) Advertência disciplinar, aplicada em {d1}, em razão da ausência anterior; e\n"
            f"b) Suspensão disciplinar de 1 dia, aplicada em {d2}, em razão da ausência anterior[cite: 11].\n\n"
            f"Mesmo após as medidas disciplinares anteriormente aplicadas e a ciência expressa acerca da necessidade de "
            f"observância da jornada de trabalho, ocorreu nova falta injustificada[cite: 11].\n\n"
            f"Diante da persistência da conduta, a empresa aplica a presente SUSPENSÃO DISCIPLINAR DE 3 DIAS ÚTEIS[cite: 11].\n\n"
            f"O empregado fica expressamente ciente de que a continuidade ou reiteração de faltas injustificadas poderá ensejar "
            f"a adoção de medida disciplinar máxima, inclusive a rescisão do contrato por justa causa[cite: 11]."
        )
    else:
        texto = (
            f"A empresa Ellenco Construções encaminha o presente histórico ao Departamento Jurídico para análise "
            f"de Rescisão por Justa Causa com base no Artigo 482, alínea 'e' da CLT (Desídia no desempenho das respectivas funções), "
            f"tendo em vista o esgotamento das sanções pedagógicas anteriores (Advertência, Suspensão de 1 dia e Suspensão Agravada)."
        )

    pdf.multi_cell(0, 5, limpar(texto))
    pdf.ln(5)
    
    # Local e Data exatos do modelo
    pdf.cell(0, 5, "Sorocaba, SP 02/10/2026", 0, 1, "R")
    pdf.ln(5)
    
    # Bloco de Assinaturas (Empregado e Testemunhas exatamente como nos PDFs)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 5, limpar(f"ELLENCO                                                                                              {nc}"), 0, 1, "L")
    pdf.ln(3)
    pdf.cell(90, 5, "Ciente do(a) Empregado(a):", 0, 0, "L")
    pdf.cell(0, 5, "", 0, 1, "R")
    pdf.ln(6)
    pdf.cell(90, 5, "_______________________________________", 0, 0, "L")
    pdf.cell(0, 5, "_______________________________________", 0, 1, "R")
    pdf.cell(90, 5, "Em:", 0, 0, "L")
    pdf.cell(0, 5, "", 0, 1, "R")
    pdf.ln(4)
    pdf.cell(90, 5, "Testemunha 1", 0, 0, "L")
    pdf.cell(90, 5, "Testemunha 2", 0, 1, "R")
    pdf.ln(6)
    
    # Transcrição Completa e Fiel do Artigo 482 da CLT no Rodapé
    pdf.set_font("Arial", "B", 7.5)
    pdf.cell(0, 3.5, "Para seu conhecimento, transcrevemos abaixo o Artigo 482 da CLT[cite: 11, 12, 13]:", 0, 1)
    pdf.set_font("Arial", "", 6)
    clt_text = (
        "Art. 482 Constituem justa causa para rescisão do contrato de trabalho pelo empregador:\n"
        "a) ato de improbidade; (desonestidade, fraude, mau caráter)\n"
        "b) incontinência de conduta ou mau procedimento; (conduta incabível)\n"
        "c) negociação habitual por conta própria ou alheia sem permissão do empregador, quando constituir ato de concorrência à empresa para a qual trabalha o empregado, ou for prejudicial ao serviço;\n"
        "d) condenação criminal do empregado, passada em julgado, caso não tenha havido suspensão da execução da pena;\n"
        "e) desídia no desempenho das respectivas funções;\n"
        "f) embriaguez habitual ou em serviço;\n"
        "g) violação de segredo da empresa;\n"
        "h) ato de indisciplina ou de insubordinação;\n"
        "i) abandono de emprego;\n"
        "j) ato lesivo da honra ou da boa fama praticado no serviço contra qualquer pessoa, ou ofensas físicas, nas mesmas condições, salvo em caso de legítima defesa, própria ou de outrem;\n"
        "k) ato lesivo da honra ou da boa fama ou ofensas físicas praticadas contra o empregador e superiores hierárquicos, salvo em caso de legítima defesa, própria ou de outrem;\n"
        "l) prática constante de jogos de azar."
    )
    pdf.multi_cell(0, 2.5, limpar(clt_text))
    
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
# QUADRO KANBAN
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
            
            pdf_bytes = gerar_pdf_identico_ellenco(
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
