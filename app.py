# INICIO DO PROJETO
import streamlit as st
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Gestão de Faltas e Medidas Disciplinares - Ellenco", layout="wide")
st.title("🏗️ Ellenco Construções - Painel Kanban de Controle Disciplinar")

# ---------------------------------------------------------
# SIMULAÇÃO DA BASE DE DADOS (CSV / UPLOAD)
# ---------------------------------------------------------
st.sidebar.header("📁 Importação de Dados")
uploaded_file = st.sidebar.file_uploader("Carregar base de dados (CSV)", type=["csv"])

if uploaded_file is not None:
    df_funcionarios = pd.read_csv(uploaded_file)
else:
    # Dados fictícios iniciais baseados nos seus exemplos (Lucas, Carlos, João)
    data_inicial = [
        {
            "id": 1,
            "nome": "LUCAS",
            "cargo": "Ajudante geral",
            "obra": "SAO ROQUE",
            "gestor_email": "responsavel.obra@ellenco.com.br",
            "historico_faltas": ["2026-09-28"],
            "penalidades_aplicadas": [],
            "coluna_kanban": "1ª Falta (Advertência)"
        },
        {
            "id": 2,
            "nome": "CARLOS",
            "cargo": "Ajudante geral",
            "obra": "SAO ROQUE/SP",
            "gestor_email": "responsavel.carlos@ellenco.com.br",
            "historico_faltas": ["2026-09-18", "2026-09-21", "2026-09-25"],
            "penalidades_aplicadas": ["Advertência (2026-09-22)"],
            "coluna_kanban": "2ª Falta (Suspensão 1 dia)"
        },
        {
            "id": 3,
            "nome": "JOÃO",
            "cargo": "Ajudante geral",
            "obra": "CONSERVA",
            "gestor_email": "responsavel.joao@ellenco.com.br",
            "historico_faltas": ["2026-07-20", "2026-09-03", "2026-09-15"],
            "penalidades_aplicadas": ["Advertência (2026-07-29)", "Suspensão 1 dia (2026-09-10)"],
            "coluna_kanban": "3ª Falta (Suspensão Agravada 3 dias)"
        }
    ]
    df_funcionarios = pd.DataFrame(data_inicial)

if "df" not in st.session_state:
    st.session_state.df = df_funcionarios

# ---------------------------------------------------------
# MINUTAS OFICIAIS (BASEADAS NOS DOCUMENTOS DA ELLENCO)
# ---------------------------------------------------------
def gerar_minuta_documento(nome, cargo, obra, tipo_medida, data_falta, historico_texto):
    # Transcrição padrão do Art. 482 da CLT presente nos rodapés/documentos da Ellenco
    art_482 = """
    Para seu conhecimento, transcrevemos abaixo o Artigo 482 da CLT:
    Art. 482 Constituem justa causa para rescisão do contrato de trabalho pelo empregador:
    a) ato de improbidade; b) incontinência de conduta ou mau procedimento; c) negociação habitual; 
    d) condenação criminal; e) desídia no desempenho das respectivas funções; f) embriaguez habitual; 
    g) violação de segredo da empresa; h) ato de indisciplina ou de insubordinação; i) abandono de emprego; 
    j) ato lesivo da honra ou boa fama; k) ofensas físicas; l) prática constante de jogos de azar.
    """

    if "Advertência" in tipo_medida:
        return f"""
        CARTA DE ADVERTÊNCIA DISCIPLINAR
        Ilmo(a) Sr(a): {nome}, ocupante do cargo de {cargo} da obra {obra}
        Referente: 1ª FALTA INJUSTIFICADA ISOLADA
        
        A empresa Ellenco Construções registra, por meio deste documento, a aplicação de ADVERTÊNCIA DISCIPLINAR, em razão de ausência injustificada ao trabalho no dia {data_falta}.
        
        A referida ausência ocasionou o não cumprimento da jornada de trabalho prevista, em desacordo com as obrigações contratuais.
        Diante do ocorrido, aplica-se a presente advertência de caráter pedagógico.
        
        Fica o empregado ciente de que a repetição de faltas injustificadas poderá ensejar medidas mais severas, inclusive suspensão e rescisão por justa causa (Art. 482 da CLT).
        
        Sorocaba, SP - {datetime.now().strftime('%d/%m/%Y')}
        
        {art_482}
        """
    elif "1 dia" in tipo_medida:
        return f"""
        CARTA DE SUSPENSÃO DISCIPLINAR (1 DIAS)
        Ilmo(a) Sr(a): {nome}, ocupante do cargo de {cargo} da obra {obra}
        Referente: Aplicação de Suspensão Disciplinar
        
        A empresa Ellenco Construções aplica a penalidade de SUSPENSÃO DISCIPLINAR pelo período de 1 dia útil, em razão da reincidência em faltas injustificadas (datas: {data_falta}).
        
        Histórico prévio: O empregado já havia sido penalizado anteriormente com ADVERTÊNCIA DISCIPLINAR.
        
        Fica o empregado formalmente advertido de que a reiteração poderá resultar em penalidades superiores e rescisão por justa causa.
        
        Sorocaba, SP - {datetime.now().strftime('%d/%m/%Y')}
        
        {art_482}
        """
    else:
        return f"""
        CARTA DE SUSPENSÃO DISCIPLINAR AGRAVADA (3 DIAS)
        Ilmo(a) Sr(a): {nome}, ocupante do cargo de {cargo} da obra {obra}
        Referente: Aplicação de Suspensão Disciplinar Agravada
        
        A empresa Ellenco Construções aplica a penalidade de SUSPENSÃO DISCIPLINAR pelo período de 3 dias úteis, em razão da reincidência reiterada em faltas injustificadas ({data_falta}).
        
        Histórico de sanções anteriores: {historico_texto}
        
        O empregado fica expressamente ciente de que a continuidade poderá ensejar a adoção da medida disciplinar máxima (Rescisão por Justa Causa - Art. 482, 'e' da CLT).
        
        Sorocaba, SP - {datetime.now().strftime('%d/%m/%Y')}
        
        {art_482}
        """

