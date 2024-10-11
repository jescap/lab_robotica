# %% [markdown]
# # Practical Session 2: Introduction to Python
# 
# ## Laboratorio de Robótica 
# ### Grado en Ingeniería Electrónica, Mecatrónica y Robótica
# ### Universidad de Sevilla

# %% [markdown]
# ## Objectives
# 
# The objective of this notebook is to propose some exercises to practise with Python and get familiar with data types, loops, functions, classes, and so on.
# 
# After completing the missing code in this notebook, export it as a Python script. You can do that both using Jupyther Notebook or through the Jupyter extension in VS Code. Then name your file `exercises_sol.py` and commit it to your course Github repository, into a folder named `python_exercises`.

# %% [markdown]
# ### Exercise 1
# 
# Define a function called `squares` that, given a list `sec` of numbers, returns a list with the squares of those numbers, in the same order.

# %%
# Examples:

# squares([2, -1.2, 3e2, 1j]) should return [4, 1.44, 90000.0, (-1+0j)]
# squares(i for i in range(10)) should return [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# %%
def squares(seq):
    ind = 0
    list = seq
    while ind < len(seq):
        list[ind] = seq[ind]**2 
        ind+=1
    return list

 
squares([2, -1.2, 3e2, 1j])

# %% [markdown]
# ### Exercise 2
# 
# A positive integer is said to be perfect if it coincides with the sum of all its proper divisors (that is, other than itself). Define a function called `write_perfect` that, given two positive integers `m` $\leq$ `n`, returns a list with all the perfect numbers within the interval `[m, n]`. The function should also print on the screen each perfect number and its divisors. 

# %%
# Examples:

# write_perfect(1, 1000) should write on screen:
# Number 6 is perfect and its divisors are [1, 2, 3]
# Number 28 is perfect and its divisors are [1, 2, 4, 7, 14]
# Number 496 is perfect and its divisors are [1, 2, 4, 8, 16, 31, 62, 124, 248]

# %%
def write_perfect(m,n):
    if(m == 1):
        ind = 2
    else:
        ind = m    
    while ind <= n:
        sum = 0
        prueba = 1
        divisors = []
        while prueba < ind:
            if(ind%prueba == 0):
                sum += prueba
                divisors.append(prueba) 
            prueba += 1
        if(sum == ind):
            print("Number", ind, "is perfect and its divisors are", divisors)
        ind += 1

write_perfect(1,1000)

# %% [markdown]
# ### Exercise 3
# 
# Consider a dictionary whose keys are character strings of length one and the associated values ​​are non-negative integers, such as the following dictionary `d`:

# %%
d = {'a': 5, 'b': 10, 'c': 12, 'd': 11, 'e': 15, 'f': 20, 'g': 15, 'h': 9, 'i': 7, 'j': 2}

# %% [markdown]
# Define a function called `horizontal_histogram` that, given a dictionary of the previous type, writes the associated histogram of horizontal bars on the screen, printing the bars from top to bottom in the order determined by the `sorted` function on the keys, as illustrated in the following example:

# %%
# horizontal_histogram(d)
# a: *****
# b: **********
# c: ************
# d: ***********
# e: ***************
# f: ********************
# g: ***************
# h: *********
# i: *******
# j: **

# %%
def horizontal_histogram(dictionary):
    ind = 0
    letra = 'a'
    while(ind < len(dictionary)):
        print(letra, ": ", "*"*dictionary[letra]) 
        letraAscii = ord(letra) + 1 #función ord: recibe un caracter y devuelve su código ASCII
        letra = chr(letraAscii) #función chr: recibe código ASCII y devuelve el caracter
        ind += 1

d = {'a': 5, 'b': 10, 'c': 12, 'd': 11, 'e': 15, 'f': 20, 'g': 15, 'h': 9, 'i': 7, 'j': 2}
horizontal_histogram(d)

# %% [markdown]
# ### Exercise 4
# 
# Suppose we want to simulate the trajectory of a drone that is launched at a given point with a certain initial height. The drone is launched forward with an initial speed and at a certain angle without propulsion motors on. Initially it will advance upwards, but due to the force of gravity, at a given moment it will begin to descend until it lands. For simplicity, we will assume that there is no friction or wind resistance.
# 
# Define a class `Drone` that represents the state of the drone at a given instant of time. At least, the class should include attributes to store the following data:
# + Traveled distance traveled (horizontally)
# + Height
# + Horizontal speed
# + Vertical speed
# 
# In addition, apart from its constructor, the class should have the following three methods:
# + `get_pos_x`: it returns the horizontal traveled distance 
# + `get_pos_y`: it returns the vertical traveled distance 
# + `update_position`: given a number `t` of seconds, it updates the position and velocity of the projectile after that time has elapsed
# 
# Once the `Drone` class is defined, define an external function called `land` that, given the `height` (meters), `velocity` (meters per second), `angle` (degrees) and time `step` (seconds), prints on the screen the different positions of a drone launched with that initial `height`, `velocity` and `angle`. The position of the drone should be displayed at each `step` of time, until it lands. The function should also print the maximum height reached by the drone, the total distance traveled horizontally and the time and number of steps that it took it to land.
# 
# Indications:
# 1. If the drone has an initial velocity $v$ and is launched at an angle $\theta$, the horizontal and vertical components of the initial velocity are $v \times \cos(\theta)$ and $v \times \ sin(\theta)$, respectively.
# 2. The horizontal component of velocity, in the absence of friction and wind, will remain constant.
# 3. The vertical component of the velocity evolves throughout time: if $vy_0$ is the initial vertical velocity, after a time step $t$, the velocity will be $vy_1 = vy_0 - 9.8 \times t$, due to the Earth's gravity.
# 4. Also, if $h_0$ is the initial drone height, after a time step $t$, the height will be $h_1 = h_0 + vm \times t$, where $vm$ is the average between the previous $vy_0$ and $vy_1$.

