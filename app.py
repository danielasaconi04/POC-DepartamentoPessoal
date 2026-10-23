import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (LAYOUT CORPORATIVO AJUSTADO)
# ---------------------------------------------------------
st.set_page_config(page_title="Ellenco Construções - Gestão Disciplinar", layout="wide")

st.markdown("""
    <style>
    /* Fundo Geral da Aplicação */
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    
    /* Cabeçalho Empresarial Ellenco */
    .header-empresarial {
        background-color: #0F172A;
        padding: 18px 25px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        border-bottom: 4px solid #1E40AF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-titulo {
        color: #FFFFFF;
        font-size: 22px;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .header-sub {
        color: #94A3B8;
        font-size: 13px;
        margin: 0;
    }
    
    /* Reformulação da Barra de Filtros Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
    }
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        color: #FFFFFF !important;
        border-radius: 6px;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 6px;
    }
    
    /* Cartões / Catálogos do Kanban com Cores Suaves e Transparência (RGBA) */
    .card-kanban-suave {
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        font-family: sans-serif;
        backdrop-filter: blur(4px);
    }
    .card-nome-suave {
        font-weight: 800;
        font-size: 15px;
        margin-bottom: 6px;
        color: #0F172A !important;
    }
    .card-detalhe-suave {
        font-size: 12px;
        margin-bottom: 4px;
        color: #334155 !important;
    }
    .card-tag-obra-suave {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.85);
        color: #0F172A !important;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: bold;
        margin-top: 6px;
        border: 1px solid rgba(15, 23, 42, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CABEÇALHO EMPRESARIAL
# ---------------------------------------------------------
st.markdown("""
    <div class="header-empresarial">
        <div>
            <p class="header-titulo">🏗️ ELLENCO CONSTRUÇÕES</p>
            <p class="header-sub">Departamento Pessoal — Gestão Disciplinar Corporativa</p>
        </div>
        <div style="text-align: right;">
            <span style="background-color: #1E40AF; color: white; padding: 6px 14px; border-radius: 4px; font-weight: bold; font-size: 12px; letter-spacing: 1px;">PORTAL DP</span>
        </div>
    </div>
""", unsafe_allow_html=
