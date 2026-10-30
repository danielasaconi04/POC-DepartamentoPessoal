import streamlit as st
import pandas as pd
import glob
os = __import__('os')

# ---------------------------------------------------------
# CARREGAMENTO E ACúMULO AUTOMÁTICO DE TODAS AS PLANILHAS DA PASTA 'dados/'
# ---------------------------------------------------------
def carregar_e_acumular_dados():
    dfs = []
    
    # Procura por todos os arquivos .xlsx dentro da pasta 'dados'
    caminho_pasta = "dados/*.xlsx"
    arquivos_excel = glob.glob(caminho_pasta)
    
    # Caso não use pasta e coloque direto na raiz, mude para glob.glob("*.xlsx")
    if not arquivos_excel:
        arquivos_excel = glob.glob("*.xlsx")

    for arq in arquivos_excel:
        try:
            # Tenta ler a aba padrão de exportação do seu sistema
            df_temp = pd.read_excel(arq, sheet_name="Exportar Planilha")
            dfs.append(df_temp)
        except Exception:
            try:
                # Se não achar a aba específica, lê a primeira aba da planilha
                df_temp = pd.read_excel(arq)
                dfs.append(df_temp)
            except Exception as e:
                print(f"Erro ao ler o arquivo {arq}: {e}")
                
    if dfs:
        # Une todas as planilhas em um único DataFrame acumulado
        df_unificado = pd.concat(dfs, ignore_index=True)
        
        # Limpeza opcional: se houver registros duplicados exatos pela CHAPA, 
        # mantemos a versão mais recente ou unificamos as faltas se necessário.
        # Aqui garantimos que as informações somem em vez de apagar as antigas.
        return df_unificado
    else:
        # Fallback padrão caso nenhuma planilha seja encontrada ainda
        return pd.DataFrame([
            {"CHAPA": 1, "FUNCIONARIO": "DIEGO", "CARGO": "Ajudante geral", "SECAO": "DER/SP - TATUI", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 1},
            {"CHAPA": 2, "FUNCIONARIO": "JOSE", "CARGO": "Ajudante geral", "SECAO": "CCR - SÃO ROQUE", "DATA_1": "28/09/2026", "TOTAL_FALTAS": 2}
        ])

# Inicializa os dados na sessão do Streamlit
if "df_dados" not in st.session_state:
    st.session_state.df_dados = carregar_e_acumular_dados()

df = st.session_state.df_dados
