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
# CARREGAMENTO E ESTADO DA APLICAÇÃO
# ---------------------------------------------------------
@st.cache_data
def carregar_dados_iniciais():
    try:
        df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
        return df
    except Exception as e:
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "LUCAS", "CARGO": "Ajudante geral", "SECAO": "SAO ROQUE", "DATA_1": "28/09/2026", "FALTA_1": 1, "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "CARLOS", "CARGO": "Ajudante geral", "SECAO": "SAO ROQUE/SP", "DATA_1": "25/09/2026", "FALTA_1": 1, "DATA_2": "28/09/2026", "FALTA_2": 1, "TOTAL_FALTAS": 2},
            {"CHAPA": 3, "FUNCIONARIO": "JOÃO", "CARGO": "Ajudante geral", "SECAO": "CONSERVA", "DATA_1": "15/09/2026", "FALTA_1": 1, "TOTAL_FALTAS": 3}
        ])

if "df_dados" not in st.session_state:
    df_temp = carregar_dados_iniciais()
    if "DATA_MEDIDA" not in df_temp.columns:
        df_temp["DATA_MEDIDA"] = datetime.now().strftime("%d/%m/%Y")
    st.session_state.df_dados = df_temp

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
# GERADOR DE PDF EXATAMENTE IGUAL AOS MODELOS OFICIAIS
# ---------------------------------------------------------
def gerar_pdf_modelo_ellenco(nome, chapa, cargo, obra, total_faltas, data_medida):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho Empresa
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 7, "ELLENCO CONSTRUCOES", 0, 1, "L")
    pdf.ln(2)
    
    # Identificação do Documento conforme os modelos anexados
    pdf.set_font("Arial", "B", 11)
    if total_faltas == 1:
        pdf.cell(0, 6, "CARTA DE ADVERTENCIA DISCIPLINAR", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome}, ocupante do cargo de {cargo} da obra {obra}", 0, 1)
        pdf.cell(0, 6, "Referente: 1a FALTA INJUSTIFICADA ISOLADA", 0, 1)
        pdf.ln(4)
        
        texto = (
            f"A empresa Ellenco Construcoes registra, por meio deste documento, a aplicacao de ADVERTENCIA DISCIPLINAR, "
            f"em razao de ausencia injustificada ao trabalho.\n\n"
            f"Conforme registros de frequencia, foi constatada a ausencia do empregado no dia {data_medida} sem que houvesse "
            f"apresentacao de justificativa legalmente valida ou documento apto a justificar a ausencia.\n\n"
            f"A referida ausencia ocasionou o nao cumprimento da jornada de trabalho prevista para a respectiva data, em "
            f"desacordo com as obrigacoes decorrentes do contrato de trabalho e das normas internas da empresa.\n\n"
            f"Registra-se que, ate o momento da aplicacao desta penalidade, nao foi apresentada justificativa legal capaz de "
            f"afastar a caracterizacao da falta.\n\n"
            f"Diante do ocorrido, a empresa aplica a presente ADVERTENCIA DISCIPLINAR, de carater pedagogico, para que "
            f"o(a) empregado(a) observe rigorosamente sua jornada de trabalho e comunique previamente a empresa eventual "
            f"impossibilidade de comparecimento, apresentando, quando cabivel, a respectiva justificativa.\n\n"
            f"Fica o empregado ciente de que a repeticao de faltas injustificadas podera ensejar a adocao de medidas "
            f"disciplinares mais severas, de acordo com a gravidade e a reiteracao da conduta, inclusive suspensao disciplinar e, "
            f"em situacoes que assim o justifiquem, a rescisao do contrato por justa causa, nos termos do art. 482 da CLT."
        )
        pdf.multi_cell(0, 5, texto)
        
    elif total_faltas == 2:
        pdf.cell(0, 7, "CARTA DE SUSPENSAO DISCIPLINAR", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome}, ocupante do cargo de {cargo} da obra {obra}", 0, 1)
        pdf.cell(0, 6, "Referente: Aplicacao de Suspensao Disciplinar (1 dia util)", 0, 1)
        pdf.ln(4)
        
        texto = (
            f"A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR "
            f"pelo periodo de 1 dia util, em razao da reincidencia reiterada em faltas injustificadas ao trabalho.\n\n"
            f"Foi constatada a ausencia do empregado recentemente ({data_medida}), sem apresentacao de justificativa legal valida.\n\n"
            f"Registra-se que o empregado ja havia sido penalizado anteriormente com ADVERTENCIA DISCIPLINAR, aplicada "
            f"em razao de falta injustificada anterior.\n\n"
            f"Apesar da orientacao e da penalidade anteriormente aplicada, houve nova ocorrencia de ausencia injustificada, "
            f"demonstrando a repeticao da conduta.\n\n"
            f"Diante da reincidencia, fica aplicada a presente SUSPENSAO DISCIPLINAR, pelo periodo de 1 dia util, "
            f"sem prejuizo dos efeitos legais decorrentes da suspensao.\n\n"
            f"O empregado fica formalmente advertido de que a repeticao de faltas injustificadas podera resultar na aplicacao de "
            f"penalidades disciplinares mais severas, inclusive suspensao por periodo superior e rescisao do contrato de trabalho por justa causa."
        )
        pdf.multi_cell(0, 5, texto)
        
    elif total_faltas == 3:
        pdf.cell(0, 7, "CARTA DE SUSPENSAO DISCIPLINAR AGRAVADA", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome}, ocupante do cargo de {cargo} da obra {obra}", 0, 1)
        pdf.cell(0, 6, "Referente: Aplicacao de Suspensao Disciplinar Agravada (3 dias uteis)", 0, 1)
        pdf.ln(4)
        
        texto = (
            f"A empresa Ellenco Construcoes aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR AGRAVADA "
            f"pelo periodo de 3 dias uteis, em razao da reincidencia reiterada em faltas injustificadas ao trabalho.\n\n"
            f"Conforme registros de frequencia, foi constatada nova ausencia injustificada do empregado em {data_medida}, "
            f"sem apresentacao de justificativa legalmente valida[cite: 22].\n\n"
            f"A presente ocorrencia nao constitui fato isolado. O empregado ja foi anteriormente penalizado por faltas "
            f"injustificadas, tendo recebido Advertencia Disciplinar e Suspensao Disciplinar previa[cite: 22].\n\n"
            f"Mesmo apos as medidas disciplinares anteriormente aplicadas e a ciencia expressa acerca da necessidade de "
            f"observancia da jornada de trabalho, ocorreu nova falta injustificada[cite: 22].\n\n"
            f"Diante da persistencia da conduta, a empresa aplica a presente SUSPENSAO DISCIPLINAR DE 3 DIAS UTEIS[cite: 22].\n\n"
            f"O empregado fica expressamente ciente de que a continuidade ou reiteração de faltas injustificadas poderá ensejar "
            f"a adoção de medida disciplinar máxima, inclusive a rescisão do contrato de trabalho por justa causa[cite: 22]."
        )
        pdf.multi_cell(0, 5, texto)
        
    else:
        pdf.cell(0, 7, "ENCAMINHAMENTO AO JURIDICO - JUSTA CAUSA", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Ilmo(a) Sr(a): {nome}, ocupante do cargo de {cargo} da obra {obra}", 0, 1)
        pdf.cell(0, 6, "Referente: Reincidencia Habitual e Esgotamento das Sancoes Pedagogicas", 0, 1)
        pdf.ln(4)
        
        texto = (
            f"Encaminhamento formal ao Departamento Juridico para analise de Rescisao por Justa Causa com base no Art. 482, alinea 'e' da CLT "
            f"(desidia no desempenho das respectivas funcoes). Verificado esgotamento de advertencias e suspensoes disciplinares previas."
        )
        pdf.multi_cell(0, 5, texto)
        
    pdf.ln(6)
    pdf.cell(0, 5, f"Sorocaba, SP {data_medida}", 0, 1, "R")
    pdf.ln(6)
    
    # Campo de Assinaturas igual aos modelos
    pdf.cell(90, 5, "Ciente do(a) Empregado(a):", 0, 1, "L")
    pdf.ln(6)
    pdf.cell(90, 5, "_______________________________________", 0, 0, "L")
    pdf.cell(90, 5, "_______________________________________", 0, 1, "R")
    pdf.cell(90, 5, "Testemunha 1", 0, 0, "L")
    pdf.cell(90, 5, "Testemunha 2", 0, 1, "R")
    pdf.ln(6)
    
    # Transcrição oficial Art. 482 da CLT no rodapé
    pdf.set_font("Arial", "B", 7.5)
    pdf.cell(0, 3.5, "Para seu conhecimento, transcrevemos abaixo o Artigo 482 da CLT:", 0, 1)
    pdf.set_font("Arial", "", 6.5)
    clt_text = (
        "Art. 482 Constituem justa causa para rescisão do contrato de trabalho pelo empregador:\n"
        "a) ato de improbidade; b) incontinência de conduta ou mau procedimento; c) negociação habitual; "
        "d) condenação criminal do empregado; e) desídia no desempenho das respectivas funções; f) embriaguez habitual; "
        "g) violação de segredo da empresa; h) ato de indisciplina ou de insubordinação; i) abandono de emprego; "
        "j) ato lesivo da honra ou da boa fama; k) ofensas físicas contra superiores ou empregador; l) prática constante de jogos de azar."
    )
    pdf.multi_cell(0, 3, clt_text)
    
    res = pdf.output(dest='S')
    if isinstance(res, str):
        return res.encode('latin1')
    return bytes(res)

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
            total_f = int(row["TOTAL_FALTAS"])
            data_medida = row.get("DATA_MEDIDA", datetime.now().strftime("%d/%m/%Y"))
            
            # Encarte Visual Colorido
            card_html = f"""
            <div class="card-kanban-solido" style="background-color: {cor_fundo};">
                <div class="card-nome-solido">👤 {row['FUNCIONARIO']}</div>
                <div class="card-detalhe-solido">🔢 <b>Chapa:</b> {chapa_val} | <b>Total Faltas:</b> {total_f}</div>
                <div class="card-detalhe-solido">💼 <b>Cargo:</b> {row.get('CARGO', '-')}</div>
                <div class="card-detalhe-solido">📅 <b>Data da Medida:</b> {data_medida}</div>
                <div class="card-tag-obra-solida">🏗️ {obra_nome}</div>
            </div>
            """
