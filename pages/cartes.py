import streamlit as st
import pandas as pd
import json
import requests
import plotly.express as px
from datetime import datetime
import numpy as np

@st.cache_data
def load_geojson(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

@st.cache_data
def load_indicator_sources():
    """Charge les sources des indicateurs depuis le fichier CSV"""
    try:
        sources_df = pd.read_csv("data/columns_indicateurs.csv", sep=",")
        if 'Nouveau_nom_indicateur' in sources_df.columns:
            sources_dict = dict(zip(sources_df['Nouveau_nom_indicateur'], sources_df.get('Source', '')))
        else:
            sources_dict = dict(zip(sources_df['Indicateur'], sources_df.get('Source', '')))
        return sources_dict
    except Exception as e:
        st.warning(f"Impossible de charger les sources des indicateurs: {e}")
        return {}

def get_surface_population_data(df, echelle, date_reference):
    """Récupère les données de surface et population"""
    surface_df = None
    population_df = None
    
    if df is not None and not df.empty:
        # Surface (valeur unique - la plus récente)
        surface_data = df[df['indicateur'] == "Surface totale du territoire (ha)"].copy()
        if not surface_data.empty:
            surface_df = surface_data.sort_values('date').groupby(
                ['code_commune'] if echelle == "Commune" else ['code_epci']
            ).last().reset_index()
        
        # Population (valeur la plus proche de la date de référence)
        population_data = df[df['indicateur'] == "Nombre d'habitants du territoire"].copy()
        if not population_data.empty:
            population_dfs = []
            code_col = 'code_commune' if echelle == "Commune" else 'code_epci'
            
            for code, group in population_data.groupby(code_col):
                dates = group['date'].values
                mask = dates <= np.datetime64(date_reference)
                
                if mask.any():
                    idx = np.where(mask)[0][-1]
                else:
                    idx = 0
                
                population_dfs.append(group.iloc[[idx]])
            
            if population_dfs:
                population_df = pd.concat(population_dfs, ignore_index=True)
                population_df['valeur'] = population_df['valeur'] / 1000
    
    return surface_df, population_df

def normalize_by_surface(df, code_col, surface_df):
    """Normalise les valeurs par surface"""
    df_normalized = df.copy()
    df_normalized = df_normalized.merge(
        surface_df[[code_col, 'valeur']].rename(columns={'valeur': 'surface_ha'}),
        on=code_col, how='left'
    )
    df_normalized['valeur_normalisee'] = df_normalized['valeur'] / df_normalized['surface_ha']
    df_normalized['unite_normalisee'] = 'par hectare'
    return df_normalized

def normalize_by_population(df, code_col, population_df):
    """Normalise les valeurs par population"""
    df_normalized = df.copy()
    df_normalized = df_normalized.merge(
        population_df[[code_col, 'valeur']].rename(columns={'valeur': 'population_milliers'}),
        on=code_col, how='left'
    )
    df_normalized['valeur_normalisee'] = df_normalized['valeur'] / df_normalized['population_milliers']
    df_normalized['unite_normalisee'] = 'pour 1000 hab.'
    return df_normalized

def get_scale_options(df, column):
    """Calcule les différentes échelles de représentation"""
    values = df[column].dropna()
    
    if len(values) == 0:
        return None, None, None
    
    linear_scale = [values.min(), values.max()]
    percentile_scale = [np.percentile(values, 5), np.percentile(values, 95)]
    
    mean_val = values.mean()
    std_val = values.std()
    std_scale = [max(values.min(), mean_val - 2*std_val), 
                 min(values.max(), mean_val + 2*std_val)]
    
    return linear_scale, percentile_scale, std_scale

def get_common_themes(df, epci_df):
    """Récupère les thématiques communes"""
    themes_communes = set(df['thematique'].dropna().unique()) if df is not None else set()
    themes_epci = set(epci_df['thematique'].dropna().unique()) if epci_df is not None else set()
    
    themes_communs = themes_communes.intersection(themes_epci)
    
    if not themes_communs:
        return sorted(themes_communes) if themes_communes else sorted(themes_epci)
    
    return sorted(themes_communs)

def show(df, epci_df):
    indicator_sources = load_indicator_sources()
    
    st.title("📊 Visualisation Cartographique des indicateurs de la Planification Ecologique")
    
    common_themes = get_common_themes(df, epci_df)
    
    col1, col2, col3, col4 = st.columns([1, 0.7, 1.5, 0.6])
    
    with col1:
        echelle = st.radio("Échelle géographique", options=["Commune", "EPCI"], horizontal=True)
    
    with col2:
        if common_themes:
            selected_thematique = st.selectbox("Thématique", ["Toutes"] + list(common_themes))
        else:
            selected_thematique = "Toutes"
    
    with col3:
        df_to_use = df if echelle == "Commune" else epci_df
        
        if selected_thematique != "Toutes" and 'thematique' in df_to_use.columns:
            filtered_df = df_to_use[df_to_use['thematique'] == selected_thematique]
            indicateurs = filtered_df['indicateur'].unique()
        else:
            indicateurs = df_to_use['indicateur'].unique()
        
        indicateurs_exclus = ["Surface totale du territoire (ha)", "Nombre d'habitants du territoire"]
        indicateurs_filtres = [ind for ind in indicateurs if ind not in indicateurs_exclus]
        
        selected_indicateur = st.selectbox("Indicateur", indicateurs_filtres)
    
    with col4:
        df_to_use = df if echelle == "Commune" else epci_df
        dates_disponibles = sorted(df_to_use[df_to_use['indicateur'] == selected_indicateur]['date'].unique())
        selected_date_str = st.selectbox("Date", [d.strftime('%d/%m/%Y') for d in dates_disponibles], index=len(dates_disponibles)-1)
        selected_date = datetime.strptime(selected_date_str, '%d/%m/%Y')
    
    # Section normalisation
    st.markdown("---")
    col_norm, col_scale1, col_scale2 = st.columns([0.7, 0.5, 0.5])
    
    with col_norm:
        normalisation_option = st.selectbox("Normalisation (par surface ou par population)", ["Aucune", "Par surface (ha)", "Par population (1000 hab.)"])
    
    # Section échelle de couleur
    with col_scale1:
        scale_options = st.selectbox("Échelle de couleur", ["Blues", "Greens", "Darkmint", "ice","Reds"])
    
    with col_scale2:
        stat_scale = st.selectbox("Répartition", ["Min-Max", "Percentiles 5-95%", "Moyenne ± 2σ"])
        reverse_scale = st.checkbox("Inverser l'échelle")
    
    # Récupération des données de normalisation
    if echelle == "Commune":
        surface_df, population_df = get_surface_population_data(df, "Commune", selected_date)
        filtered_df = df[(df['indicateur'] == selected_indicateur) & (df['date'] == selected_date)].copy()
        code_col = 'code_commune'
    else:
        surface_df, population_df = get_surface_population_data(epci_df, "EPCI", selected_date)
        filtered_df = epci_df[(epci_df['indicateur'] == selected_indicateur) & (epci_df['date'] == selected_date)].copy()
        code_col = 'code_epci'
    
    # Application de la normalisation
    suffixe_titre = ""
    if normalisation_option == "Par surface (ha)" and surface_df is not None:
        filtered_df = normalize_by_surface(filtered_df, code_col, surface_df)
        valeur_colonne = 'valeur_normalisee'
        suffixe_titre = " (par hectare)"
    elif normalisation_option == "Par population (1000 hab.)" and population_df is not None:
        filtered_df = normalize_by_population(filtered_df, code_col, population_df)
        valeur_colonne = 'valeur_normalisee'
        suffixe_titre = " (pour 1000 habitants)"
    else:
        valeur_colonne = 'valeur'
    
    # Calcul des échelles statistiques
    linear_scale, percentile_scale, std_scale = get_scale_options(filtered_df, valeur_colonne)
    
    if stat_scale == "Min-Max" and linear_scale:
        range_color = linear_scale
        range_note = f"min={linear_scale[0]:.2f}, max={linear_scale[1]:.2f}"
    elif stat_scale == "Percentiles 5-95%" and percentile_scale:
        range_color = percentile_scale
        range_note = f"5e={percentile_scale[0]:.2f}, 95e={percentile_scale[1]:.2f}"
    elif stat_scale == "Moyenne ± 2σ" and std_scale:
        range_color = std_scale
        range_note = f"m±2σ=[{std_scale[0]:.2f}, {std_scale[1]:.2f}]"
    else:
        range_color = None
        range_note = "Auto"
    
    color_scale = scale_options + ("_r" if reverse_scale else "")
    
    # Création de la carte
    if echelle == "Commune":
        communes_geojson = load_geojson("data/communes_simple.geojson")
        
        source_text = ""
        if selected_indicateur in indicator_sources and pd.notna(indicator_sources[selected_indicateur]):
            source_text = f"<br><sub>Source : {indicator_sources[selected_indicateur]}</sub>"
        
        fig = px.choropleth(
            filtered_df,
            geojson=communes_geojson,
            locations='code_commune',
            featureidkey="properties.code",
            color=valeur_colonne,
            hover_name='libelle_commune',
            hover_data={valeur_colonne: True, 'code_commune': False},
            color_continuous_scale=color_scale,
            range_color=range_color,
            scope="europe",
            center={"lat": 46.8, "lon": -2.3},
            title=f"{selected_indicateur}{suffixe_titre} au {selected_date_str}<br><sub>{range_note}</sub>{source_text}")
        
    else:
        epci_geojson = load_geojson("data/epci_simple.geojson")
        
        source_text = ""
        if selected_indicateur in indicator_sources and pd.notna(indicator_sources[selected_indicateur]):
            source_text = f"<br><sub>Source : {indicator_sources[selected_indicateur]}</sub>"
        
        fig = px.choropleth(
            filtered_df,
            geojson=epci_geojson,
            locations='code_epci',
            featureidkey="properties.code",
            color=valeur_colonne,
            hover_name='libelle_epci',
            hover_data={valeur_colonne: True, 'code_epci': False},
            color_continuous_scale=color_scale,
            range_color=range_color,
            scope="europe",
            center={"lat": 46.8, "lon": -2.3},
            title=f"{selected_indicateur}{suffixe_titre} au {selected_date_str}<br><sub>{range_note}</sub>{source_text}")
    
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(width=1000, height=1000)
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques
    with st.expander("📈 Statistiques descriptives"):
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Moyenne", f"{filtered_df[valeur_colonne].mean():.2f}")
        with col_stat2:
            st.metric("Médiane", f"{filtered_df[valeur_colonne].median():.2f}")
        with col_stat3:
            st.metric("Écart-type", f"{filtered_df[valeur_colonne].std():.2f}")
    
    # Tableau des données
    st.subheader("Données affichées")
    if echelle == "Commune":
        display_cols = ['libelle_commune', 'code_commune', valeur_colonne, 'date']
    else:
        display_cols = ['libelle_epci', 'code_epci', valeur_colonne, 'date']
    
    display_df = filtered_df[display_cols].copy()
    display_df['date'] = display_df['date'].dt.strftime('%d/%m/%Y')
    
    if valeur_colonne == 'valeur_normalisee':
        if normalisation_option == "Par surface (ha)":
            display_df.rename(columns={'valeur_normalisee': 'Valeur (par ha)'}, inplace=True)
        elif normalisation_option == "Par population (1000 hab.)":
            display_df.rename(columns={'valeur_normalisee': 'Valeur (pour 1000 hab.)'}, inplace=True)
    
    st.dataframe(display_df, use_container_width=True)
