# -*- coding: utf-8 -*-
"""
Final Project Code
Created by Sarah Dunmire and Samuel Blake
December 5, 2019
GIS Programming and Automation
"""

#Importing packages needed for script and setting workspace
import arcpy, os
from arcpy import env
env.workspace = r'G:\Samuel\Semester_3\GIS_Programming\Final_Project\deliverables\Denver.gdb'
env.overwriteOutput = 1
arcpy.CheckOutExtension("Spatial")
from pandas import DataFrame


################################################################FUNCTIONS#####################################################
#function converting feature class to a pandas dataframe
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


########################################################START ANALYSIS##########################################################
#Listing all feature classes in workspace & projecting
fcList = arcpy.ListFeatureClasses("","")  
fcproj = []
for i  in fcList:
    arcpy.Project_management(i, i + '_proj', 102654)
    fcproj.append(i + '_proj')


#assigning objects to the elements of a lists
streets = fcproj[0]
neighborhoods = fcproj[1]
county = fcproj[2]
par = fcproj[3]
census2010 = fcproj[4]
census2017 = fcproj[5]

    
    
#creating census list
census_list = ['CO_2010_proj', 'CO_2017_proj']
cliplist =[]
sj = []
#Clipping census data to the county boundary just to get census tracks we are interested in
for c in census_list:
    fields = namefield(c)
    arcpy.Clip_analysis(c, county, 'den_' + c[3:7])
    cliplist.append('den_' + c[3:7])
    #spatial join of block groups to neighborhood levels
    for clip in cliplist:
        sj.append(arcpy.SpatialJoin_analysis(clip, neighborhoods, clip + '_Census_Neighborhoods', "#", "#", "#", 'HAVE_THEIR_CENTER_IN'))
        #Adding fields and calculating geometry for 2010 and 2017 census data
        for r in sj:
            arcpy.AddField_management(r,"geom2","double")
            exp = "float(!SHAPE.AREA!)"
            arcpy.CalculateField_management(r, "geom2", exp)



#Calling function for field names
x = namefield(sj[0])
y = namefield(sj[2])

#creating datframes from the two feature classes
df10 = feature_class_to_pandas_data_frame(sj[0], x[30:])
df17 = feature_class_to_pandas_data_frame(sj[2], y[30:])


#Removing polygons bigger than 750000 sq ft which are not complete census tracts.
#2010 data
df10_1 = df10[df10.GISJOIN_1 != 'G08000100083531']
df10_2 = df10_1[df10_1.GISJOIN_1 != 'G08000100083091']
df10_3 = df10_2[df10_2.GISJOIN_1 != 'G08005900120502']
df10_4 = df10_3[df10_3.GISJOIN_1 != 'G08005900120503']
df10_5 = df10_4[df10_4.GISJOIN_1 != 'G08000500068541']
#2017 data
df17_1 = df17[df17.GISJOIN_1 != 'G08000100083531']
df17_2 = df17_1[df17_1.GISJOIN_1 != 'G08000100083091']
df17_3 = df17_2[df17_2.GISJOIN_1 != 'G08005900120502']
df17_4 = df17_3[df17_3.GISJOIN_1 != 'G08005900120503']
df17_5 = df17_4[df17_4.GISJOIN_1 != 'G08000500068541']


#Removing polys under 750000 sq ft.& NBHD_NAME is null
#2010 data
dfselect10 = df10_5[df10_5.geom2 > 750000]
dfselect10_2 = dfselect10[dfselect10.NBHD_NAME != '-99999']
#2017 data
dfselect17 = df17_5[df17_5.geom2 > 750000]
dfselect17_2 = dfselect17[dfselect17.NBHD_NAME != '-99999']


#merge both dataframes into one. 
dfmerge = DataFrame.merge(dfselect10_2, dfselect17_2, on='GISJOIN_1', suffixes=('_2010', '_2017'))
#groupby neighborhood for the current data frames
#all summed except median household income and median home value
grouping = dfmerge.groupby('NBHD_NAME_2010')
sums = grouping.sum()
medians = grouping.median()

