##
#add an attribute to a point layer by spatial joining from a polygon layer
#
# S. Porter
# 8.10.2011
##


import arcpy, sys, os
from arcpy import env
env.overwriteOutput=True

def addAttributeFromPolygons(v_layer, v_field, v_joinLayer, v_joinField):
    env.workspace = os.path.dirname(v_layer)

    #check fields of join layer
    if(checkOrMakeField(v_joinLayer,v_joinField, False,"")==0):
        arcpy.AddError("Join Field Does Not Exist")
        sys.exit(1)
        
    #test if v_field exists, if not make it
    for field in arcpy.ListFields(v_joinLayer):
        if field.name == v_joinField:
            checkOrMakeField(v_layer,v_field, True,field.type)
        
     
    #add ID field for future us 
        
    #create field map
    fieldMappings = arcpy.FieldMappings()
    fieldMappings.removeAll()
    for item in arcpy.ListFields(v_layer):
        if item.type != "Geometry":
            fieldmap = arcpy.FieldMap()
            fieldmap.addInputField(v_layer, item.name)
            if item.name == v_field:
                fieldmap.addInputField(v_joinLayer,v_joinField)
            field = fieldmap.outputField
            field.name =item.name
            fieldmap.outputField = field
            fieldMappings.addFieldMap(fieldmap)
            
           
    #perform spatial join
    arcpy.SpatialJoin_analysis(v_layer,v_joinLayer,env.workspace + "\\SJ_Layer","JOIN_ONE_TO_ONE","KEEP_ALL",fieldMappings, "WITHIN")
    
    #use a join to map new info over, create list of Fields to drop
    dropFields = []
    for field in arcpy.ListFields(v_layer):
        if field.type == "OID":
            jField = field.name
            dropFields.append(field.name+"_1")
        elif field.name == v_field:
            dropFields.append("Join_Count")
            dropFields.append(v_field+"_1")
        else:
            dropFields.append(field.name+"_1")
            
    dropFields.append("TARGET_FID")
        
    
    arcpy.JoinField_management(v_layer, jField,"SJ_Layer", jField)
    arcpy.CalculateField_management(v_layer,v_field,"!"+v_field+"_1!","PYTHON")
    arcpy.DeleteField_management(v_layer, dropFields)
    
    
    arcpy.Delete_management("SJ_Layer")
    
    return 1;


def checkOrMakeField(v_layer, v_field, makeField, type):
    result=-1
    fieldFlag = False
    for field in arcpy.ListFields(v_layer):
        if field.name == v_field : fieldFlag = True
        
    if fieldFlag == False:
        if(makeField): 
            arcpy.AddField_management(v_layer,v_field,type)
            arcpy.AddWarning("Created field \""+v_field+"\" in "+v_layer)
        result = 0
    else:
        result = 1
        
    return result

addAttributeFromPolygons(sys.argv[1],sys.argv[3],sys.argv[2],sys.argv[4])
