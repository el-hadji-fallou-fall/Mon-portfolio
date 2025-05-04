# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 09:57:24 2025

@author: pc-portable.net
"""
#======================================================================
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Charger le dataset Iris
iris = pd.read_csv("C:/Users/pc-portable.net/Documents/Travaux_pratiques/iris.csv")
print(iris.head())

# 2. Exploration : La vue ensemble : pairplot
sns.pairplot(iris, hue='variety')
plt.show()

# 3. Charger le dataset Iris
titanic = sns.load_dataset('titanic')
titanic.drop(['alone', 'alive', 'who', 'adult_male', 'embark_town', 'class'], axis=1, inplace=True)
titanic.dropna(axis=0, inplace=True)
print(titanic.head())
# 4. Catplot
sns.catplot(x='survived', y='age', data=titanic, hue='sex')
plt.show()
# 5. boxplot
sns.boxplot(x='age', y='fare', data=titanic, hue='sex')
plt.show()

# 6. distribution
sns.distplot(titanic['fare'])
plt.show()
#======================================================================




























