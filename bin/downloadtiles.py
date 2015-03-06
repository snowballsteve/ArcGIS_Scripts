#!/bin/python
'''
OSIP Tile Downloader

Steven C. Porter
1/24/12
'''
import urllib2, sys, arcpy, os

'''
URL Reference

http://gis3.oit.ohio.gov/ZIPARCHIVES/IMAGERY/1FTGEOTIFF/Licking/S1900790_TIF.zip
http://gis3.oit.ohio.gov/ZIPARCHIVES/IMAGERY/1FTSIDTILES/Licking/S1900790_SID.zip
http://gis3.oit.ohio.gov/ZIPARCHIVES/ELEVATION/LIDAR/Licking/S1900790_LAS.zip
http://gis3.oit.ohio.gov/ZIPARCHIVES/ELEVATION/ASCIITILES/Licking/S1900790_ASCII.zip
'''
workingDirectory = sys.argv[2]
inputData = sys.argv[1]
osipNTiles = u"V:/projects-GIS/Data/OSIP_data/OSIP_N_Tiles.shp"
osipSTiles = u"V:/projects-GIS/Data/OSIP_data/OSIP_S_Tiles.shp"
countyData = u"V:/projects-GIS/Data/Statewide.gdb/Political_Administrative_Units/Counties"

typeDict = {'1FTGEOTIFF': sys.argv[3], '1FTSIDTILES': sys.argv[4], 'LIDAR': sys.argv[5], 'ASCIITILES': sys.argv[6]}
tileDict = {'1FTGEOTIFF': ['IMAGERY', 'TIF'], '1FTSIDTILES': ['IMAGERY', 'SID'], 'LIDAR': ['ELEVATION', 'LAS'],
            'ASCIITILES': ['ELEVATION', 'ASCII']}


def getDownloadDict(inputData):
    arcpy.AddMessage("Determining needed Tiles")
    #flush memory
    from arcpy import env

    env.workspace = "in_memory"
    for dataset in arcpy.ListDatasets():
        arcpy.Delete_management(dataset)

    for featureclass in arcpy.ListFeatureClasses():
        arcpy.Delete_management(featureclass)

    for table in arcpy.ListTables():
        arcpy.Delete_management(table)

    env.workspace = workingDirectory
    stiles = arcpy.MakeFeatureLayer_management(osipSTiles, "stiles")
    ntiles = arcpy.MakeFeatureLayer_management(osipSTiles, "ntiles")
    arcpy.SelectLayerByLocation_management(stiles, "INTERSECT", inputData, "", "NEW_SELECTION")
    arcpy.SelectLayerByLocation_management(ntiles, "INTERSECT", inputData, "", "NEW_SELECTION")

    arcpy.Union_analysis([stiles, ntiles, countyData], "in_memory/union", "ALL", "")
    union = arcpy.MakeFeatureLayer_management("in_memory/union", "union")
    arcpy.SelectLayerByLocation_management(union, "INTERSECT", inputData, "", "NEW_SELECTION")
    searchData = arcpy.CopyFeatures_management(union, "in_memory/searchdata")
    dlist = {}
    rows = arcpy.SearchCursor(searchData)
    for row in rows:
        dlist[row.getValue("TILE")] = row.getValue("COUNTY_NAM")
    arcpy.Delete_management(union)
    arcpy.Delete_management(searchData)
    arcpy.Delete_management(stiles)
    arcpy.Delete_management(ntiles)
    return dlist


def getZip(url):
    file_name = url.split('/')[-1]
    if os.path.exists(workingDirectory + "\\" + file_name):
        arcpy.AddMessage("File %s exists, skipping" % file_name)
    else:
        u = urllib2.urlopen(url)
        f = open(workingDirectory + "\\" + file_name, 'wb')
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)

        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8) * (len(status) + 1)
            print status,

        f.close()

#build types list	


#download
download = getDownloadDict(inputData)
numYes = 0
for item in typeDict.values():
    if item == "true": numYes = numYes + 1

arcpy.AddMessage("Downloading %d Tiles" % (len(download) * numYes))
arcpy.SetProgressor("step", "Downloading Tiles", 0, len(download) * numYes, 1)
for type, yes in typeDict.iteritems():
    if (yes == "true"):
        for sid, county in download.iteritems():
            try:
                getZip("http://gis3.oit.ohio.gov/ZIPARCHIVES/" + tileDict[type][
                    0] + "/" + type + "/" + county.rstrip() + "/" + sid + "_" + tileDict[type][1] + ".zip")
            except urllib2.URLError:
                arcpy.AddWarning("Error downloading %s-%s" % (sid, county))
            arcpy.SetProgressorPosition()
