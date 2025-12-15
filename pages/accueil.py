import streamlit as st
import pandas as pd

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
    
    # Créer un dictionnaire pour regrouper les indicateurs par thématique
    indicateurs_par_thematique = {}
    
    # Ajouter les indicateurs des communes
    if 'thematique' in df.columns:
        # Nettoyer les données : supprimer les lignes où thématique ou indicateur est NaN
        df_clean = df.dropna(subset=['thematique', 'indicateur'])
        
        for thematique in sorted(df_clean['thematique'].unique()):
            if thematique not in indicateurs_par_thematique:
                indicateurs_par_thematique[thematique] = {'communes': set(), 'epci': set()}
            
            indicateurs = df_clean[df_clean['thematique'] == thematique]['indicateur'].unique()
            indicateurs_par_thematique[thematique]['communes'].update(indicateurs)
    
    # Ajouter les indicateurs des EPCI
    if 'thematique' in epci_df.columns:
        # Nettoyer les données : supprimer les lignes où thématique ou indicateur est NaN
        epci_df_clean = epci_df.dropna(subset=['thematique', 'indicateur'])
        
        for thematique in sorted(epci_df_clean['thematique'].unique()):
            if thematique not in indicateurs_par_thematique:
                indicateurs_par_thematique[thematique] = {'communes': set(), 'epci': set()}
            
            indicateurs = epci_df_clean[epci_df_clean['thematique'] == thematique]['indicateur'].unique()
            indicateurs_par_thematique[thematique]['epci'].update(indicateurs)
    
    # Afficher les indicateurs par thématique
    if indicateurs_par_thematique:
        for thematique in sorted(indicateurs_par_thematique.keys()):
            with st.expander(f"{thematique}"):
                # Récupérer tous les indicateurs uniques pour cette thématique (des deux sources)
                tous_indicateurs = sorted(
                    indicateurs_par_thematique[thematique]['communes'].union(
                        indicateurs_par_thematique[thematique]['epci']
                    )
                )
                
                for ind in tous_indicateurs:
                    # Vérifier dans quelle(s) source(s) l'indicateur est présent
                    sources = []
                    if ind in indicateurs_par_thematique[thematique]['communes']:
                        sources.append("communes")
                    if ind in indicateurs_par_thematique[thematique]['epci']:
                        sources.append("EPCI")
                    
                    # Afficher l'indicateur avec sa/ ses source(s)
                    if len(sources) == 2:
                        st.write(f"• {ind} (disponible aux deux échelles)")
                    elif sources[0] == "communes":
                        st.write(f"• {ind} (échelle communale uniquement)")
                    else:
                        st.write(f"• {ind} (échelle EPCI uniquement)")
    else:
        # Fallback si pas de colonne thématique
        st.info("Aucune thématique définie dans les données.")
        
        # Indicateurs des communes
        st.markdown("**Indicateurs communaux:**")
        for ind in sorted(df['indicateur'].unique()):
            st.write(f"• {ind}")
        
        # Indicateurs des EPCI
        st.markdown("**Indicateurs EPCI:**")
        for ind in sorted(epci_df['indicateur'].unique()):
            st.write(f"• {ind}")
