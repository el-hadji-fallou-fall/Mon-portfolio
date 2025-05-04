# -*- coding: utf-8 -*-
"""
Created on Fri May  2 18:43:16 2025

@author: pc-portable.net
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# === Étape 1 : Création de données aléatoires ===
data = {
    'label': ['ham', 'spam', 'ham', 'spam', 'ham', 'spam', 'ham', 'spam', 'ham', 'spam'],
    'message': [
        "Hey, tu fais quoi ce soir ?",
        "Gagne un iPhone maintenant ! Clique ici",
        "Tu viens au cours demain ?",
        "Offre spéciale !!! Réponds vite",
        "Rendez-vous à 14h",
        "Ton code promo est: GRATUIT2025",
        "J'ai bien reçu ton message.",
        "Crédit gratuit sans conditions, clique ici",
        "Tu veux manger ensemble ?",
        "Gagne 500€ en 5 minutes !"
    ]
}
df = pd.DataFrame(data)

# === Étape 2 : Prétraitement ===
df['label_num'] = df.label.map({'ham': 0, 'spam': 1})
X = df['message']
y = df['label_num']

# === Étape 3 : Split en train/test ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Étape 4 : Pipeline (vectorisation + modèle) ===
model = Pipeline([
    ('vect', CountVectorizer()),
    ('clf', MultinomialNB())
])

# === Étape 5 : Entraînement ===
model.fit(X_train, y_train)

# === Étape 6 : Évaluation ===
y_pred = model.predict(X_test)

print("Classification Report:\n", classification_report(y_test, y_pred))
print("Accuracy Score:", accuracy_score(y_test, y_pred))

# Matrice de confusion
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Ham', 'Spam'],
            yticklabels=['Ham', 'Spam'])
plt.xlabel('Prédit')
plt.ylabel('Réel')
plt.title('Matrice de Confusion')
plt.show()
