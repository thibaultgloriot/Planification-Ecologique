import streamlit as st
import pandas as pd
import json
import requests
import plotly.express as px
from datetime import datetime

def show(df, epci_df):
    st.title("📊 Visualisation Cartographique des indicateurs de la Planification Ecologique")
    
    # Sélection de l'échelle
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        echelle = st.radio(
            "Échelle géographique",
            options=["Commune", "EPCI"],
            horizontal=True
        )
    
    with col2:
        # Sélection de l'indicateur
        if echelle=="Commune":
            indicateurs = df['indicateur'].unique()
            selected_indicateur = st.selectbox("Sélectionnez l'indicateur",options=indicateurs)
        else:
            indicateurs = epci_df['indicateur'].unique()
            selected_indicateur = st.selectbox("Sélectionnez l'indicateur",options=indicateurs)
    
    with col3:
        if echelle == "Commune":
            dates_disponibles = sorted(df[df['indicateur'] == selected_indicateur]['date'].unique())
        else:
            if epci_df is not None:
                dates_disponibles = sorted(epci_df[epci_df['indicateur'] == selected_indicateur]['date'].unique())
            else:
                dates_disponibles = sorted(df[df['indicateur'] == selected_indicateur]['date'].unique())
        
        dates_options = [date.strftime('%d/%m/%Y') for date in dates_disponibles]
        
        if dates_options:
            selected_date_str = st.selectbox(
                "Sélectionnez la date",
                options=dates_options,
                index=len(dates_options)-1
            )
            selected_date = datetime.strptime(selected_date_str, '%d/%m/%Y')
        else:
            st.warning("Aucune date disponible pour cet indicateur")
            return
    
    # Filtrage des données selon l'échelle
    if echelle == "Commune":
        filtered_df = df[
            (df['indicateur'] == selected_indicateur) & 
            (df['date'] == selected_date)]
        
        # Récupérer le GeoJSON
        #Voir le programme Création GeoJson communes.py pour plus d'infos
        with open("data/communes.geojson", 'r') as f:
           communes_geojson = json.load(f)
        # Carte communale
        #Source GEoJSON :https://www.data.gouv.fr/datasets/communes-cantons-et-epci-2025-admin-express-cog-plus-ign/
        fig = px.choropleth(
            filtered_df,
            geojson=communes_geojson,
            locations='code_commune',
            featureidkey="properties.code",
            color='valeur',
            hover_name='libelle_commune',
            hover_data={'valeur': True, 'code_commune': False},
            color_continuous_scale="Viridis",
            scope="europe",
            center={"lat": 46.8, "lon": -2.3},
            title=f"{selected_indicateur} à l'échelle communale pour la date {selected_date_str}")
        
    else:  # EPCI
        filtered_df = epci_df[
            (epci_df['indicateur'] == selected_indicateur) & 
            (epci_df['date'] == selected_date)].copy()
            
        # Load GeoJSON and check for data consistency
        #with open("data/EPCI_2025.geojson", 'r') as f:
            #geojson_data = json.load(f)['features']
            #geojson_data['code_epci']=geojson_data['code']
        filtered_df['code']=filtered_df['code_epci']


            
        # Récupérer le GeoJSON
        #Voir le programme Création GeoJson EPCI.py pour plus d'infos
        with open("data/epci.geojson", 'r') as f:
           epci_geojson = json.load(f)
        # Créer la carte
        fig = px.choropleth(
            filtered_df,
            geojson=epci_geojson,  # Utiliser l'objet GeoJSON converti
            locations='code_epci',  # Doit correspondre aux codes dans votre DataFrame
            featureidkey="properties.code",  # Correspond à "code" dans les properties
            color='valeur',
            hover_name='libelle_epci',
            hover_data={'valeur': True, 'code_epci': False},
            color_continuous_scale="Viridis",
            scope="europe",
            center={"lat": 46.8, "lon": -2.3},
            title=f"{selected_indicateur} à l'échelle EPCI pour la date {selected_date_str}",
            subtitle="unité = unité")
        
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(width=1000,height=1000)
    st.plotly_chart(fig, use_container_width=True)

    # Données sous la carte
    st.subheader("Données affichées")
    if echelle == "Commune":
        display_df = filtered_df[['libelle_commune', 'code_commune', 'valeur', 'date']].copy()
    else:
        display_df = filtered_df[['libelle_epci', 'code_epci', 'valeur', 'date']].copy()
    
    display_df['date'] = display_df['date'].dt.strftime('%d/%m/%Y')

    st.dataframe(display_df, use_container_width=True)
