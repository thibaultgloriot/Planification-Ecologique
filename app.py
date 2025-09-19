import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="Observatoire des Communes",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed")

# Chargement du logo
logo = Image.open('assets/logo.png')

# Sidebar avec navigation
with st.sidebar:
    st.image(logo, width=200)
    st.title("Indicateurs de la Planification Ecologique")
    
    # Navigation par onglets
    page = st.radio("Navigation", ["🗺️ Accès aux cartes", "📊 Accès aux données brutes"])

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv('data/final_df_communes.csv')
    # Conversion des dates en format datetime
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
    # Suppression des lignes avec dates invalides si nécessaire
    df['code_commune'] = df['code_commune'].astype(str)
    df = df.dropna(subset=['date'])
    return df

@st.cache_data
def load_epci_data():
    # Charger les données EPCI (à adapter selon votre fichier)
    try:
        epci_df = pd.read_csv('data/final_df_epci.csv')
        epci_df.rename(columns={'nom':'libelle_epci'},inplace=True)
        epci_df['date'] = pd.to_datetime(epci_df['date'], format='%d/%m/%Y', errors='coerce')
        epci_df['code_epci'] = epci_df['code_epci'].astype(str)
        return epci_df
    except FileNotFoundError:
        return None
    return None

df = load_data()
epci_df = load_epci_data()

# Pages
if "🗺️ Accès aux cartes" in page:
    import pages.cartes
    pages.cartes.show(df, epci_df)
    
elif "📊 Accès aux données brutes" in page:
    import pages.donnees_brutes
    pages.donnees_brutes.show(df)