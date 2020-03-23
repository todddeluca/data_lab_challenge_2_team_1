import pandas as pd
import sierra_leone
import copy
import numpy as np
import pickle 

#load csv's in to data frames
pops = pd.read_csv("pops.csv")
cases = pd.read_csv("cases.csv")

#change these to alter plots
popCap = 1000000
stdMultiplier = 1 #the difference between % infected in standard deviations required for a surprising neighbor

myList = {} #going to be populations by chiefdom
counter = 0

#initialize a list of dictionaries of dictionaries
for province in sierra_leone.provinces:
    myList[province] = {}
for province in sierra_leone.provinces:
    for district in sierra_leone.province2districts[province]:
        myList[province][district] = {}

for province in sierra_leone.provinces:
    for district in sierra_leone.province2districts[province]:
        for chiefdom in sierra_leone.district2chiefdoms[district]:
            myList[province][district][chiefdom] = 0

#make a copy of our data structure for tallying cases in the next loop
myCounters = copy.deepcopy(myList)

#fill dictionary with district populations from imported dataframe
for index, row in pops.iterrows():
    for province in sierra_leone.provinces:
        for district in sierra_leone.province2districts[province]:
            for chiefdom in sierra_leone.district2chiefdoms[district]:
                if (province == row["Province"] and district == row["District"] and chiefdom == row["Chiefdom"]):  
                    #counter+=1
                    if int(row["2004 population"]) > popCap:
                        myList[province][district][chiefdom] = popCap
                    else:
                        myList[province][district][chiefdom] = int(row["2004 population"])
                    
                    
# go through cases.csv and tally cases in corresponding districts
print(type(myCounters))
for index, row in cases.iterrows():
    province = sierra_leone.district2province.get(row['District'])
    district = row['District']
    chiefdom = row['Chiefdom']
    myCounters[province][district][chiefdom] += 1

#show case totals in each district
print(myCounters)

#keep track of total cases and sum to calculate std
total = 0
sum=0
#loop divides district case counts my district populations for % population infected
for province in sierra_leone.provinces:
    for district in sierra_leone.province2districts[province]:
        for chiefdom in sierra_leone.district2chiefdoms[district]:
            try: 
                myCounters[province][district][chiefdom] = 100.0*float(myCounters[province][district][chiefdom])/float(myList[province][district][chiefdom])
                total+=myCounters[province][district][chiefdom]
                sum+=1
            #shouldn't hit this clause, was used for finding name errors
            except ZeroDivisionError:
                #
                print(province, district, chiefdom)

#display % infected between May 2014 and Sept 2015 in Sierra Leone
#print("\n\n MY PERCENTS \n\n")


#calculate average for std
avg = total/sum

#totalling each (% - avg) ^ 2
total = 0
ctr=0
for province in sierra_leone.provinces:
    for district in sierra_leone.province2districts[province]:
        for chiefdom in sierra_leone.district2chiefdoms[district]:
            total += np.power(myCounters[province][district][chiefdom]-avg,2)
            ctr+=1
std = stdMultiplier*np.sqrt(total/sum)

print("std: ",std)
adjList = pd.read_csv("sierra_leone_chiefdom_adjacency.csv")

