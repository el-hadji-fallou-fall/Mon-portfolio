# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 20:44:40 2025

@author: pc-portable.net
"""


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#========================================================================
data = pd.read_excel("C:/Users/pc-portable.net/Documents/Travaux_pratiques/titanic.xls")
print(data)

# Afficher les 5 premières lignes
print(data.head())

# Afficher les noms de colonnes
print(data.columns)

# Supprimer certaines colonnes
data = data.drop(['name', 'sibsp', 'parch', 'ticket', 'fare', 'cabin', 'embarked', 'boat', 'body', 'home.dest'], axis=1)
print(data)

# Statistiques de base
print(data.describe())

# Remplacer les valeurs manquantes
print(data.fillna(data['age'].mean()))

# Statistiques de base
print(data.describe())

# Eliminer les valeurs manquantes
data = data.dropna(axis=0)

# Statistiques de base
print(data.describe())

# Accéder à une colonne et faire le décompte ensuite tracer le graphique
print(data["pclass"].value_counts().plot.bar())
plt.show()

# Filtrer les lignes
print(data[data["age"] > 30])

# Grouper et compter
print(data.groupby(["sex"]).count())

# Sauvegarder dans un nouveau fichier Titanic_traité
data.to_excel("Titanic_traité.xlsx", index=False)

# DataFrame et series 
print(data[data['age'] < 18]['pclass'].value_counts())

#=======================================================================

# ============ Exercice: Feature Engineering ===========================
#Créer des catégories d'ages avec pandas
#======================================================================

def category_ages(age):
    if age <= 20:
        return 'Cas 0: <20 ans'
    elif (age > 20) & (age <= 30):
        return 'Cas 1: 20-30 ans'
    elif (age > 30) & (age <= 40):
        return 'Cas 2: 30-40 ans'
    else:
        return 'Cas 3:+40 ans'

print(data['age'].map(category_ages))

data.loc[data['age'] <= 20, 'age'] = 0
data.loc[(data['age'] > 20) & (data['age'] <= 30) , 'age'] = 1
data.loc[(data['age'] > 30) & (data['age'] <= 40) , 'age'] = 2
data.loc[data['age'] > 40, 'age'] = 3
print(data.head())
print(data['age'].value_counts())
print(data['sex'].astype('category').cat.codes)











