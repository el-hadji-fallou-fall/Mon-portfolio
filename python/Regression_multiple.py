# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 22:10:15 2025

@author: pc-portable.net
"""

import numpy as np
from sklearn.datasets import make_regression
import matplotlib.pyplot as plt
from PIL import Image

#=======================================================================
#================ Regrssion Plynomiale ===================================
#=======================================================================


# ======================== I. Dataset ========================
np.random.seed(0)
X, y = make_regression(n_samples=100, n_features=3, noise=15)
y = y.reshape(-1, 1)

print("Shape de X :", X.shape)  # (100, 3)
print("Shape de y :", y.shape)  # (100, 1)

# ======================== II. Préparation ========================

# Ajout du biais (colonne de 1)
X_biais = np.hstack((X, np.ones((X.shape[0], 1))))

# Initialisation de theta
theta = np.random.randn(X_biais.shape[1], 1)

# ======================== III. Modèle ========================

def model(X, theta):
    return X.dot(theta)

# ======================== IV. Fonction Coût ========================

def cost_function(X, y, theta):
    m = len(y)
    return (1 / (2 * m)) * np.sum((model(X, theta) - y) ** 2)

# ======================== V. Gradient & Descente ========================

def grad(X, y, theta):
    m = len(y)
    return (1 / m) * X.T.dot(model(X, theta) - y)

def gradient_descent(X, y, theta, learning_rate, n_iterations):
    cost_history = np.zeros(n_iterations)
    for i in range(n_iterations):
        theta -= learning_rate * grad(X, y, theta)
        cost_history[i] = cost_function(X, y, theta)
    return theta, cost_history

# ======================== VI. Entraînement ========================

n_iterations = 1000
learning_rate = 0.01

theta_final, cost_history = gradient_descent(X_biais, y, theta, learning_rate, n_iterations)
print("Theta final :\n", theta_final)

# ======================== VII. Prédictions & Évaluation ========================

predictions = model(X_biais, theta_final)

# ======================= VII. Visualisation =======================

plt.figure(figsize=(8, 6))
plt.scatter(y, predictions, c='blue', label='Prédictions vs Réel')
plt.plot([y.min(), y.max()], [y.min(), y.max()], color='red', linestyle='--', label='Parfait')
plt.xlabel("Valeurs réelles")
plt.ylabel("Valeurs prédites")
plt.title("Comparaison Prédictions vs Réel")
plt.legend()
plt.grid()
plt.show()


# Courbe coût
plt.plot(cost_history)
plt.title("Courbe d'apprentissage (fonction coût)")
plt.xlabel("Itérations")
plt.ylabel("Coût")
plt.grid()
plt.show()

# R² score
def coef_determination(y, y_pred):
    u = ((y - y_pred) ** 2).sum()
    v = ((y - y.mean()) ** 2).sum()
    return 1 - u / v

print(f"Coefficient de détermination (R²) : {coef_determination(y, predictions):.4f}")