# %%
# Example:

# land(30, 1, 20, 0.1)
# Drone at position(0.0, 30.0)
# Drone at position(0.1, 30.0)
# Drone at position(0.2, 29.9)
# Drone at position(0.3, 29.7)
# Drone at position(0.4, 29.4)
# Drone at position(0.5, 28.9)
# Drone at position(0.6, 28.4)
# Drone at position(0.7, 27.8)
# Drone at position(0.8, 27.1)
# Drone at position(0.8, 26.3)
# Drone at position(0.9, 25.4)
# Drone at position(1.0, 24.4)
# Drone at position(1.1, 23.4)
# Drone at position(1.2, 22.2)
# Drone at position(1.3, 20.9)
# Drone at position(1.4, 19.5)
# Drone at position(1.5, 18.0)
# Drone at position(1.6, 16.4)
# Drone at position(1.7, 14.7)
# Drone at position(1.8, 13.0)
# Drone at position(1.9, 11.1)
# Drone at position(2.0, 9.1)
# Drone at position(2.1, 7.0)
# Drone at position(2.2, 4.9)
# Drone at position(2.3, 2.6)
# Drone at position(2.3, 0.2)

# After 26 steps of 0.1 seconds (2.6 seconds), the drone has landed.
# It has traveled a distance of 2.4 meters.
# It has reached a maximum height of 30.0 meters.

# %%
import math


class Drone():  #class should store: distanceHoriz, height, speedHoriz, speedVert   
    t = 0.0
    nSteps = 0
    maxH = 0.0

    def __init__(self, hIni, vIni, angle, stepTime):
        self.hIni = hIni
        self.vIni = vIni
        self.angle = angle
        self.stepTime = stepTime
    
    def get_pos_x(self): #returns horizontal traveled distance
        return self.vIni*math.cos(math.radians(self.angle))*Drone.t

    def get_pos_y(self): #returns vertical traveled distance 
        return self.hIni + self.vIni*math.sin(math.radians(self.angle))*Drone.t - 0.5*9.8*(Drone.t**2)
    
    def updated_position(self): #given a number `t` of seconds, it updates the position and velocity of the projectile after that time has elapsed
        Drone.maxH = self.hIni
        while self.get_pos_y() > 0.0:
            print(f"Drone at position ({self.get_pos_x():.1f}, {self.get_pos_y():.1f})")
            if self.get_pos_y() > Drone.maxH:
                Drone.maxH = self.get_pos_y()
            Drone.t += self.stepTime
            Drone.nSteps += 1
            

def land(h_0, v_0, angle, stepT):
    mi_Drone = Drone(h_0, v_0, angle, stepT)
    mi_Drone.updated_position()
    print("After ",mi_Drone.nSteps," steps of ",stepT," seconds (",mi_Drone.nSteps*stepT," seconds), the drone has landed.")
    print(f"It has traveled a distance of {mi_Drone.get_pos_x():.1f} meters.")
    print(f"It has reached a maximum height of {mi_Drone.maxH:.1f} meters.")

land(30, 1, 20, 0.1)

# %% [markdown]
# ### Exercise 5
# 
# Define a function called `matrix_operation` that receives an integer `n` as argument. The function should create a NumPy array (vector) with the integers within the interval $[n,n+25)$ and perform the following operations:
# 
# + Calculate the mean and standard deviation of the array and print it on the screen.
# + Reshape the array into a 5x5 matrix, calculate the determinant of the matrix and print the result on the screen.
# + Return a tuple with the three computed values `(mean, std, determinant)`.

# %%
# Example

# matrix_operation(1)
# The mean and standard deviation of the vector is 13.0 +/- 7.211102550927978.
# The determinant of the matrix is 0.0.

# %%
import numpy

def matrix_operation(n):
    #create a NumPy array (vector) with integers [n,n + 25)
    vector = numpy.arange(n, n + 25)

    #mean & standard deviation of the vector 
    mean = numpy.mean(vector)
    std = numpy.std(vector)
    print(f"The mean and standard deviation of the vector is {mean:.1f} +/- {std}.")

    #reshape array into a 5x5 matriz and calculate the determinant
    matrix = vector.reshape(5,5)
    det = numpy.linalg.det(matrix)
    print(f"The determinant of the matrix is {det:.1f}.")

matrix_operation(1)

# %% [markdown]
# ### Exercise 6
# 
# Create a function called `plot_functions` that makes a figure and plot the following functions over the range $[0, 10]$:
# 
# + $y_1 = sin(x)$
# + $y_2 = cos(x)$
# 
# The figure should also include appropriate labels, title, and a legend.

# %%



