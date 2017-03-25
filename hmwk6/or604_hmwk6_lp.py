from gurobipy import *
import csv
import sqlite3
import pandas as pd
from geopy.distance import vincenty

# Problem 1 

# average Demand 
demandDf = pd.read_csv('dominos_daily_demand.csv')
averageDf = demandDf.groupby('store', as_index=False).mean()

avgDict = {}
for i in range(1,4862):
    avgDict[str(averageDf['store'][i])] = int(round(averageDf['demand'][i] * 4, 0))

# supply with lat/lon and cost for 4 days of demand 
distReader = csv.reader(open('dominos_distributors.csv', 'rU'))
distDict = {}
for i in distReader:
    distDict[i[0]]= [i[5], i[6], int(int(i[7])/7.0 * 4.0), i[8]]

    
# distance Function 
def calculate_distance(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return vincenty(point1, point2).miles

# store Distance 
storeReader = csv.reader(open('dominos_good_data.csv'))

storeDict = {}
for i in storeReader:
    storeDict[i[0]] = [i[6], i[7]]

# update Average Demand with dummy variable of 175 for missing stores
missingDemandDict = {}
for j in storeDict:
     if j not in avgDict:
            missingDemandDict[j] = 175
updatedDemandDict = dict(avgDict, **missingDemandDict)

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
    myVars[edge] = myModel.addVar(obj = float(distDict[edge[0]][3])*distance[edge] * updatedDemandDict[edge[1]]/9900, vtype = GRB.BINARY, name = 'x_%s_%s' % (edge[0], edge[1]))
myModel.update()
myModel.write('DominoTransportation6.lp')


# create supply contraints
myConstr = {}
for d in distDict:
    constrName = 'Supply %s' % d
    myConstr[constrName] = myModel.addConstr(quicksum(myVars[d,str(s)] * updatedDemandDict[s] for s in updatedDemandDict) <= distDict[d][2], name = constrName)
myModel.update()

# create updated demand constraint
for s in updatedDemandDict:
    constrName = 'Demand_%s' % s
    myConstr[constrName] = myModel.addConstr(quicksum(myVars[d,str(s)] for d in distDict) == 1, name = constrName)

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
conn = sqlite3.connect('db6Solution.db')
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

# Problem 2


