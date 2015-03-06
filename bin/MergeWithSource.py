##
## MergeWithSource.py
##
## Merges all inputs into one output with an Attribute indicating the Source
## This has only been tested with shapefile inputs, because it does copy everything to a shapefile
## during the process as to not add fields to existing data, shapefile limitiations will apply, such as
## 12 character attribute names. This script is intended to merge data received from clients that have no need to be
## seperate feature classes, thus reducing on data management problems.
## S. Porter
## 2/23/11
##

import arcpy, sys, os


#Input Variables
Input_Datasets = sys.argv[1]
Output_Dataset = sys.argv[2]
mergeData = []

for dataset in Input_Datasets.split(";"):
	currentName = os.path.basename(dataset)
	currentName = currentName.split(".")[0]
	copyLocation = "C:\\Windows\\Temp\\"+currentName+".shp"
	mergeData.append(copyLocation)
	arcpy.AddMessage(currentName)
	arcpy.Copy_management(dataset,copyLocation)
	arcpy.AddField_management(copyLocation,"Source","TEXT")
	arcpy.CalculateField_management(copyLocation,"Source","'"+currentName+"'","PYTHON")
	

arcpy.Merge_management(mergeData,Output_Dataset)

for shapefile in mergeData:
	arcpy.Delete_management(shapefile)