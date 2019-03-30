# Final Project in Python
# May involve the orbitals diagram and/or molecular dynamics
import numpy as np
import random as rd
import pylab as py
import matplotlib.pyplot as plt
from matplotlib import animation
from sympy import var, factorial, sqrt, exp, S, assoc_laguerre, Float
from sympy.physics.hydrogen import R_nl
import scipy.integrate as integrate
import scipy.special as spe
import seaborn as sns

a_0 = 5.2917721067e-11 # Bohr Radius
Z = 2  # Atomic number
N = 1000 # Number of samples

# Explain the mehchanics of the code R_nl from "Sympy" library at
#https://docs.sympy.org/1.0/_modules/sympy/physics/hydrogen.html
# The radial density function is R_nl
"""
# The electron-in-helium wavefunction
def R_nl(n, l, r, Z=1):
    n_r = n - l - 1
    # rescaled "r"
    a = 1/Z  # Bohr radius
    r0 = 2 * r / (n * a)
    # normalization coefficient
    C = sqrt((S(2)/(n*a))**3 * factorial(n_r) / (2*n*factorial(n + l)))
    # This is an equivalent normalization coefficient, that can be found in
    # some books. Both coefficients seem to be the same fast:
    # C =  S(2)/n**2 * sqrt(1/a**3 * factorial(n_r) / (factorial(n+l)))
    return C * r0**l * assoc_laguerre(n_r, 2*l + 1, r0).expand() * exp(-r0/2)
"""

def HFunc(r,theta,phi,n,l,m):
    #Full wavefunction (radial and spherical harmonics functions)
    # between an electron and nucleus of atomic number Z. The function was
    #taken from http://www.pitt.edu/~djb145/python/utilities/2016/03/07/Plot-Density/
    sphHarm = spe.sph_harm(m,l,phi,theta) # Note the different convention from doc
    return R_nl(n, l, r, Z)*sphHarm

#starting Monte Carlo method...
# Gaussian distribution of random sampling
def gaussian():
    r = rd.uniform(0,2)
    theta = np.pi*rd.uniform(-1,1) #
    x = r*np.cos(theta) 
    y = r*np.sin(theta)
    return x,y, theta
    # We return the x and y coordinates with the angle of orientation

# Wavefunction density
Psi = []
Psi_1 = []
Psi_2 = []

# Density coordinates:
X1 = []
Y1 = []
X2 = []
Y2 = []
Random = []

# Mapping 2 different electrons
for i in range(N):
    x1,y1, theta1 = gaussian()
    x2, y2, theta2 = gaussian()
    r1 = np.sqrt((x1)**2+(y1)**2)
    r2 = np.sqrt((x2)**2+(y2)**2)
    phi = np.pi/2
    # Gathering the coordinates data for each point
    X1.append(x1)
    Y1.append(y1)
    X2.append(x2)
    Y2.append(y2)
    # Quantum numbers of 2 excited states:
    #Note that 2p and 3p orbitals have linear combinations of 3 wavefunctions'
    #components at m = -1, 0, 1

    #define 2p orbital
    n = 2
    l = 1

    #define 3p orbital
    n1 = 3
    l1 = 1
    
    # Probabilistic values:
    #here, function_1 and 2 are linear combinations of wavefunctions in 2p, 3p, respectively
    function_1 = 1/np.sqrt(3)*(HFunc(r1,theta1,phi,n,l,m=-1)+HFunc(r1,theta1,phi,n,l,m=0)+HFunc(r1,theta1,phi,n,l,m=1))
    function_2 = 1/sqrt(3)*(HFunc(r2,theta2,phi,n1,l1,m=-1)+HFunc(r2,theta2,phi,n1,l1,m=0)+HFunc(r2,theta2,phi,n1,l1,m=1))
    function= function_1*function_2 #probability distribution
    Psi.append(abs(function)**2)
    Psi_1.append(abs(function_1)**2)
    Psi_2.append(abs(function_2)**2)



# Electron 2d position density based on the probability
e_1x = []
e_1y = []
e_2x = []
e_2y = []

# Mapping regions with high density
avg_value = sum(Psi)/len(Psi)
avg_value_1 = sum(Psi_1)/len(Psi_1)
avg_value_2 = sum(Psi_2)/len(Psi_2)

#while sampling, retain electron positions that appear more than occasionally
for i in range(N):
    if Psi[i]>=avg_value:
        if Psi_1[i]>=avg_value_1:
            e_1x.append(X1[i])
            e_1y.append(Y1[i])
        if Psi_2[i]>=avg_value_2:
            e_2x.append(X2[i]+3)
            e_2y.append(Y2[i])

# now setup stuff for animation....
myfig = plt.figure(figsize=(8,7))
ax = plt.axes()
ax.set_xlim([-2,5])
ax.set_ylim([-2.5,3])
line, = ax.plot([],[],lw=2)
scat1 = ax.scatter(e_1x,e_1y, label = "He_1")
scat2 = ax.scatter(e_2x,e_2y, label = "He_2")

#Recording positions for 2 electrons in Helium's orbitals 2p, 3p
position_template1, position_template2 ='position of 1st He = % .3f, %.3f', 'position of 2nd He = % .3f, %.3f'
position_text1,position_text2 = ax.text(0.1, 0.95, '', transform=ax.transAxes), ax.text(0.1, 0.90, '', transform=ax.transAxes)

def animate1_2(i):
    #Animate 2 frames of 2 electrons
    xoffs = e_1x[i]
    yoffs = e_1y[i]
    scat1.set_offsets(np.c_[xoffs,yoffs])
    position_text1.set_text(position_template1 % (xoffs, yoffs))
    
    xoffs = e_2x[i]
    yoffs = e_2y[i]
    scat2.set_offsets(np.c_[xoffs,yoffs])
    position_text2.set_text(position_template2 % (xoffs, yoffs))
    return scat1, scat2, position_text1, position_text2

M = min(len(e_1x), len(e_2x))
#Plotting with Seaborn for density plots; animations with Matplotlib
anim = animation.FuncAnimation(myfig, animate1_2, interval= 100, frames = len(e_1x))
sns.kdeplot(e_1x, e_1y, ax=ax, cmap = "Blues", shade=True,alpha=0.5, shade_lowest=False, bw = .3)
sns.kdeplot(e_2x, e_2y, ax=ax, cmap = "Reds", shade=True, alpha=0.5,shade_lowest=False , bw = .3)

ax.legend()
plt.title("Simulations of Helium electrons in two excited states, 2p and 3p")
plt.show()



