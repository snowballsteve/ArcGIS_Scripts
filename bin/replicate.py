'''Replicates a feature class's data to another with identical schema
replicate.py -h for usage

Steven C. Porter
2013.8.21
'''

import arcpy
import argparse

def getFieldNames(layer):
	''' Returns a set of field names that exist in the layer'''
	return set([field.name for field in arcpy.ListFields(layer)])
	
if __name__=="__main__":
	parser = argparse.ArgumentParser(description='Replicate data from one feature class to another')
	parser.add_argument('source', metavar='source', type=str, nargs='+', help='Source layer whose data will be replcated to destination.')
	parser.add_argument('destination', metavar='destination', type=str, nargs='+', help='Destination layer whose records will be deleted and replaced with those from source layer.')

	args = parser.parse_args()
	source = ''.join(args.source)
	destination = ''.join(args.destination)
	
	if getFieldNames(source)!=getFieldNames(destination):
		arcpy.AddError("Schemas are not the same, exiting")
	else:
		arcpy.DeleteFeatures_management(destination)
		arcpy.Append_management(source,destination,"TEST","","")


