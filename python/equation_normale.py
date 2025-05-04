# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 18:18:33 2025

@author: pc-portable.net
"""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_regression

# ====================== I. Dataset ============================
np.random.seed(0)
x, y = make_regression(n_samples=100, n_features=1, noise=10)
y = y.reshape(-1, 1)  # mise en forme

# ====================== II. Préparation des données ============
# Ajouter colonne de biais à X
X = np.hstack((x, np.ones_like(x)))

# ====================== III. Équation Normale ==================
# θ = (XᵀX)^(-1)Xᵀy
theta = np.linalg.inv(X.T @ X) @ X.T @ y
print("Paramètres optimaux (theta) :")
print(theta)

# ====================== IV. Prédictions ========================
predictions = X @ theta
# ====================== V. Visualisation =======================
plt.figure(figsize=(10, 6))
plt.scatter(x, y, label="Données réelles")
plt.plot(x, predictions, color='r', label="Régression (Équation normale)")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Régression linéaire (Équation normale)")
plt.legend()
plt.grid()
plt.show()


# ====================== VI. Évaluation du modèle ===============
def coef_determination(y, pred):
    u = ((y - pred)**2).sum()
    v = ((y - y.mean())**2).sum()
    return 1 - u / v

print(f"Coefficient de détermination (R²) : {coef_determination(y, predictions):.4f}")
