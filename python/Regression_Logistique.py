# -*- coding: utf-8 -*-
"""
Created on Fri May  2 20:10:41 2025

@author: pc-portable.net
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification

# 1. Générer un jeu de données binaire
X, y = make_classification(n_samples=100, n_features=2, n_redundant=0,
                           n_informative=2, n_clusters_per_class=1, random_state=0)

y = y.reshape(-1, 1)  # pour que y soit une matrice colonne

# Ajouter le biais (colonne de 1)
X_b = np.hstack((X, np.ones((X.shape[0], 1))))

# 2. Fonction Sigmoid
def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# 3. Modèle
def model(X, theta):
    return sigmoid(np.dot(X, theta))

# 4. Fonction coût (log loss)
def cost_function(X, y, theta):
    m = len(y)
    predictions = model(X, theta)
    return -1/m * (y.T @ np.log(predictions + 1e-15) + (1 - y).T @ np.log(1 - predictions + 1e-15))

# 5. Gradient de la log-loss
def grad(X, y, theta):
    m = len(y)
    return 1/m * X.T @ (model(X, theta) - y)

# 6. Descente de gradient
def gradient_descent(X, y, theta, learning_rate, n_iterations):
    cost_history = []
    for _ in range(n_iterations):
        theta -= learning_rate * grad(X, y, theta)
        cost_history.append(cost_function(X, y, theta).flatten()[0])
    return theta, cost_history

# Initialiser theta
np.random.seed(0)
theta_init = np.random.randn(X_b.shape[1], 1)

# Apprentissage
theta_final, cost_history = gradient_descent(X_b, y, theta_init, learning_rate=0.1, n_iterations=1000)

# Prédiction
def predict(X, theta):
    return (model(X, theta) >= 0.5).astype(int)

y_pred = predict(X_b, theta_final)

# Taux de précision
accuracy = (y_pred == y).mean()
print(f"Précision du modèle : {accuracy:.2f}")

# Courbe de coût
plt.plot(cost_history)
plt.title("Courbe d'apprentissage")
plt.xlabel("Itérations")
plt.ylabel("Fonction coût (log-loss)")
plt.grid()
plt.show()

# Visualisation des classes
plt.scatter(X[:, 0], X[:, 1], c=y_pred.flatten(), cmap="bwr", alpha=0.7)
plt.title("Classification par régression logistique")
plt.xlabel("X1")
plt.ylabel("X2")
plt.grid()
plt.show()
