# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 16:40:03 2017

@author: mquijada
"""

import or604_hmwk6_lp
import csv

for i in distDict:
    mileCost = distDict[i][3]
    print mileCost

# Flour Distributor Demand
distFlourDemand ={}
for x in mySolList:
    for i in distDict:
        if x[0] == i:
            mileCost = distDict[i][3]
    for j in updatedDemandDict:
        if x[1] == j:
            flourDemand = updatedDemandDict[j] * 3
            distFlourDemand[x[0]] =  flourDemand, mileCost 
print distFlourDemand 

ardentReader = csv.reader(open('ardent_mills_supply.csv', 'rU'))

# Flour Supply 
ardentDict ={}

for i in ardentReader:
    ardentDict[i[0]] = [i[1], i[2], int(int(i[3])/7.0 * 4.0)]

print ardentDict 

# Variables
distanceFlour = {}
for d in distDict:
    dlat = float(distDict[d][0])
    dlon = float(distDict[d][1])
    for s in ardentDict:
        slat = float(ardentDict[s][0])
        slon = float(ardentDict[s][1])
    for f in distFlourDemand:
        if f == d:
            distanceFlour[d,s] = calculate_distance(dlat,dlon,slat,slon)

# create the model
myModel2 = Model()
myModel2.ModelSense = GRB.MINIMIZE
myModel2.update()


myVars = {}
# edge is the key of the dictionary 
for edge in distanceFlour:
    myVars[edge] = myModel2.addVar(obj = float(distFlourDemand[edge[0]][1]) * distanceFlour[edge] * 3000000, vtype = GRB.BINARY, name = 'x_%s_%s' % (edge[0], edge[1]))
myModel2.update()
myModel2.write('DominoTransportation6_p2.lp')

# create one mill constraint 
for m in ardentDict:
    constrName = 'Demand_%s' % s
    myConstr[constrName] = myModel2.addConstr(quicksum(myVars[d,str(s)] for d in distFlourDemand) == 1, name = constrName)
    
myModel2.optimize()

mySolList2 = []
if myModel2.status == GRB.OPTIMAL:
    mySolution = []
    for v in myVars:
        if myVars[v].x > 0.0:
            print v, myVars[v].x, myVars[v].varName
            mySolList.append((v[0], v[1], myVars[v].x, myVars[v].varName))