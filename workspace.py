# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#Importing arcpy
import arcpy, os
from arcpy import env
env.workspace = r'G:\Samuel\Semester_3\GIS_Programming\Final_Project\data\Denver.gdb'
env.overwriteOutput = 1
arcpy.CheckOutExtension("Spatial")
import arcpy, numpy
from pandas import DataFrame

###################################FUNCTIONS########################################
#function that I made from scratch
def feature_class_to_pandas_data_frame(feature_class, field_list):
    """
    Load data into a Pandas Data Frame for subsequent analysis.
    :param feature_class: Input ArcGIS Feature Class.
    :param field_list: Fields for input.
    :return: Pandas DataFrame object.
    """
    return DataFrame(
        arcpy.da.FeatureClassToNumPyArray(
            in_table=feature_class,
            field_names=field_list,
            skip_nulls=False,
            null_value=-99999
        )
    )

#function listing field names for analysis
def namefield(path):
  field_names = []
  fields = arcpy.ListFields(path,"")
  for field in fields:
    field_names.append(field.name)
  #return ";".join(field_names)
  return field_names



####################################START ANALYSIS###################################
#Listing all feature classes in workspace
fcList = arcpy.ListFeatureClasses("","")  
for fc in fcList:  
    print(fc)  

#assigning objects to the elements of a lists
#Make into for loop ; for f in fclist:
streets = fcList[0]
zoning = fcList[1]
neighborhoods = fcList[2]
parcels = fcList[3]
county = fcList[4]
census2010 = fcList[5]
census2017 = fcList[6]

#projecting all feature classes
fcproj = []
for i  in fcList:
    arcpy.Project_management(i, i + '_proj', 102654)
    fcproj.append(i + '_proj')
print(fcproj)

#creating census list
census_list = ['CO_BG_2010_proj', 'CO_BG_2017_proj']
cliplist =[]
sj = []
#Clipping census data to the county boundary just to get census tracks we are interested in
for c in census_list:
    arcpy.Clip_analysis(c, county, 'den_' + c[6:10])
    cliplist.append('den_' + c[6:10])
    #spatial join of block groups to neighborhood levels
    for clip in cliplist:
        sj.append(arcpy.SpatialJoin_analysis(clip, neighborhoods, clip + '_Census_Neighborhoods'))
        #for s in sj:
            #fieldnames.append(arcpy.ListFields(s))
        #print(fieldnames)
print(sj)


#Calling function for field names
x = namefield(sj[0])
y = namefield(sj[2])
print(y)

#creating datframes from the two feature classes
df10 = feature_class_to_pandas_data_frame(sj[0], x[55:])
df17 = feature_class_to_pandas_data_frame(sj[2], y[55:])
print(df10)
print(df17)


#merge both dataframes into one. 
pands.merge(df10, df17, on=UI, '_2010', '_2017')

df['diff_pop'] = 

#returns summary statistics from df columns
df.describe


df.groupby()
#making sure neighborhood column exists in fields
for col in df17.columns:
    print(col)


#removing selected attributes from parcel data based on ownership. AKA Denver lands
arcpy.SelectLayerByAttribute_management(parcels,"NEW_SELECTION", OWNER_NAME IN ( 'CITY & COUNTY OF DENVER', 'STATE OF COLORADO DEPARTMENT OF TRANSPORTATION', 'DEPARTMENT OF TRANSPORTATION STATE OF COLORADO', 'BURLINGTON NORTHERN RR CO PROPERTY TAX DEPARTMENT', 
                                                                                'UNION PACIFIC RR CO', 'UNION PACIFIC RAILROAD COMPANY', 'REGIONAL TRANSPORTATION DISTRICT'))


arcpy.SelectLayerByAttribute_management(parcels,"SWITCH_SELECTION")


############################TRIAL WITH MATPLOTLIB##############################################
import matplotlib.pyplot as plt
import numpy as np

# Fixing random state for reproducibility
np.random.seed(19680801)


x = np.arange(0.0, 50.0, 2.0)
y = x ** 1.3 + np.random.rand(*x.shape) * 30.0
s = np.random.rand(*x.shape) * 800 + 500

plt.scatter(x, y, s, c="g", alpha=0.5, marker=r'$\clubsuit$',
            label="Luck")
plt.xlabel("Leprechauns")
plt.ylabel("Gold")
plt.legend(loc='upper left')
plt.show()


