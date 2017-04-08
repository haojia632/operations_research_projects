# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 15:04:58 2017

@author: mquijada
"""
import csv
import sqlite3
from gurobipy import *

# read csv files
nflTeamReader = csv.reader(open('nfl_team_data.csv', 'rU'))
weekSlotNetworkReader = csv.reader(open('week_slot_network.csv', 'rU'))
awayHomeReader = csv.reader(open('away_home_2017.csv', 'rU'))

# Team lists and dictionary
teamList = []
nflTeamInfo = []
nflTeamDict ={}
for i in nflTeamReader:
    teamList.append(i[0])
    nflTeamInfo.append([i[0], i[1], i[2], i[3], i[4]])
    nflTeamDict[i[0]] =[i[1], i[2], i[3], i[4]]

# Away/Home games list
awayGamesList = []
for i in awayHomeReader:
    awayGamesList.append([i[0],i[1]])


# week, timeslot, network list 
weekSlotNetList =[]
timeSlots ={}
for i in weekSlotNetworkReader:
    weekSlotNetList.append([i[0],i[1],i[2]])
    timeSlots[(i[0], i[1])] = i[1], i[2]
#timeSlots = {x:[] for x in range(1,18)}

primeTime = set(('MON1','MON2','THUN','SUNN'))


allowableGames =[]
for m in awayGamesList:
    if nflTeamDict[m[0]][3] + nflTeamDict[m[1]][3] >= 4:
        for week in timeSlots:
            for s in timeSlots[week]:
                if s[0] in primeTime:
                    qp =(nflTeamDict[m[0]][3] + nflTeamDict[m[1]][3]) * 2
                    allowableGames.append((m[0],m[1], week, s[0], s[1],qp))


            
            
# Conference Dictionary
confDict ={}
confDict['AFC'] ={}
confDict['NFC'] = {}
 
afcSouthList =[]
afcNorthList =[]
afcWestList =[]
afcEastList =[]

nfcSouthList =[]
nfcNorthList =[]
nfcWestList =[]
nfcEastList =[]
 
for i in nflTeamInfo:
    if i[1] == 'AFC' and i[2] == 'SOUTH':
        afcSouthList.append(i[0])
        confDict['AFC']['SOUTH'] = afcSouthList
    if i[1] == 'AFC' and i[2] == 'NORTH':
        afcNorthList.append(i[0])
        confDict['AFC']['NORTH'] = afcNorthList
    if i[1] == 'AFC' and i[2] == 'WEST':
        afcWestList.append(i[0])
        confDict['AFC']['WEST'] = afcWestList
    if i[1] == 'AFC' and i[2] == 'EAST':
        afcEastList.append(i[0])
        confDict['AFC']['EAST'] = afcEastList        
        
    if i[1] == 'NFC' and i[2] == 'SOUTH':
        nfcSouthList.append(i[0])
        confDict['NFC']['SOUTH'] = nfcSouthList
    if i[1] == 'NFC' and i[2] == 'NORTH':
        nfcNorthList.append(i[0])
        confDict['NFC']['NORTH'] = nfcNorthList
    if i[1] == 'NFC' and i[2] == 'WEST':
        nfcWestList.append(i[0])
        confDict['NFC']['WEST'] = nfcWestList
    if i[1] == 'NFC' and i[2] == 'EAST':
        nfcEastList.append(i[0])        
        confDict['NFC']['EAST'] = nfcEastList

# List of West Coast Teams
westCoastTeams =[]
for i in nflTeamInfo:
    if i[2] =='WEST':
        westCoastTeams.append(i[0])
        
# Create database 
conn = sqlite3.connect('NFL_2017.db')
myCursor = conn.cursor()

# Create tables

myCursor.execute("DROP TABLE tblMatchups")
tblString = '''CREATE TABLE IF NOT EXISTS tblMatchups (
            AWAY_TEAM TEXT,
            HOME_TEAM TEXT); '''
myCursor.execute(tblString)
myCursor.executemany('''INSERT INTO tblMatchups VALUES(?,?)''', awayGamesList)
conn.commit()

myCursor.execute("DROP TABLE tblTeamData")
teamString = '''CREATE TABLE IF NOT EXISTS tblTeamData (
            TEAM TEXT,
            CONFERENCE TEXT,
            DIVISION TEXT,
            QUALPOINT REAL,
            TIMEZONE INTEGER); '''
myCursor.execute(teamString)
myCursor.executemany('''INSERT INTO tblTeamData VALUES(?,?,?,?,?)''', nflTeamInfo)
conn.commit()

myCursor.execute("DROP TABLE tblTimeData")
teamString = '''CREATE TABLE IF NOT EXISTS tblTimeData (
            WEEK INTEGER,
            TIMESLOT TEXT,
            NETWORK TEXT); '''
myCursor.execute(teamString)
myCursor.executemany('''INSERT INTO tblTimeData VALUES(?,?,?)''', weekSlotNetList)
conn.commit()

myCursor.execute("DROP TABLE tblGameVariables")
varString = '''CREATE TABLE IF NOT EXISTS tblGameVariables (
            AWAY_TEAM TEXT,
            HOME_TEAM TEXT,
            WEEK INTEGER,
            SLOT TEXT,
            NETWORK TEXT,
            QUALPOINT REAL); '''
myCursor.execute(varString)
conn.commit()

#Create Model 
#myModel = Model()
#myModel.ModelSense = GRB.MINIMIZE
#myModel.update()

