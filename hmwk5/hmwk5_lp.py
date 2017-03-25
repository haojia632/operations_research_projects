# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 18:29:01 2017

@author: mquijada
"""

from gurobipy import *
import csv
import sqlite3
import pandas as pd
from geopy.distance import vincenty

# Average Demand 
demandDf = pd.read_csv('dominos_daily_demand.csv')
averageDf = demandDf.groupby('Store Number', as_index=False).mean()

avgDict = {}
for i in range(1,4862):
    avgDict[averageDf['Store Number'][i]] = int(round(averageDf['Demand'][i] * 4, 0))


# Supply with lat/lon and cost 
distReader = csv.reader(open('dominos_distributors.csv', 'rU'))

distDict = {}
for i in distReader:
    distDict[i[0]]= [i[5], i[6], int(int(i[7])/7.0 * 4.0), i[8]]

# Distance Function 
def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return vincenty(point1, point2).miles

# Store Distance 
storeReader = csv.reader(open('dominos_good_data.csv'))

storeDict = {}
for i in storeReader:
    storeDict[i[0]] = [i[6], i[7]]

# Variables
distance = {}
for d in distDict:
    dlat = float(distDict[d][0])
    dlon = float(distDict[d][1])
    for s in storeDict:
        slat = float(storeDict[s][0])
        slon = float(storeDict[s][1])
        distance[d,s] = calculate_distance(dlat,dlon,slat,slon) 

# create the model
myModel = Model()
myModel.ModelSense = GRB.MINIMIZE
myModel.update() 

myVars = {}
# edge is the key of the dictionary 
for edge in distance:
    myVars[edge] = myModel.addVar(obj = float(distDict[edge[0]][3])*distance[edge]/9900, vtype = GRB.CONTINUOUS, name = 'x_%s_%s' % (edge[0], edge[1]))
myModel.update()
myModel.write('DominoTransportation.lp')


# create supply contraints
myConstr = {}
for d in distDict:
    constrName = 'Supply %s' % d
    myConstr[constrName] = myModel.addConstr(quicksum(myVars[d,str(s)] for s in avgDict) <= distDict[d][2], name = constrName)
myModel.update()

# create demand constraint
for s in avgDict:
    constrName = 'Demand_%s' % s
    myConstr[constrName] = myModel.addConstr(quicksum(myVars[d,str(s)] for d in distDict) >= avgDict[s], name = constrName)

myModel.update()


myModel.optimize()

mySolList = []
if myModel.status == GRB.OPTIMAL:
    mySolution = []
    for v in myVars:
        if myVars[v].x > 0.0:
            print v, myVars[v].x, myVars[v].varName
            mySolList.append((v[0], v[1], myVars[v].x, myVars[v].varName))
            
# Add Solution to a database
conn = sqlite3.connect('db5Solution.db')
cursor = conn.cursor()
cursor.execute(''' DROP TABLE OptimalSolution''')
cursor.execute('''CREATE TABLE OptimalSolution (
distributorId int,
storeId int,
distanceMiles numeric,
pairSummary char (50),
databaseEntry datetime
)
''')
cursor.executemany('''INSERT INTO OptimalSolution VALUES(?,?,?,?,current_timestamp)''', mySolList)
conn.commit()
