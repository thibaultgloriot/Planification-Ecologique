import pandas as pd
import numpy as np

columns=pd.read_csv("data/columns_indicateurs.csv",sep=";")

df_communes=pd.read_csv("data/final_df_communes.csv")

df_epci=pd.read_csv("data/final_df_epci.csv")


indicateurs_columns=columns["Indicateur"].unique()
liste_indicateurs_columns=indicateurs_columns.tolist()
indicateurs_communes=df_communes["indicateur"].unique()
liste_indicateurs_communes=indicateurs_communes.tolist()

indicateurs_epci=df_epci["indicateur"].unique()
liste_indicateurs_epci=indicateurs_epci.tolist()

indicateurs_non_dans_columns = np.setdiff1d(
    np.union1d(indicateurs_communes, indicateurs_epci),
    indicateurs_columns)

liste_indicateurs_non_dans_columns=indicateurs_non_dans_columns.tolist()
print("Indicateurs qui ne sont PAS dans columns:")
print(indicateurs_non_dans_columns)
print(f"Nombre: {len(indicateurs_non_dans_columns)}")

# 2. Indicateurs communs entre les trois (intersection)
indicateurs_communs_tous = np.intersect1d(
    indicateurs_columns,
    np.intersect1d(indicateurs_communes, indicateurs_epci)
)

# 3. Union unique des indicateurs de communes et epci
union_communes_epci = np.union1d(indicateurs_communes, indicateurs_epci)
union_communes_epci=np.sort(union_communes_epci).tolist()
print("\nUnion unique des indicateurs communes et EPCI:")
print(union_communes_epci)
print(f"Nombre: {len(union_communes_epci)}")

# 4. Si vous voulez aussi voir quels indicateurs sont exclusifs à chaque source
indicateurs_uniques_communes = np.setdiff1d(indicateurs_communes, indicateurs_epci)
indicateurs_uniques_epci = np.setdiff1d(indicateurs_epci, indicateurs_communes)