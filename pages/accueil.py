import streamlit as st
import pandas as pd
import numpy as np

def show(df, epci_df):
    st.title("🏠 Tableau de bord - Observatoire Régional de la Planification Ecologique")
    
    # KPI globaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Nombre d'indicateurs à l'échelle commune", df['indicateur'].nunique())
    with col2:
        st.metric("Nombre d'indicateurs à l'échelle EPCI", epci_df['indicateur'].nunique())
    
    with col3:
        st.metric("Nombre de communes", df['code_commune'].nunique())
    
    with col4:
        if epci_df is not None:
            st.metric("Nombre d'EPCI", 61)
        else:
            st.metric("Période couverte", f"{df['date'].min().year}-{df['date'].max().year}")
    
    # Liste des indicateurs disponibles par thématique
    st.subheader("📋 Indicateurs disponibles par thématique")
    
    # Créer une liste combinée des thématiques
    themes_communes = df['thematique'].unique() if 'thematique' in df.columns else []
    themes_epci = epci_df['thematique'].unique() if 'thematique' in epci_df.columns else []
    
    # Fusionner les thématiques uniques
    all_thematiques = sorted(set(list(themes_communes) + list(themes_epci)))
    
    if len(all_thematiques) > 0:
        for thematique in all_thematiques:
            with st.expander(f"{thematique}"):
                # Collecter les indicateurs de cette thématique depuis les deux sources
                indicateurs_communes = []
                indicateurs_epci = []
                indicateurs_communes_epci = []  # Indicateurs présents dans les deux
                
                # Vérifier dans df (communes)
                if 'thematique' in df.columns:
                    mask_communes = df['thematique'] == thematique
                    indicateurs_communes = df[mask_communes]['indicateur'].unique()
                
                # Vérifier dans epci_df (EPCI)
                if 'thematique' in epci_df.columns:
                    mask_epci = epci_df['thematique'] == thematique
                    indicateurs_epci = epci_df[mask_epci]['indicateur'].unique()
                
                # Identifier les indicateurs communs
                indicateurs_communes_set = set(indicateurs_communes)
                indicateurs_epci_set = set(indicateurs_epci)
                
                indicateurs_communes_seulement = list(indicateurs_communes_set - indicateurs_epci_set)
                indicateurs_epci_seulement = list(indicateurs_epci_set - indicateurs_communes_set)
                indicateurs_communes_epci = list(indicateurs_communes_set.intersection(indicateurs_epci_set))
                
                # Afficher les indicateurs avec leurs disponibilités
                if len(indicateurs_communes_epci) > 0:
                    st.markdown("**📊 Disponible aux deux échelles (communes et EPCI):**")
                    for ind in sorted(indicateurs_communes_epci):
                        st.write(f"• {ind}")
                
                if len(indicateurs_communes_seulement) > 0:
                    st.markdown("**🏘️ Disponible uniquement à l'échelle communale:**")
                    for ind in sorted(indicateurs_communes_seulement):
                        st.write(f"• {ind}")
                
                if len(indicateurs_epci_seulement) > 0:
                    st.markdown("**🏢 Disponible uniquement à l'échelle EPCI:**")
                    for ind in sorted(indicateurs_epci_seulement):
                        st.write(f"• {ind}")
                
                # Afficher un résumé statistique
                st.caption(f"*Total: {len(indicateurs_communes_epci) + len(indicateurs_communes_seulement) + len(indicateurs_epci_seulement)} indicateurs*")
    else:
        # Fallback si pas de colonne thématique
        st.info("Aucune thématique définie dans les données. Affichage de tous les indicateurs:")
        
        # Indicateurs des communes
        st.markdown("**Indicateurs communaux:**")
        for ind in sorted(df['indicateur'].unique()):
            st.write(f"• {ind}")
        
        # Indicateurs des EPCI
        st.markdown("**Indicateurs EPCI:**")
        for ind in sorted(epci_df['indicateur'].unique()):
            st.write(f"• {ind}")
    
    # Optionnel: Ajouter un tableau récapitulatif
    st.subheader("📈 Récapitulatif par thématique")
    
    # Créer un DataFrame récapitulatif
    recap_data = []
    for thematique in all_thematiques:
        # Compter les indicateurs par source
        nb_communes = 0
        nb_epci = 0
        nb_communes_epci = 0
        
        if 'thematique' in df.columns:
            mask_communes = df['thematique'] == thematique
            indicateurs_communes = df[mask_communes]['indicateur'].unique()
            nb_communes = len(indicateurs_communes)
        
        if 'thematique' in epci_df.columns:
            mask_epci = epci_df['thematique'] == thematique
            indicateurs_epci = epci_df[mask_epci]['indicateur'].unique()
            nb_epci = len(indicateurs_epci)
        
        # Identifier les communs
        if nb_communes > 0 and nb_epci > 0:
            indicateurs_communes_set = set(indicateurs_communes)
            indicateurs_epci_set = set(indicateurs_epci)
            nb_communes_epci = len(indicateurs_communes_set.intersection(indicateurs_epci_set))
            nb_communes -= nb_communes_epci
            nb_epci -= nb_communes_epci
        
        total = nb_communes + nb_epci + nb_communes_epci
        
        recap_data.append({
            "Thématique": thematique,
            "Total indicateurs": total,
            "Commune seule": nb_communes,
            "EPCI seule": nb_epci,
            "Commune + EPCI": nb_communes_epci
        })
    
    if recap_data:
        recap_df = pd.DataFrame(recap_data)
        st.dataframe(recap_df, use_container_width=True)
