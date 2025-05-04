# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 21:35:23 2025

@author: pc-portable.net
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 18:18:33 2025

@author: pc-portable.net
"""

import numpy as np
from sklearn.datasets import make_regression
import matplotlib.pyplot as plt
from PIL import Image

#=======================================================================
#================ Regrssion Plynomiale ===================================
#=======================================================================

# +++++++++++++++++++ I. Dataset ++++++++++++++++++++++++++++++


np.random.seed(0)             
x, y = make_regression(n_samples=100, n_features=1, noise=10)
y = y + abs(y/2)
plt.scatter(x, y)            
plt.show()

print(x.shape)
print(y.shape)

# redimensionner y
y = y.reshape(y.shape[0], 1)

print(y.shape)

# 1. Création de la matrice X 

X = np.hstack((x, np.ones(x.shape)))
X = np.hstack((x**2, X))
print(X)
print(X[:10])

# 2. Finalement, création d'un vecteur parametre, 

np.random.seed(0) 
theta = np.random.randn(3, 1)
print(theta)

# +++++++++++++++++ II. Modele Linéaire ++++++++++++++++++

def model(X, theta):
    return X.dot(theta)
plt.scatter(x, y)
plt.plot(x, model(X, theta), c='r')
plt.show()

#++++++++++++++++++++ III. Fonction Cout ++++++++++++++++++++++++


def cost_function(X, y, theta):
    m = len(y)
    return 1/(2*m) * np.sum((model(X, theta) - y)**2)

#++++++++++++++++++++++ IV. Gradients et Descente de Gradient +++++++++


img = Image.open("C:/Users/pc-portable.net/Documents/Travaux_pratiques/RL.png")
plt.imshow(img)
plt.show()

def grad(X, y, theta):
    m = len(y)
    return 1/m * X.T.dot(model(X, theta) - y)


def gradient_descent(X, y, theta, learning_rate, n_iterations):
    
    cost_history = np.zeros(n_iterations) # création d'un tableau de stockage pour enregistrer l'évolution du Cout du modele
    
    for i in range(0, n_iterations):
        theta = theta - learning_rate * grad(X, y, theta) # mise a jour du parametre theta (formule du gradient descent)
        cost_history[i] = cost_function(X, y, theta) # on enregistre la valeur du Cout au tour i dans cost_history[i]
        
    return theta, cost_history


# +++++++++++++++++ V. Phase d'entrainement ++++++++++++++++++++++++



n_iterations = 1000
learning_rate = 0.01

theta_final, cost_history = gradient_descent(X, y, theta, learning_rate, n_iterations)

print(theta_final) 

predictions = model(X, theta_final)

# ++++++++++++++++ VISUALISATION +++++++++++++++++++++++++

plt.figure(figsize=(10, 6))  # optionnel pour agrandir

plt.scatter(x, y, label="Données réelles")  # points
plt.plot(x, predictions, color='r', label="Prédictions")  # ligne rouge

plt.title("Phase d'entraînement")
plt.xlabel("Ordonnées")
plt.ylabel("Abscisses")
plt.legend()
plt.grid()
plt.show()


# +++++++++++++++++ VI. Courbes d'apprentissage ++++++++++++++++++++

plt.plot(range(n_iterations), cost_history)
plt.title("Courbes d'apprentissage")
plt.ylabel("fonction cout")
plt.xlabel("nombre d'itérations")
plt.grid()
plt.show()

# +++++++++++++++++++ VII. Evaluation finale +++++++++++++++++++++++

def coef_determination(y, predictions):
    u = ((y - predictions)**2).sum()
    v = ((y - y.mean())**2).sum()
    return 1 - u/v
print(f"Coefficient de détermination (R²) : {coef_determination(y, predictions):.4f}")