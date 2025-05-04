# -*- coding: utf-8 -*-
"""
=========================================================
               Fallou fall
==========================================================

          PYTHON AVEC MACHINE LEARNING

===========================================================
"""

import math
import statistics
import os
import glob
import random




#=================================
# exo1 sur les dictionnaires
#=================================

classeur ={
    
    "positif": [],
    "negatif": [],
    
    
    }

def trier(classeur, nombre):
    if nombre >= 0:
        classeur['positif'].append(nombre)
    else:
        classeur['negatif'].append(nombre)
    return classeur

#=============================================
#exo2 sur les dictionnaires comprehensions
#=============================================

clets = [i for i in range(21) ]
valeurs = [j**2 for j in range(21)]

dictio= {k:v for k, v in zip(clets, valeurs)}

print(dictio)

#=====================================================
#MATH
#=====================================================

print(math.cos(math.pi))
print(math.exp(2))

#=====================================================
#Statistics
#=====================================================

print(statistics.mean([1, 2, 3, 4,5]))
print(statistics.variance([1, 2, 3, 4,5]))


#=====================================================
#Random
#=====================================================

random.seed(3)

print(random.choice([1, 2, 3, 4,5]))

print(random.random()) # float

print(random.randint(1, 6)) # integer

print(random.sample(range(20), 10)) # liste de 10 elements aleatoires


#======================================================================
#EXERCICES
#===========================================================================

filename = glob.glob('*.txt')
d = {}
for file in filename:
    with open(file, 'r') as f:
        d[file] = f.read().splitlines()
print(d)


#================================================
# NUMPY Machine Learning
#================================================

import numpy as np

tab1 = np.zeros((3,4)) # tabeau dim2 de 3 ligne , 4 coulonne
print(tab1)

tab2 = np.random.randn(4, 3) # tabeau dim2 de 4 ligne , 3 coulonnes
print(tab2)

tab3 = np.eye(4) # tabeau dim2 de 4 ligne , 4 coulonnes
print(tab3)

tab4 = np.linspace(0, 10, 20, dtype = np.float64) # tabeau dim1 avec 20 éléments répartis entre 0 et 10
print(tab4)

tab5 = np.arange(0, 10, 1) # tabeau dim1 avec 1 pas répartis entre 0 et 10
print(tab5)

#=====================================
#HSTACK &  VSTACK & CONCATENATE 
#=====================================

A= np.zeros((3, 4))
B= np.ones((3, 4))
C= np.hstack((A, B))
D=np.vstack((A, B))
E=np.concatenate((A, B), axis =1)
print(C)
print(D)
print(E)

#=======================================
#Rechape & SQUEEZE & RAVEL
#=======================================
M=np.array([1, 2, 3])
M=M.reshape((M.shape[0], 1))
print(M.shape)
M=M.squeeze()
print(M.shape)
print(M.ravel())

#==============================================
# EXERCICE D'APPLICATION
#===============================================
import numpy as np

def initialisation(m, n):
    
    matrice1 = np.random.randn(m, n)
    matrice2= np.ones((matrice1.shape[0], 1))
    matrice= np.concatenate((matrice1, matrice2), axis =1)
    
    return matrice

#===========================================================
# Matlottlib Plot
#===========================================================

import matplotlib.pyplot as plt
import numpy as np

x= np.linspace(0, 2, 10)
y= x**2
plt.plot(x, y) #  
plt.show()













