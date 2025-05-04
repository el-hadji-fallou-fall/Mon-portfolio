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
#================ Regrssion Linéaire ===================================
#=======================================================================

# ++++++++++++++ I. Dataset ++++++++++++++++++++++++++++++

#Génération de données aléatoires avec une tendance linéaire avec make_regression: 
#on a un dataset 
# qui contient 100 exemples, et une seule variable 
#Note: chaque fois que la cellule est executée, des données différentes sont générer. 
#Utiliser np.random.seed(0) pour reproduire le meme Dataset a chaque fois.

np.random.seed(0)             # pour toujours reproduire le meme dataset
x, y = make_regression(n_samples=100, n_features=1, noise=10)
plt.scatter(x, y)             # afficher les résultats. X en abscisse et y en ordonnée
plt.show()

print(x.shape)
print(y.shape)

# redimensionner y
y = y.reshape(y.shape[0], 1)

print(y.shape)

# 1. Création de la matrice X 

#qui contient la colonne de Biais. 
#Pour ça, on colle l'un contre l'autre le vecteur x
#et un vecteur 1 (avec np.ones) de dimension égale a celle de x

X = np.hstack((x, np.ones(x.shape)))
print(X)
print(X.shape)

# 2. Finalement, création d'un vecteur parametre, 

# initialisé avec des coefficients aléatoires. 
# Ce vecteur est de dimension (2, 1). 
# Si on désire toujours reproduire le meme vecteur, 
# on utilise comme avant np.random.seed(0).

np.random.seed(0) # pour produire toujours le meme vecteur theta aléatoire
theta = np.random.randn(2, 1)
print(theta)

# +++++++++++++++++ II. Modele Linéaire ++++++++++++++++++

#On implémente un modele , 
#puis on teste le modele pour voir s'il n'y a pas de bug (bonne pratique oblige).
# En plus, cela permet de voir a quoi ressemble le modele initial, défini par la valeur de 

def model(X, theta):
    return X.dot(theta)
plt.scatter(x, y)
plt.plot(x, model(X, theta), c='r')
plt.show()

#++++++++++++++++++++ III. Fonction Cout ++++++++++++++++++++++++

#Erreur Quadratique moyenne
#On mesure les erreurs du modele sur le Dataset X, 
#y en implémenterl'erreur quadratique moyenne, Mean Squared Error (MSE) en anglais.
# J(theta) =1/2m *somme(X*theta - y)²
#Ensuite, on teste notre fonction, pour voir s'il n'y a pas de bug

def cost_function(X, y, theta):
    m = len(y)
    return 1/(2*m) * np.sum((model(X, theta) - y)**2)

#++++++++++++++++++++++ IV. Gradients et Descente de Gradient +++++++++

#On implémente la formule du gradient pour la MSE
#Ensuite on utilise cette fonction dans la descente de gradient:

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

# On définit un nombre d'itérations, ainsi qu'un pas d'apprentissage, et c'est partit !
#Une fois le modele entrainé, on observe les resultats par rapport a notre Dataset

n_iterations = 1000
learning_rate = 0.01

theta_final, cost_history = gradient_descent(X, y, theta, learning_rate, n_iterations)

print(theta_final) # voici les parametres du modele une fois que la machine a été entrainée

# création d'un vecteur prédictions qui contient les prédictions de notre modele final

predictions = model(X, theta_final)

# Affiche les résultats de prédictions (en rouge) par rapport a notre Dataset (en bleu)

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

#Pour vérifier si notre algorithme de Descente de gradient a bien fonctionné, 
#on observe l'évolution de la fonction cout a travers les itérations. 
#On est sensé obtenir une courbe qui diminue a chaque itération jusqu'a stagner a un niveau minimal (proche de zéro).
#Si la courbe ne suit pas ce motif, alors le pas learning_rate est peut-etre trop élevé, 
#il faut prendre un pas plus faible.

plt.plot(range(n_iterations), cost_history)
plt.title("Courbes d'apprentissage")
plt.ylabel("fonction cout")
plt.xlabel("nombre d'itérations")
plt.grid()
plt.show()

# +++++++++++++++++++ VII. Evaluation finale +++++++++++++++++++++++

#Pour évaluer la réelle performance de notre modele avec une métrique populaire 
#(pour votre patron, client, ou vos collegues) on peut utiliser le coefficient de détermination 
#Il nous vient de la méthode des moindres carrés. 
#Plus le résultat est proche de 1, meilleur est votre modele

def coef_determination(y, pred):
    u = ((y - pred)**2).sum()
    v = ((y - y.mean())**2).sum()
    return 1 - u/v
print(f"Coefficient de détermination (R²) : {coef_determination(y, predictions):.4f}")