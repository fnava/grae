#!/usr/bin/python3
# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt

from sklearn import linear_model, decomposition, datasets
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV

logistic = linear_model.LogisticRegression()


# Recover MILES processed spectra through SHARDs filters:
import pickle
with open('shardsout.pickle', 'rb') as f:
	resp_u = pickle.load(f)     
print("header = ", resp_u[0])
#print(resp_u[1][8:-12])

resp = sorted(resp_u[1:], key=lambda r: r[7])
mag_data = []
par_data = []
for r in resp:
	#print(r[8:-12])
	mag_data.append(r[8:-12])
	#par_data.append([float(r[4]),]) # MH
	if r[5]=='baseFe':
		par_data.append([0.0,])
	else:
		par_data.append([float(r[5]),]) 
# build X matrix with magnitudes
X = np.array(mag_data)
# build Y matrix with parameters
Y = np.array(par_data)

#X_1 = np.array(data)
##X = X_m-np.mean(X_m)
#pca1 = decomposition.PCA()
#pca1.fit(X_1)
#
#X_2 = []
#for r in X_1:
#	X_2.append(r-pca1.mean_)	
#X = np.array(X_2)

print("X.shape=",X.shape)
print("X_max=",np.max(X))
print("X_min=",np.min(X))
print("Y.shape=",Y.shape)
print("Y_max=",np.max(Y))
print("Y_min=",np.min(Y))

def plot_X():
	plt.clf()
	plt.pcolor(X, cmap='jet')
	plt.show()

###############################################################################
# Plot the PCA spectrum
print("### PCA ###")
pca = decomposition.PCA()
pca.fit(X)
print("PCA variances=",pca.explained_variance_)
print("PCA mean=",pca.mean_)

def plot_pca():
	plt.figure(1, figsize=(4, 3))
	plt.clf()
	plt.axes([.2, .2, .7, .7])
	plt.plot(pca.explained_variance_, linewidth=2)
	plt.axis('tight')
	plt.xlabel('n_components')
	plt.ylabel('explained_variance_')
	plt.show()
###############################################################################
# Prediction
print("### PLS ###")
from sklearn.cross_decomposition import PLSRegression, PLSCanonical

def print_y(Y1,Y1_pred):
	Y,Y_pred = (list(t) for t in zip(*sorted(zip(Y1, Y1_pred))))
	plt.figure(1, figsize=(4, 3))
	plt.clf()
	#plt.axes([.2, .2, .7, .7])
	plt.plot(Y, linewidth=2, color='green' )
	plt.plot(Y_pred, linewidth=2, color='red' )
	plt.axis('tight')
	#plt.xlabel('n_components')
	#plt.ylabel('explained_variance_')
	plt.show()

pls2 = PLSRegression(copy=True, max_iter=100, n_components=13, scale=False, tol=1e-06)
pls2.fit(X, Y)
#PLSRegression(copy=True, max_iter=500, n_components=13, scale=True, tol=1e-06)
Y_pred = pls2.predict(X)

print("Y=", Y)
print("Y_pred=", Y_pred)
print_y(Y,Y_pred)

#pls2 = PLSCanonical(copy=True, max_iter=1000, n_components=13, scale=False, tol=1e-06)
#pls2.fit(X, Y)
#Y_pred = pls2.predict(X)
#print("Y=", Y)
#print("Y_pred=", Y_pred)
#print_y(Y,Y_pred)

###############################################################################
# Prediction
print("### SVM ###")

from sklearn import preprocessing
scaler = preprocessing.StandardScaler().fit(X)
# StandardScaler(copy=True, with_mean=True, with_std=True)
#scaler.mean_
#scaler.scale_
X2 = scaler.transform(X)

from sklearn import svm
clf = svm.SVR(C=1.0, cache_size=200, epsilon=0.1, gamma='auto', kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
#SVR(C=1.0, cache_size=200, coef0=0.0, degree=3, epsilon=0.1, gamma='auto', kernel='rbf', max_iter=-1, shrinking=True, tol=0.001, verbose=False)
clf.fit(X2, np.ravel(Y)) 
Y_pred=clf.predict(X2)
print_y(Y,Y_pred)