#compiling adjList for surprising districts, also another one of our datastructures storing a boolean value
surpAdjList = []
excCounter=0
mySurprises = copy.deepcopy(myList)
myAdjLists = copy.deepcopy(myList)
for index, row in adjList.iterrows():
    for province in sierra_leone.provinces:
        for district in sierra_leone.province2districts[province]:
            for chiefdom in sierra_leone.district2chiefdoms[district]:
                if(mySurprises[province][district][chiefdom] > 30):
                    mySurprises[province][district][chiefdom] = 0
                    myAdjLists[province][district][chiefdom] = 0
                try:
                    if(row["OBJECTID2_admin1Name"] == province and row["OBJECTID2_admin2Name"] == district and row["OBJECTID2_admin3Name"] == chiefdom  ):
                        myAdjLists[province][district][chiefdom] +=1
                        if( np.abs(myCounters[province][district][chiefdom] - myCounters[row["OBJECTID1_admin1Name"]][row["OBJECTID1_admin2Name"]][row["OBJECTID1_admin3Name"]]) > std):
                            if ( myCounters[province][district][chiefdom] > myCounters[row["OBJECTID1_admin1Name"]][row["OBJECTID1_admin2Name"]][row["OBJECTID1_admin3Name"]]):
                                #mySurprises[province][district][chiefdom] += 1
                                mySurprises[row["OBJECTID1_admin1Name"]][row["OBJECTID1_admin2Name"]][row["OBJECTID1_admin3Name"]] -= 1
                            else:
                                #mySurprises[row["OBJECTID1_admin1Name"]][row["OBJECTID1_admin2Name"]][row["OBJECTID1_admin3Name"]] += 1
                                mySurprises[province][district][chiefdom] -= 1
    
                except KeyError as ke:
                    print("EXCEPT: adj obj1: ", row["OBJECTID1_admin1Name"], row["OBJECTID1_admin2Name"], row["OBJECTID1_admin3Name"], " obj2: ", row["OBJECTID2_admin1Name"], row["OBJECTID2_admin2Name"], row["OBJECTID2_admin3Name"]," LHD files: ", province, district, chiefdom)
                    print(ke)
                    excCounter+=1

#print("MY SURPRISES \n\n\n", mySurprises)
#print("MY myAdjLists \n\n\n", myAdjLists)

for province in sierra_leone.provinces:
    for district in sierra_leone.province2districts[province]:
        for chiefdom in sierra_leone.district2chiefdoms[district]:
            # we must divide by 2*totalNeighbors, as each surprising neighbor is counted twice, once by itself, once by its neighbor.
            mySurprises[province][district][chiefdom] /= (2*myAdjLists[province][district][chiefdom])




## the colab was being fussy with plotly express versions so I've moved some code here

import geopandas
import pandas as pd
import json

#NOTE: this is a different .shp file where names were edited to match data
#            1m is original, this is:         2m
chief = geopandas.read_file('sle_admbnda_adm3_2m_gov_ocha_20161017.shp')






# LOOP TO
# ADD COLS
# TO DATAFRAME
indices = []
percInf = []
surp1Neighbor = []
all = []
myPops = []
for index, row in chief.iterrows():
    
    Cprovince = row['admin1Name']
    Cdistrict = row['admin2Name']
    Cchiefdom = row['admin3Name']
    
    all.append(index)
    for province in sierra_leone.provinces:
        for district in sierra_leone.province2districts[province]:
            for chiefdom in sierra_leone.district2chiefdoms[district]:
                
                if province == Cprovince and district == Cdistrict and chiefdom == Cchiefdom:
                    indices.append( index )
                    percInf.append( myCounters[province][district][chiefdom])
                    surp1Neighbor.append( mySurprises[province][district][chiefdom])
                    myPops.append(myList[province][district][chiefdom])


noData = set(all) - set(indices)

for i in noData:
    indices.append( i )
    percInf.append( 0)
    surp1Neighbor.append( 0)
    myPops.append( 0 )

percInfCol = pd.Series( percInf, index = indices )
surp1NeighborCol = pd.Series( surp1Neighbor, index = indices )

chief.insert(20, "PercentInfected", percInfCol)
chief.insert(21, "NumAdjacentSTDdiff", surp1NeighborCol)
chief.insert(22, "Population", myPops)


#build my plot, Thanks to Todd for this code!!
chiefdom_geojson_filename = "chiefdom.geojson"
chief.to_file(chiefdom_geojson_filename, driver = "GeoJSON")
with open(chiefdom_geojson_filename) as fh:
    chief_geojson = json.load(fh)
import plotly
import plotly.express as px
print(plotly.__version__)

# Plot Chiefdoms, colored by NumAdjacentSTDdiff
fig = px.choropleth(
                    chief,
                    geojson=chief_geojson,
                    #     color='Shape_Area',
                    color='NumAdjacentSTDdiff',
                    locations="OBJECTID",
                    featureidkey="properties.OBJECTID",
                    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(mapbox_style="white-bg")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

