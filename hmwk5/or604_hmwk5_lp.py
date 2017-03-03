from gurobipy import *
import csv
import sqlite3
import pandas as pd

# formulate the LP that minimizes transportation costs while ensuring all supply
# and demand restrictions are satisfied

# Upload csv file of stores
storeReader = csv.reader(open('dominos_good_data.csv', 'rb'))
storeHeaders = storeReader.next()
storeHeaders
# Pair stores with states
storeStateDict = dict((row[0],row[4]) for row in storeReader)


# Initiate Distributor CSV reader
distReader = csv.reader(open('dominos_distributors.csv', 'rU'))
distHeaders = distReader.next()
distHeaders
# Pair distributors with state
distStateDict = dict((row[0],row[3]) for row in distReader)

# Match stores and distributors in the same state
# stateDict = []
# for row in distStateDict:
#     for item in row:
#         if item.values() in distStateDict.values():
#             stateDict.append(item.keys(), item.values(), distStateDict.keys())
# print stateDict

# Initiate Distributor CSV reader
distReader = csv.reader(open('dominos_distributors.csv', 'rU'))
distHeaders = distReader.next()
distHeaders
# Pair distributors with supply capacity
distributorSuppDict = dict((row[0],row[7]) for row in distReader)
print distributorSuppDict

#agreggate the average demand for each store
demandDf = pd.read_csv('dominos_daily_demand.csv')
averageDf = demandDf.groupby('Store Number', as_index=False).mean()

# demand = {}
# for row in averageDf.to_csv():
#     demand[row[1]] = float(row[2])
# print demand
# averageDemandDict = averageDf.set_index('Store Number').T.to_dict('records')
# print averageDemandDict

# Create variables

# Create constraints - demand, supply, etc.


# Create model
# myModel = Model()
# myModel.modelSense = GRB.MINIMIZE
# myModel.update()

# Optimize model and print result
