##
# MakeMXDThumbnails
# 
# Makes thumbnails for all passed mxds
#
# S. Porter
# 6/24/11
##


import arcpy, sys, os
files = sys.argv[1]


for file in files.split(";"):
    file=file.strip("'")
    map = arcpy.mapping.MapDocument(file)
    map.deleteThumbnail()
    map.makeThumbnail()
    del map