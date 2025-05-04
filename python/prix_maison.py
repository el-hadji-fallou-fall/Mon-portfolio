# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 19:47:17 2025
@author: pc-portable.net
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

#=========================== I. Dataset ===========================

np.random.seed(1)
surface = 2.5 * np.random.rand(50, 1) * 100  # entre 0 et 250 m²
prix = 500 + 30 * surface + np.random.randn(50, 1) * 1000  # prix avec du bruit

# Affichage des données
plt.scatter(surface, prix)
plt.xlabel("Surface (m²)")
plt.ylabel("Prix (€)")
plt.title("Prix de la maison en fonction de laSurface")
plt.grid()
plt.show()

print(surface.shape)
print(prix.shape)

# Affichage de la formule
img = Image.open("C:/Users/pc-portable.net/Documents/Travaux_pratiques/RL.png")
plt.imshow(img)
plt.axis("off")
plt.show()


#====================== II. Préparation des données =======================

# Normalisation

surface_mean = np.mean(surface)
surface_std = np.std(surface)
surface_norm = (surface - surface_mean) / surface_std

# Création de la matrice par Ajout d'une colonne de biais

X = np.hstack((surface_norm, np.ones(surface.shape)))
print(X)
print(X.shape)

# création d'un vecteur parametre theta

np.random.seed(0)
theta = np.random.randn(2, 1)
print(theta)
print(theta.shape)

#====================== III. Modèle Linéaire =======================

def model(X, theta):
    return X.dot(theta)


#================== IV. Fonction coût: Erreur Quadrulature Moyenne =======================

def cost_function(X, y, theta):
    m = len(y)
    return 1 / (2 * m) * np.sum((model(X, theta) - y)**2)

#====================== V. Gradient et descente de gradient =======================

def grad(X, y, theta):
    m = len(y)
    return 1 / m * X.T.dot(model(X, theta) - y)

def gradient_descent(X, y, theta, learning_rate, n_iterations):
    cost_history = np.zeros(n_iterations)
    for i in range(n_iterations):
        theta =  theta - learning_rate * grad(X, y, theta)
        cost_history[i] = cost_function(X, y, theta)
    return theta, cost_history

#====================== VI. Phase d'Entraînement =======================

n_iterations = 1000
learning_rate = 0.01

theta_final, cost_history = gradient_descent(X, prix, theta, learning_rate, n_iterations)
print(theta_final)

# Prédictions
predictions = model(X, theta_final)

#====================== VII. Visualisation =======================

# Données + prédictions
plt.figure(figsize=(10, 6))
plt.scatter(surface, prix, label="Données réelles")
plt.plot(surface, predictions, color='r', label="Prédictions")
plt.title("Phase d'entraînement")
plt.xlabel("Surface (m²)")
plt.ylabel("Prix (€)")
plt.legend()
plt.grid()
plt.show()

# =================== VI. Courbes d'apprentissage ======================

plt.figure(figsize=(8, 4))
plt.plot(cost_history)
plt.title("Courbes d'apprentissage")
plt.xlabel("Nombre d'Itérations")
plt.ylabel("Fonction Coût")
plt.grid()
plt.show()

# ================== VIII. Evaluation finale ========================

def coef_determination(prix, predictions):
    u = ((prix - predictions)**2).sum()
    v = ((prix - prix.mean())**2).sum()
    return 1 - u/v
print(f"Coefficient de détermination (R²) : {coef_determination(prix, predictions):.4f}")