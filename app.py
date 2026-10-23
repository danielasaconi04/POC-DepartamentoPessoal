# ---------------------------------------------------------
# LEITURA DA PLANILHA CORPORATIVA (WF0031.xlsx)
# ---------------------------------------------------------
@st.cache_data
def carregar_dados():
    # Lê rigorosamente a aba 'Exportar Planilha' do seu arquivo WF0031.xlsx
    df = pd.read_excel("WF0031.xlsx", sheet_name="Exportar Planilha")
    return df

if "df_dados" not in st.session_state:
    st.session_state.df_dados = carregar_dados()

df = st.session_state.df_dados

# Mapeamento automático das etapas conforme o total de faltas da planilha
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
