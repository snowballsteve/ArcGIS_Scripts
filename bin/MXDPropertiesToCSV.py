##
# MXDPropertiesToCSV
# 
# Exports some base mxd properties to a csv file
#
# S. Porter
# 6/24/11
##


import arcpy, sys, os
files = sys.argv[1]
outputFile = sys.argv[2]

outStream = open(outputFile,'w')
outStream.write("\"FileName\",\"Title\",\"Summary\",\"Description\",\"Author\",\"Credits\"\n")
for file in files.split(";"):
    file=file.strip("'")
    map = arcpy.mapping.MapDocument(file)
    outStream.write("\""+os.path.basename(file).split(".")[0]+"\",\""+map.title+"\",\""+map.summary+"\",\""+map.description+"\",\""+map.author+"\",\""+map.credits+"\"\n")
    
outStream.close()