#differences calculated for chosen criteria
#differences for all population fields
sums['diff_pop'] = sums['AHY1E001'] - sums['JMAE001']
sums['diff_white'] = sums['AHY2E002'] - sums['JMBE002']
sums['diff_black'] = sums['AHY2E003'] - sums['JMBE003']
sums['diff_indian'] = sums['AHY2E004'] - sums['JMBE004']
sums['diff_asian'] = sums['AHY2E005'] - sums['JMBE005']
sums['diff_hawaii'] = sums['AHY2E006'] - sums['JMBE006']
sums['diff_other'] = sums['AHY2E007'] - sums['JMBE007']
sums['diff_2more'] = sums['AHY2E008'] - sums['JMBE008']
sums['diff_2more+'] = sums['AHY2E009'] - sums['JMBE009']
sums['diff_2more++'] = sums['AHY2E010'] - sums['JMBE010']
#differences for all population fields
sums['diff_totalhis'] = sums['AHZBE001'] - sums['JMKE001']
sums['diff_his'] = sums['AHZBE002'] - sums['JMKE002']
sums['diff_nothis'] = sums['AHZBE003'] - sums['JMKE003']
#differences for schooling over the age of 25
sums['diff_totalschool'] = sums['AH04E001'] - sums['JN9E001']
sums['diff_associates'] = sums['AH04E021'] - sums['JN9E014']
sums['diff_bachelors'] = sums['AH04E022'] - sums['JN9E015']
sums['diff_masters'] = sums['AH04E023'] - sums['JN9E016']
sums['diff_professional'] = sums['AH04E024'] - sums['JN9E017']
sums['diff_doctorate'] = sums['AH04E025'] - sums['JN9E018']
#differences (medians) for median household income & median home value
medians['diff_householdinc'] = medians['AH1PE001'] - medians['JOIE001']
medians['diff_medianval'] = medians['AH53E001'] - medians['JTIE001']
#differences for housing units
sums['diff_tothousingunits'] = sums['AH35E001'] - sums['JRIE001']
sums['diff_occupied'] = sums['AH36E002'] - sums['JRJE002']
sums['diff_vacant'] = sums['AH36E003'] - sums['JRJE003']
sums['diff_ownoccupied'] = sums['AH37E002'] - sums['JRKE002']
sums['diff_rentoccupied'] = sums['AH37E003'] - sums['JRKE003']

##################################################Binary Analysis#########################################################
#adding columns
sums.insert(96, 'white', 0)
sums.insert(97, 'black', 0)
sums.insert(98, 'hispanic', 0)
sums.insert(99, 'renter', 0)
sums.insert(100, 'owner', 0)
sums.insert(101, 'sum_crit', 0)
#median binary
medians.insert(74, 'homevalue', 0)
medians.insert(75, 'hhincome', 0)
medians.insert(76, 'sum_crit1', 0)

#sums binary columns
sums.loc[sums['diff_white'] > 0, ['white']] = 1
sums.loc[sums['diff_black'] < 0, ['black']] = 1
sums.loc[sums['diff_his'] < 0, ['hispanic']] = 1
sums.loc[sums['diff_rentoccupied'] < 0, ['renter']] = 1
sums.loc[sums['diff_ownoccupied'] > 0, ['owner']] = 1
sums['sum_crit'] = sums.white + sums.black + sums.hispanic + sums.renter + sums.owner
#median binary column
medians.loc[medians['diff_medianval'] > 0, ['homevalue']] = 1
medians.loc[medians['diff_householdinc'] > 0, ['hhincome']] = 1
medians['sum_crit1'] = medians.homevalue + medians.hhincome


#####################################################Final Step###########################################################
#Indexing sums and medians df to get only differences into new dataframe with all rows
sumdifferences_df = sums.iloc [:, 70:]
mediandifferences_df = medians.iloc[:, 70:]

#Merge both dataframes into one dataframe
final_df = DataFrame.merge(sumdifferences_df, mediandifferences_df, on='NBHD_NAME_2010')
final_df.insert(39, 'TotalScore', 0)
final_df['TotalScore'] = final_df['sum_crit'] + final_df['sum_crit1']

#Converting df to CSV
final_df.to_csv(r'G:\Samuel\Semester_3\GIS_Programming\Final_Project\deliverables\final_dataset.csv')

#Join CSVs to statistical neighborhoods. The final step to display changes for each neighborhood
os.chdir(r'G:\Samuel\Semester_3\GIS_Programming\Final_Project\deliverables')
joindata = 'final_dataset.csv'
arcpy.JoinField_management(neighborhoods, 'NBHD_NAME', joindata, 'NBHD_NAME_2010')



#####################################################PARCEL DATA#############################################################
#par = 'parcels_proj'
arcpy.AddField_management(par, "Vacant", "SHORT")
arcpy.AddField_management(par, "L_Value", "SHORT")
arcpy.SpatialJoin_analysis(par, neighborhoods, 'den_parcels')
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
ndf.to_csv(r'G:\Samuel\Semester_3\GIS_Programming\Final_Project\deliverables\DataParcels.csv')

#Join CSV to neighborhoods feature class 
joindata = 'DataParcels.csv'
arcpy.JoinField_management(neighborhoods, 'NBHD_NAME', joindata, 'NBHD_NAME')

############################################################################################################################

