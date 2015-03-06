'''
  SplitSourceByTypeAttribute
  seperates an input layer into seperate shapefiles or feature classes based on the unique values found in an input field
  
  author -- steven c. porter
  version -- 9/12/2012

'''

import arcpy,os


layer = arcpy.GetParameterAsText(0)
type_field = arcpy.GetParameterAsText(1)
outputFolder = arcpy.GetParameterAsText(2)

uniqueList = []
base = os.path.basename(layer)
arcpy.AddMessage("Processing %s" %(base))


cur = arcpy.SearchCursor(layer)
for row in cur:
	value = row.getValue(type_field)
	if not value in uniqueList: 
		uniqueList.append(value)
		arcpy.AddMessage("Found type %s" %(value))
	
del cur

for item in uniqueList:
	outfile = os.path.join(outputFolder,base.split(".")[0]+"_"+type_field + "_" + item)
	arcpy.AddMessage("Saving %s to %s" %(item,outfile))
	selectLayer = arcpy.MakeFeatureLayer_management(layer,"selectLayer")
	selectLayer = arcpy.SelectLayerByAttribute_management(selectLayer,"NEW_SELECTION", " \""+type_field+"\" = \'"+item+"\'")
	arcpy.CopyFeatures_management(selectLayer,outfile)
	arcpy.Delete_management(selectLayer)
