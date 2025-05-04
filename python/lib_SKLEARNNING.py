# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 10:57:25 2025

@author: pc-portable.net
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsClassifier

# 1. REGRESSION
np.random.seed(0)
m = 100 # creation de 100 échantillons
X = np.linspace(0, 10, m).reshape(m,1)
y = X + np.random.randn(m, 1)
plt.scatter(X, y)
plt.show()

# 2. REGRESSION LINEAIRE
model = LinearRegression()
model.fit(X, y) # entrainement du modele
print(model.score(X, y)) # évaluation avec le coefficient de corrélation
plt.scatter(X, y)
plt.plot(X, model.predict(X), c='red')
plt.show()

# 3. Classification
titanic = sns.load_dataset('titanic')
titanic = titanic[['survived', 'pclass', 'sex', 'age']]
titanic.dropna(axis=0, inplace=True)
titanic['sex'].replace(['male', 'female'], [0, 1], inplace=True)
print(titanic.head())

model = KNeighborsClassifier() 
 
y = titanic['survived']
X = titanic.drop('survived', axis=1)
print(X)
print(y)

model.fit(X, y) # entrainement du modele
print(model.score(X, y)) # évaluation
print(model.predict(X))

# 4. Prediction de survie
def survie(model, pclass=1, sex=0, age=25):
  x = np.array([pclass, sex, age]).reshape(1, 3)
  print(model.predict(x))
  print(model.predict_proba(x))







