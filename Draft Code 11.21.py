# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import arcpy
from arcpy import env
env.workspace = r'C:\Users\dunmires\OneDrive - The University of Colorado Denver\Geog5092\Final Project\Denver.gdb'
env.overweriteOutput = 1
arcpy.CheckOutExtension ("Spatial")
import pandas

#Listing all feature classes in workspace
fcList = arcpy.ListFeatureClasses("","")  
for fc in fcList:  
    print(fc)  

#assigning objects to the elements of a lists 
streets = fcList[0]
zoning = fcList[1]
neighborhoods = fcList[2]
county = fcList[3]
parcels = fcList[4]
census2010 = fcList[5]
census2017 = fcList[6]


#projecting all feature classes
fcproj = []
for i  in fcList:
    arcpy.Project_management(i, i + '_proj', 102654)
    fcproj.append(i + '_proj')
print(fcproj)

#Clip & spatial join of Census data to Denver neighborhoods

census_list = ['CO_2010_proj', 'CO_2017_proj']
census_list2 = []
neigh = 'statistical_neighborhoods_proj'
cliplist = []
#Clipping census data to the county boundary just to get census tracks we are interested in
for c in census_list:
    arcpy.Clip_analysis(c, county, 'den_' + c[3:7])
    cliplist.append('den_' + c[3:7])
    #spatial join of block groups to neighborhood levels
for clip in cliplist:
    arcpy.SpatialJoin_analysis(clip, neighborhoods, clip + '_nbhd')
    #sj.append(arcpy.SpatialJoin_analysis(clip, neighborhoods, clip + '_Census_Neighborhoods'))



#FUNCTION FOR FEATURE CLASS TO PANDA DATAFRAME#
from pandas import DataFrame

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


#PARCEL DATA
par = 'parcels_proj'
arcpy.AddField_management(par, "Vacant", "SHORT")
arcpy.AddField_management(par, "L_Value", "SHORT")
arcpy.SpatialJoin_analysis(par, neigh, 'den_parcels')
dpar = 'den_parcels'

#Parcels to Dataframe
dfp = feature_class_to_pandas_data_frame(dpar,['D_CLASS_CN','LAND_VALUE', 'IMPROVEMEN', 'Vacant', 'L_Value','NBHD_NAME','LAND', 'OBJECTID'] )
dfp.insert(5, 'Total', 1)

#Boolean categorize Vacant Parcels
dfp.loc[dfp.D_CLASS_CN.isin(['VCNT LAND' , 'VCNT LAND - RES RATIO' , 'VCNT LAND I-0 ZONE' , 'VCNT LAND R-5 ZONE' , 'VCNT LAND R-X ZONE' , 'VCNT LAND W/MINOR STR']), ['Vacant']] = 1
dfp.loc[~dfp.D_CLASS_CN.isin(['VCNT LAND' , 'VCNT LAND - RES RATIO' , 'VCNT LAND I-0 ZONE' , 'VCNT LAND R-5 ZONE' , 'VCNT LAND R-X ZONE' , 'VCNT LAND W/MINOR STR']), ['Vacant']] = 0
#Boolean categorize Soft Parcels
dfp.loc[dfp['LAND_VALUE'] > dfp['IMPROVEMEN'], ['L_Value']] = 1
dfp.loc[dfp['LAND_VALUE'] <= dfp['IMPROVEMEN'], ['L_Value']] = 0

#Groupby Neighborhood
vdf = dfp.groupby(['NBHD_NAME']).sum()
ndf = vdf.drop('-99999')
ndf.insert(5, 'P_Vac',0)
ndf.insert(6, 'P_Lvalue', 0)
#Calculate % of Vacant and Soft Parcels
ndf['P_Vac'] = vdf['Vacant'] / vdf['Total'] * 100
ndf['P_Lvalue'] = vdf['L_Value'] / vdf['Total']*100

#Convert to CSV
ndf.to_csv(r'C:\Users\dunmires\OneDrive - The University of Colorado Denver\Geog5092\Final Project\DataParcels.csv')

#JOIN CSV TO NEIGHBORHOODS FEATURE CLASS
joindata = 'DataParcels.csv'
arcpy.JoinField_management(neigh, 'NBHD_NAME', joindata, 'NBHD_NAME')

    











#select by attribute ownership to remove from data
#OWNER_NAME IN ( 'CITY & COUNTY OF DENVER', 'STATE OF COLORADO DEPARTMENT OF TRANSPORTATION', 'DEPARTMENT OF TRANSPORTATION STATE OF COLORADO', 'BURLINGTON NORTHERN RR CO PROPERTY TAX DEPARTMENT', 'UNION PACIFIC RR CO', 'UNION PACIFIC RAILROAD COMPANY', 'REGIONAL TRANSPORTATION DISTRICT', 'DEPARTMENT OF TRANSPORTATION','DEPARTMENT OF TRANSPORTATION OF COLORADO', 'DEPARTMENT OF TRANSPORTATION STATE OF COLO', 'BURLINGTON NORTHERN RR CO')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        