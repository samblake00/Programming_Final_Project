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

#Listing all feature classes in workspace
fcList = arcpy.ListFeatureClasses("","")  
for fc in fcList:  
    print(fc)  

#assigning objects to the elements of a lists 
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
    arcpy.Project_management(i, i + '_proj', 26954)
    fcproj.append(i + '_proj')
print(fcproj)

#creating census list
census_list = ['CO_BG_2010_proj', 'CO_BG_2017_proj']
#Clipping census data to the county boundary just to get census tracks we are interested in
for c in census_list:
    arcpy.Clip_analysis(c, county, 'den_' + c[6:10])

#spatial join of block groups to neighborhood levels
SpatialJoin(census_clipped, neighborhoods, Census_Neighborhoods)