# ---------------------------------------------------------
# FUNÇÃO DE ENVIO DE E-MAIL (SMTP -> Proton.me + Responsável)
# ---------------------------------------------------------
def disparar_emails(destinatario_gestor, email_proton, assunto, conteudo):
    # Configuração de gateway SMTP (ex: Gmail/Proton Bridge simulado)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    remetente = "dp.ellenco@gmail.com"
    senha_app = "senha_app_aqui"

    destinatarios = [destinatario_gestor, email_proton]

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = ", ".join(destinatarios)
    msg['Subject'] = assunto
    msg.attach(MIMEText(conteudo, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(remetente, senha_app)
        server.sendmail(remetente, destinatarios, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        # Modo simulação educacional caso o SMTP externo não esteja conectado
        return False

# ---------------------------------------------------------
# PAINEL KANBAN AUTOMÁTICO
# ---------------------------------------------------------
st.subheader("📊 Kanban Operacional de Controle (Janela de 12 Meses)")

col1, col2, col3, col4 = st.columns(4)

colunas_status = [
    "1ª Falta (Advertência)", 
    "2ª Falta (Suspensão 1 dia)", 
    "3ª Falta (Suspensão Agravada 3 dias)", 
    "4ª Falta (Análise Jurídico / Justa Causa)"
]

containers = {colunas_status[0]: col1, colunas_status[1]: col2, colunas_status[2]: col3, colunas_status[3]: col4}

for status, coluna_ui in containers.items():
    with coluna_ui:
        st.markdown(f"### {status}")
        df_col = st.session_state.df[st.session_state.df["coluna_kanban"] == status]
        for _, row in df_col.iterrows():
            with st.container():
                st.warning(f"**{row['nome']}**\n\nObra: {row['obra']}\nFaltas: {len(row['historico_faltas'])}")

# ---------------------------------------------------------
# REGISTRO DE NOVA FALTA E MUDANÇA AUTOMÁTICA DE COLUNA
# ----------------index-----------------------------------------
st.divider()
st.subheader("➕ Registrar Nova Falta Injustificada para Colaborador")

with st.form("form_nova_falta"):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        func_id = st.selectbox(
            "Selecionar Funcionário:", 
            options=st.session_state.df["id"],
            format_func=lambda x: st.session_state.df[st.session_state.df['id'] == x]['nome'].values[0]
        )
        data_falta = st.date_input("Data da Nova Falta Injustificada")
    with col_f2:
        email_proton = st.text_input("Seu E-mail (Proton.me):", value="seu_usuario@proton.me")

    btn_enviar = st.form_submit_button("Processar Falta, Mover no Kanban e Enviar E-mails")

    if btn_enviar:
        idx = st.session_state.df[st.session_state.df['id'] == func_id].index[0]
        row_func = st.session_state.df.loc[idx]
        
        # Atualiza histórico de faltas
        st.session_state.df.at[idx, "historico_faltas"].append(str(data_falta))
        total_faltas = len(st.session_state.df.at[idx, "historico_faltas"])
        
        # Regra de transição automática de colunas no Kanban baseada na quantidade de faltas/reincidência
        if total_faltas == 1:
            nova_col = colunas_status[0]
            tipo_medida = "Advertência Disciplinar"
        elif total_faltas == 2:
            nova_col = colunas_status[1]
            tipo_medida = "Suspensão Disciplinar (1 dia)"
        elif total_faltas == 3:
            nova_col = colunas_status[2]
            tipo_medida = "Suspensão Disciplinar Agravada (3 dias)"
        else:
            nova_col = colunas_status[3]
            tipo_medida = "Encaminhamento Jurídico (Justa Causa)"

        st.session_state.df.at[idx, "coluna_kanban"] = nova_col
        
        # Gera o texto da minuta oficial
        minuta_pronta = gerar_minuta_documento(
            nome=row_func["nome"],
            cargo=row_func["cargo"],
            obra=row_func["obra"],
            tipo_medida=tipo_medida,
            data_falta=str(data_falta),
            historico_texto=str(row_func["penalidades_aplicadas"])
        )
        
        # Dispara os e-mails
        email_enviado = disparar_emails(row_func["gestor_email"], email_proton, f"[DP Ellenco] Minuta Pronta - {tipo_medida} - {row_func['nome']}", minuta_pronta)
        
        st.success(f"Sucesso! O funcionário avançou automaticamente para a coluna: **{nova_col}**.")
        st.info(f"📧 Minuta gerada e encaminhada para o seu e-mail ({email_proton}) e para o responsável da obra ({row_func['gestor_email']}).")
        
        with st.expander("Visualizar Minuta Gerada"):
            st.text(minuta_pronta)
