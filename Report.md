# Capacitated Lot sizing problem by Mohamed Guetari and Muhammed Ali

# Introduction: 
In this project we tried to solve to Capacitated lot sizing and scheduling problem on parallel machines with tool synchronisation using Gurobi. 

The file named runcapacitatedlotsizing.py you will find the code for the model. 

The file readln.py represents the code that was used to extract, modify and adjust the data used. More information under "Data modification" below.

Note: please note that there are some decision variables from the GLSP that we added but did not use (we decided to keep them anyway and hope this is fine).

# Model description : 
The CLSP (Capacitated Lot Sizing Problem) model is a classical optimization problem in operations research and supply chain management. It involves determining an optimal production plan for a multi-period production system, taking into account capacity constraints, inventory carrying costs, and demand requirements.

In the CLSP, the goal is to minimize the total cost of production and inventory while satisfying customer demand. The problem is typically formulated as a mixed-integer linear programming (MILP) model.

The main components of the CLSP model include: Time Periods, Products, Demand, Production, Inventory and Capacity constraints 

The CLSP model aims to find production quantities for each period that minimize the sum of production costs and inventory holding costs, while meeting customer demand and respecting capacity constraints.

# Data modification 
To be able to read the test data files, some modification had to be done.
Check the "readLn.py" to see the code. 

1-We created a new function "readFile" that reads the data depending on the filename that we provide in input.

2-The data is being read line by line and breaks (splits) when it reaches the ";" symbol. 

3-N, T , M , K were converted and become integer.

4-The spaces in the data were replaced by "," symbol. 

5-The variables S, C and Sigma presented some problems. 

6-We converted the strings to tables. 

# Representation of the solutions 
We are very sorry for not being able to provide the solutions as there is a problem in our model that we couldn't fix.

The code seems to be running without errors but the outcome is "Model is infeasible ". 

