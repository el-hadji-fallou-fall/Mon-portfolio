# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 23:11:48 2025

@author: pc-portable.net
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#========================================================================

bitcoin = pd.read_csv("C:/Users/pc-portable.net/Documents/Travaux_pratiques/BTC-EUR.csv", index_col = 'Date', parse_dates = True)
print(bitcoin)

# Afficher les 5 premières lignes
print(bitcoin.head())

bitcoin['Close'].plot(figsize=(9, 6))
plt.show()

print(bitcoin.index)

# Filtrer l'année 2019 et tracer la colonne 'Close'
bitcoin.loc['2019', 'Close'].plot()

plt.title("Cours du Bitcoin entre 2017 et 2020")
plt.ylabel("Prix de clôture")
plt.xlabel("Date")
plt.grid()
plt.show()

# Définir la série temporelle 'Close' entre 2017 et 2020
close = bitcoin.loc['2019', 'Close']

# Resample et plot
close.resample('2W').std().plot()

# Affichage du graphe
plt.title("Prix moyen mensuel du Bitcoin (2017-2020)")
plt.xlabel("Date")
plt.ylabel("Prix de clôture (USD)")
plt.grid()
plt.show()


plt.figure()

# Ligne journalière brute
bitcoin.loc['2019', 'Close'].plot(label='valeur journalière')

# Moyenne mensuelle
bitcoin.loc['2019', 'Close'].resample('M').mean().plot(label='moyenne par mois')

# Moyenne hebdomadaire
bitcoin.loc['2019', 'Close'].resample('W').mean().plot(label='moyenne par semaine')

plt.title("Évolution du Bitcoin en 2019")
plt.xlabel("Date")
plt.ylabel("Prix de clôture (USD)")
plt.legend()
plt.grid()
plt.show()

# Aggregate

print(bitcoin.loc['2019', 'Close'].resample('W').agg(['mean', 'var', 'std', 'max', 'min']))

m = bitcoin['Close'].resample('W').agg(['mean', 'std', 'min', 'max'])

plt.figure(figsize=(12, 8))
m['mean']['2019'].plot(label='moyenne par semaine')
plt.fill_between(m.index, m['max'], m['min'], alpha=0.2, label='min-max par semaine')

plt.legend()
plt.show()

# Moving Rolling

plt.figure(figsize=(12, 8))

# Série brute
bitcoin.loc['2019-09', 'Close'].plot(label='cours quotidien')

# Moyenne mobile non centrée
bitcoin.loc['2019-09', 'Close'].rolling(window=7).mean().plot(label='rolling 7j (non centré)', lw=3, ls=':', alpha=0.8)

# Moyenne mobile centrée
bitcoin.loc['2019-09', 'Close'].rolling(window=7, center=True).mean().plot(label='rolling 7j (centré)', lw=3, ls=':', alpha=0.8)

# Moyenne mobile exponentielle
bitcoin.loc['2019-09', 'Close'].ewm(alpha=0.6).mean().plot(label='ewm (α=0.6)', lw=3, ls=':', alpha=0.8)

# Mise en forme
plt.title("Bitcoin – Septembre 2019 : Lissage des prix de clôture")
plt.xlabel("Date")
plt.ylabel("Prix de clôture (USD)")
plt.grid(True)
plt.legend()
plt.show()

plt.figure(figsize=(12, 8))
bitcoin.loc['2019-09', 'Close'].plot()
for i in np.arange(0.2, 1, 0.2):
    bitcoin.loc['2019-09', 'Close'].ewm(alpha=i).mean().plot(label=f'ewm {i}', ls='--', alpha=0.8)
plt.legend()
plt.show()

#====================================================================
ethereum = pd.read_csv("C:/Users/pc-portable.net/Documents/Travaux_pratiques/ETH-EUR.csv", index_col = 'Date', parse_dates = True)
print(ethereum)

# Afficher les 5 premières lignes
print(ethereum.head())

btc_eth = pd.merge(bitcoin, ethereum, on='Date', how='inner', suffixes=('_btc', '_eth'))
print(btc_eth)

btc_eth[['Close_btc', 'Close_eth']].plot(figsize = (12, 8))
plt.show()

btc_eth[['Close_btc', 'Close_eth']].plot(subplots=True, figsize=(12, 8))
plt.show()

print(btc_eth[['Close_btc', 'Close_eth']].corr())

#====================================================================
# Exercice Trading Strategies
#====================================================================

data = bitcoin.copy()
data['Buy'] = np.zeros(len(data))
data['Sell'] = np.zeros(len(data))
     

data['RollingMax'] = data['Close'].shift(1).rolling(window=28).max()
data['RollingMin'] = data['Close'].shift(1).rolling(window=28).min()
data.loc[data['RollingMax'] < data['Close'], 'Buy'] = 1
data.loc[data['RollingMin'] > data['Close'], 'Sell'] = -1
     

start ='2019'
end='2019'
fig, ax = plt.subplots(2, figsize=(12, 8), sharex=True)
#plt.figure(figsize=(12, 8))
#plt.subplot(211)
ax[0].plot(data['Close'][start:end])
ax[0].plot(data['RollingMin'][start:end])
ax[0].plot(data['RollingMax'][start:end])
ax[0].legend(['close', 'min', 'max'])
ax[1].plot(data['Buy'][start:end], c='g')
ax[1].plot(data['Sell'][start:end], c='r')
ax[1].legend(['buy', 'sell'])
plt.show()
     

