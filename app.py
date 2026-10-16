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
# TRATAMENTO DE TEXTO
# ---------------------------------------------------------
def limpar(texto):
    return str(texto).encode('latin-1', 'replace').decode('latin-1')

# ---------------------------------------------------------
# GERADOR DE PDF ESTRUTURADO (MODELO OFICIAL ELLENCO)
# ---------------------------------------------------------
def gerar_pdf_perfeito_ellenco(nome, chapa, cargo, obra, total_faltas, data_1, data_2, data_3):
    pdf = FPDF(unit="mm", format="A4")
    pdf.add_page()
    
    nc = limpar(nome)
    cc = limpar(cargo)
    oc = limpar(obra)
    
    # 1. Cabeçalho Superior Ellenco
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(20, 40, 110)
    pdf.cell(130, 8, "", 0, 0)
    pdf.cell(50, 8, "Ellenco", 0, 1, "R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)
    
    # Caixa do Título Principal
    pdf.set_font("Arial", "B", 11)
    pdf.rect(10, 20, 190, 8)
    pdf.set_xy(10, 21)
    if total_faltas == 1:
        pdf.cell(190, 6, "CARTA DE ADVERTÊNCIA DISCIPLINAR", 0, 1, "C")
    elif total_faltas == 2 or total_faltas == 3:
        pdf.cell(190, 6, "CARTA DE SUSPENSAO DISCIPLINAR", 0, 1, "C")
    else:
        pdf.cell(190, 6, "ENCAMINHAMENTO AO DEPARTAMENTO JURÍDICO", 0, 1, "C")
        
    pdf.ln(4)
    
    # 2. Caixa do Texto Principal com Bordas
    pdf.rect(10, 30, 190, 105)
    pdf.set_xy(12, 32)
    
    pdf.set_font("Arial", "B", 9.5)
    pdf.cell(0, 5, limpar(f"Ilmo(a) Sr(a): {nc}, ocupante do cargo de {cc} da obra {oc}"), 0, 1, "L")
    pdf.set_x(12)
    
    if total_faltas == 1:
        pdf.cell(0, 5, "Referente: 1ª FALTA INJUSTIFICADA ISOLADA", 0, 1, "L")
        pdf.ln(2)
        d1 = str(data_1) if pd.notna(data_1) else "28/09/2026"
        texto = (
            f"A empresa Ellenco Construções registra, por meio deste documento, a aplicação de ADVERTÊNCIA DISCIPLINAR, "
            f"em razão de ausência injustificada ao trabalho.\n\n"
            f"Conforme registros de frequência, foi constatada a ausência do empregado no dia {d1} sem que houvesse "
            f"apresentação de justificativa legalmente válida ou documento apto a justificar a ausência.\n\n"
            f"A referida ausência ocasionou o não cumprimento da jornada de trabalho prevista para a respectiva data, em "
            f"desacordo com as obrigações decorrentes do contrato de trabalho e das normas internas da empresa.\n\n"
            f"Registra-se que, até o momento da aplicação desta penalidade, não foi apresentada justificativa legal capaz de "
            f"afastar a caracterização da falta.\n\n"
            f"Diante do ocorrido, a empresa aplica a presente ADVERTÊNCIA DISCIPLINAR, de caráter pedagógico, para que "
            f"o(a) empregado(a) observe rigorosamente sua jornada de trabalho e comunique previamente à empresa eventual "
            f"impossibilidade de comparecimento, apresentando, quando cabível, a respectiva justificativa.\n\n"
            f"Fica o empregado ciente de que a repetição de faltas injustificadas poderá ensejar a adoção de medidas "
            f"disciplinares mais severas, de acordo com a gravidade e a reiteração da conduta, inclusive suspensão disciplinar e, "
            f"em situações que assim o justifiquem, a rescisão do contrato por justa causa, nos termos do art. 482 da CLT."
        )
    elif total_faltas == 2:
        pdf.cell(0, 5, "Referente: Aplicação de Suspensão Disciplinar", 0, 1, "L")
        pdf.ln(2)
        d_atual = str(data_2) if pd.notna(data_2) else "25/09/2026"
        d_ant = str(data_1) if pd.notna(data_1) else "18/09/2026"
        texto = (
            f"A empresa Ellenco Construções aplica, por meio deste documento, a penalidade de SUSPENSÃO DISCIPLINAR "
            f"pelo período de 1 dia útil, em razão da reincidência reiterada em faltas injustificadas ao trabalho.\n\n"
            f"Foi constatada a ausência do empregado no dia {d_atual}, sem apresentação de justificativa legal válida.\n\n"
            f"Registra-se que o empregado já havia sido penalizado anteriormente com ADVERTÊNCIA DISCIPLINAR, aplicada "
            f"em {d_ant}, em razão de falta injustificada ocorrida.\n\n"
            f"Apesar da orientação e da penalidade anteriormente aplicada, houve nova ocorrência de ausência injustificada, "
            f"demonstrando a repetição da conduta.\n\n"
            f"Diante da reincidência, fica aplicada a presente SUSPENSAO DISCIPLINAR, pelo período de 1 dia útil, "
            f"sem prejuízo dos efeitos legais decorrentes da suspensão.\n\n"
            f"O empregado fica formalmente advertido de que a repetição de faltas injustificadas poderá resultar na aplicação de "
            f"penalidades disciplinares mais severas, inclusive suspensão por período superior e rescisão do contrato por justa causa."
        )
    elif total_faltas == 3:
        pdf.cell(0, 5, "Referente: Aplicação de Suspensão Disciplinar Agravada", 0, 1, "L")
        pdf.ln(2)
        d3 = str(data_3) if pd.notna(data_3) else "15/09/2026"
        d1 = str(data_1) if pd.notna(data_1) else "20/07/2026"
        d2 = str(data_2) if pd.notna(data_2) else "03/09/2026"
        texto = (
            f"A empresa Ellenco Construções aplica, por meio deste documento, a penalidade de SUSPENSAO DISCIPLINAR AGRAVADA "
            f"pelo período de 3 dias úteis, em razão da reincidência reiterada em faltas injustificadas ao trabalho.\n\n"
            f"Conforme registros de frequência, foi constatada nova ausência injustificada do empregado em {d3}.\n\n"
            f"A presente ocorrência não constitui fato isolado. O empregado já foi anteriormente penalizado por faltas "
            f"injustificadas, tendo recebido:\n"
            f"a) Advertência disciplinar, aplicada em {d1}, em razão da ausência anterior; e\n"
            f"b) Suspensão disciplinar de 1 dia, aplicada em {d2}, em razão da ausência anterior.\n\n"
            f"Mesmo após as medidas disciplinares anteriormente aplicadas e a ciência expressa acerca da necessidade de "
            f"observância da jornada de trabalho, ocorreu nova falta injustificada.\n\n"
            f"Diante da persistência da conduta, a empresa aplica a presente SUSPENSÃO DISCIPLINAR DE 3 DIAS ÚTEIS.\n\n"
            f"O empregado fica expressamente ciente de que a continuidade ou reiteração poderá ensejar a rescisão do contrato por justa causa."
        )
    else:
        pdf.cell(0, 5, "Referente: Encaminhamento Jurídico - Justa Causa", 0, 1, "L")
        pdf.ln(2)
        texto = "Encaminhamento formal ao Departamento Jurídico para análise de Rescisão por Justa Causa (Art. 482, alínea 'e' da CLT)."

    pdf.set_font("Arial", "", 8.5)
    pdf.set_x(12)
    pdf.multi_cell(186, 4.2, limpar(texto))
    
    pdf.set_xy(12, 131)
    pdf.set_font("Arial", "", 9)
    pdf.cell(186, 5, "Sorocaba, SP 02/10/2026", 0, 1, "R")
    pdf.cell(186, 5, "ELLENCO", 0, 1, "C")
    
    # 3. Caixa de Assinaturas e Testemunhas
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
    
    # 4. Caixa do Artigo 482 da CLT
    pdf.rect(10, 174, 190, 48)
    pdf.set_xy(12, 175)
    pdf.set_font("Arial", "B", 7.5)
    pdf.cell(186, 4, "Para seu conhecimento, transcrevemos abaixo o Artigo 482 da CLT:", 0, 1, "L")
    
    pdf.set_font("Arial", "", 5.8)
    pdf.set_x(12)
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
        "l) prática constante de jogos de azar.\n"
        "Parágrafo único - Constitui igualmente justa causa para dispensa de emprego a prática, devidamente comprovada em inquérito administrativo, de atos atentatórios contra a segurança nacional."
    )
    pdf.multi_cell(186, 2.5, limpar(clt_text))
    
    # 5. Rodapé Institucional com Endereços Oficiais
    pdf.set_xy(10, 224)
    pdf.set_font("Arial", "", 6)
    pdf.cell(95, 3, "Av. Antônio Bardella, 3 444 - Iporanga - Distrito Industrial", 0, 0, "L")
    pdf.cell(95, 3, "Av. Roberto Simonsen, 47 - Santa Rosália", 0, 1, "R")
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
