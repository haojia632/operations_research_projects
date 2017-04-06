# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 00:42:57 2017

@author: mquijada
"""


from bs4 import BeautifulSoup
import csv
import urllib2

url = "http://www.cityfeet.com/cont/district-of-columbia-retail-space#id=LN20064281"
page = urllib2.urlopen(url)
soup = BeautifulSoup(page, "lxml")


completeListing = soup.findAll('div', {'class' : 'property clearfix src-LN level-20'})
listingStreetAddress = soup.findAll('h2')
listingCityZip = soup.findAll('address')
listingPrice = soup.findAll('strong', {'class' : 'price'})
listingSize = soup.findAll('strong', {'class' : None})
listingDescription = soup.findAll('div', {'class' : 'propertydescription'})

listingList =[]

streetAddressList =[]
for i in listingStreetAddress:
    streetInfo = i.text
    if streetInfo[0].isdigit():
        streetAddressList.append(i.text)

cityZipList =[]
for i in listingCityZip:
    cityZipList.append(i.text)

priceList = []
for i in listingPrice:
    priceList.append(i.text)
    
sizeList = []
for i in listingSize:
    sizeInfo = i.text
    if sizeInfo[0].isdigit():
        sizeList.append(i.text)

    
descList = []
for i in listingDescription:
    descList.append(i.text)

aggregateList =[]
for j in streetAddressList:
    for i in cityZipList:
        zipCode = i
    for m in priceList:
        priceVar = m
    for k in sizeList:
        size = k
        print size
    for l in descList:
        description = l
    aggregateList.append([j,zipCode, priceVar, size, description])

print aggregateList
