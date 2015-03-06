##  Drive IsoChrones
##
##  Takes as input a feature class, network dataset, min, max, and ring increment and creates contours roughly estimating locations of equal network cost, ie drive time or drive distance.
##  Smooth factor is an option used to smooth the output for cartographic representation
##
##  S. Porter
##  6/10/2011



import arcpy, sys, os

#start the progress bar
arcpy.SetProgressor("default","Initializing")


#Read passed arguments and raise exception if they are no good
try:
    v_points = str(sys.argv[1]) # Input points to produce rings from
    nd_streets = str(sys.argv[2]) #Network Dataset for Streets
    option_measureField = str(sys.argv[3]) #Distance or Time
    a = int(sys.argv[4]) #lower bound
    b = int(sys.argv[5]) #upper bound
    d = int(sys.argv[6]) #increments
    option_smoothing = str(sys.argv[7]) #smoothing option
    v_output = str(sys.argv[8]) #output points
except:
    arcpy.AddError("Error in arguments, check inputs")




#create smooth factor
if option_smoothing == "Very Smooth":
    smoothFactor = 4.0
elif option_smoothing == "Moderately Smooth":
    smoothFactor = 2.0
elif option_smoothing == "Smooth":
    smoothFactor = 1.0
elif option_smoothing == "Moderately Rough":
    smoothFactor = 0.5
elif option_smoothing == "Very Rough":
    smoothFactor = 0.25  
else:
    smoothFactor = 0 

try: 
    arcpy.CheckOutExtension("Network")
except:
    arcpy.AddError("This tool requires the Network Analyst Extension")
    
    
#set workspace
from arcpy import env
env.workspace = os.path.dirname(v_points)

#set overwrite and warn if needed
env.overwriteOutput = True 
if arcpy.Exists(v_output): arcpy.AddWarning("Overwritting "+v_output)    
arcpy.Copy_management(v_points, "Input")

#Check inputs
errorFlag = False 
if arcpy.Describe("Input").shapeType == "Polygon":
    arcpy.AddWarning("Converting Polygons to Vertex Points, this will increase time to solve")
    arcpy.SmoothPolygon_cartography("Input","SmoothInput","BEZIER_INTERPOLATION",0, False )
    arcpy.FeatureVerticesToPoints_management("SmoothInput","Input2")
    arcpy.Delete_management("Input")
    arcpy.Delete_management("SmoothInput")
    arcpy.Rename_management("Input2","Input")
    
    
if arcpy.Describe("Input").shapeType == "Polyline":
    arcpy.AddWarning("Converting Lines to Vertex Points, this will increase time to solve")
    arcpy.FeatureVerticesToPoints_management("Input","Input2")
    arcpy.Delete_management("Input")
    arcpy.Rename_management("Input2","Input")
    
if not arcpy.Describe("Input").shapeType == "Point":
    arcpy.AddError("Final Input Not Points, Check input feature class")
    errorFlag = True
    
    
#verify passed cost field exists in network dataset    
costError=True
for attribute in arcpy.Describe(nd_streets).attributes:
    if(attribute.usageType == "Cost" and attribute.name==option_measureField):
        costError=False
if costError: errorFlag=True

if a==0: a=d #in case they entered zero, we need to start one increment greater

if(a>b): 
    errorFlag = True
    arcpy.AddError("Lower radius is greater than upper radius")
    
if errorFlag:
    arcpy.AddError("Error, Halting")
    sys.exit(1)

   
    
#smoothing
arcpy.SetProgressor("step","Running Analysis",int(a),int(b+d),int(d))
for breakValue in range(a,b+d,d):
    arcpy.SetProgressorLabel("Creating Network")
    arcpy.MakeServiceAreaLayer_na(nd_streets,"SA", option_measureField,"TRAVEL_FROM",breakValue,"SIMPLE_POLYS","MERGE","RINGS","NO_LINES","#","#","#","#","ALLOW_UTURNS","#","#","#","#")
    arcpy.AddLocations_na("SA", "Facilities", "Input", "","")
    arcpy.SetProgressorLabel("Solving Network")
    arcpy.Solve_na("SA")
    arcpy.SetProgressorLabel("Smoothing Ring")
    extentValue = (arcpy.Describe("Polygons").extent.Xmax - arcpy.Describe("Polygons").extent.Xmin)/8+(arcpy.Describe("Polygons").extent.Ymax - arcpy.Describe("Polygons").extent.Ymin)/8
    arcpy.SmoothPolygon_cartography("Polygons","Smooth","PAEK",str(extentValue*smoothFactor), False )
    if breakValue == a: #This condition is the first ring to export, so it has unique
        arcpy.PolygonToLine_management("Smooth", v_output)
        arcpy.AddField_management(v_output,option_measureField,"LONG")
        arcpy.CalculateField_management(v_output,option_measureField, breakValue)
    else:
        arcpy.PolygonToLine_management("Smooth", "SmoothLines")
        arcpy.AddField_management("SmoothLines",option_measureField,"LONG")
        arcpy.CalculateField_management("SmoothLines",option_measureField, breakValue)
        arcpy.Append_management("SmoothLines",v_output)
        arcpy.Delete_management("SmoothLines")
        
    arcpy.Delete_management("Smooth")
    arcpy.SetProgressorPosition()


#cleanup
arcpy.SetProgressor("default","Cleaning Up")
arcpy.Delete_management("SA")
arcpy.Delete_management("Input")
arcpy.DeleteField_management(v_output,"LEFT_FID")
arcpy.DeleteField_management(v_output,"RIGHT_FID")

arcpy.SetProgressorLabel("Finished, thanks for using Steve\'s Tools")
arcpy.GetMessages()  
