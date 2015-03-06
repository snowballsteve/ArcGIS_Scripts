##
## Clear default geodatabase.py
##
## 
## S. Porter
## 2/23/11
##

import arcpy, sys, os
from arcpy import env

env.workspace = "C:\\Users\\"+os.getenv("USERNAME")+"\\Documents\\ArcGIS\\Default.gdb"
for dataset in arcpy.ListDatasets():
	arcpy.Delete_management(dataset)
	
for featureclass in arcpy.ListFeatureClasses(): 	
	arcpy.Delete_management(featureclass)
	
for table in arcpy.ListTables(): 	
	arcpy.Delete_management(table)
