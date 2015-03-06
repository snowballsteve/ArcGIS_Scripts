'''
	Zoom to a selected features of first dataframe and first layer
	
	S. Porter
	2.17.12

'''

scale = 600

import arcpy
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd)[0]
try:
	layer = arcpy.mapping.ListLayers(mxd)[0]
	df.extent = layer.getSelectedExtent(False)
	df.scale = scale
except:
	arcpy.AddError("Error with zooming to selected")
	raise
	
arcpy.RefreshActiveView()
