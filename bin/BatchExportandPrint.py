"""
Batch Export and Print
  This script takes MXD files
  and exports all the maps as selected

  @author Steven Porter
  @contact: porters1@ohio.edu
  @organization: The Voinovich School for Leadership and Public Affairs, Ohio University
  @version 1/20/11
"""

import arcpy, sys, os

#Input variables. Remember arcgis passes lists as semicolon delimited strings (files)
files= sys.argv[1]
yesPDF = sys.argv[2]
yesJPG = sys.argv[3]
yesPNG = sys.argv[4]
yesEMF = sys.argv[5]
yesAI = sys.argv[6]
yesPRINT = sys.argv[7]
printer = sys.argv[8] #relies on code to generate a list in the tool itself
outputFolder = sys.argv[9]
mergePDF = sys.argv[10]

#if outputFolder is empty use mxd location
if outputFolder=="#":
	outputFolder = os.path.dirname(files.split(";")[0])

if yesPDF=="true" and mergePDF =="true":
		combinedpdf = arcpy.mapping.PDFDocumentCreate(outputFolder + os.sep + "CombinedMaps.pdf")

#loop through each passed mxd file split the string back into the list
for file in files.split(";"):
	file=file.strip("'")
	
	
	#parse out the file name of the file 
	filename = os.path.basename(file)
	
	#get the name of file without any file extension
	mxd_name = filename.split(".")[0]
	#create a map object from the file
	map = arcpy.mapping
	map_document = map.MapDocument(file)	
	
	#Check for broken data sources
	brokenList = arcpy.mapping.ListBrokenDataSources(map_document)
	if brokenList:
		errorString = filename+" has broken data sources on layer(s): "
		for item in brokenList:
			errorString = errorString + "'"+item.name+"'"
		arcpy.AddError(errorString)
		
	# Set all the parameters as variables here:
	data_frame = 'PAGE_LAYOUT'
	resolution = "300"
	image_quality = "NORMAL"
	colorspace = "RGB"
	compress_vectors = "True"
	image_compression = "DEFLATE"
	picture_symbol = 'RASTERIZE_BITMAP'
	convert_markers = "TRUE"
	embed_fonts = "True"
	layers_attributes = "NONE"
	georef_info = "False"

	
		
	#perform selected operations
	if yesPDF=="true":
		arcpy.AddMessage("Exporting: "+ filename+" as PDF")
		out_pdf = outputFolder + os.sep + mxd_name+ ".pdf"
		map.ExportToPDF(map_document, out_pdf, data_frame, 640, 480, resolution, image_quality, colorspace, compress_vectors, image_compression, picture_symbol, convert_markers, embed_fonts, layers_attributes, georef_info)
		if mergePDF =="true":
			combinedpdf.appendPages(out_pdf)
			
	if yesJPG=="true":
		arcpy.AddMessage("Exporting: "+ filename+" as JPEG")
		out_jpg = outputFolder + os.sep + mxd_name+ ".jpg"
		map.ExportToJPEG(map_document, out_jpg)
		
	if yesPNG=="true":
		arcpy.AddMessage("Exporting: "+ filename+" as PNG")
		out_png = outputFolder + os.sep + mxd_name+ ".png"
		map.ExportToPNG(map_document, out_png, data_frame, 640, 480, resolution)
		
	if yesEMF=="true":
		arcpy.AddMessage("Exporting: "+ filename+" as EMF")
		out_emf= outputFolder + os.sep + mxd_name+ ".emf"
		map.ExportToEMF(map_document, out_emf, data_frame, 640, 480, resolution, image_quality, "#", picture_symbol, convert_markers)
		
	if yesAI=="true":
		arcpy.AddMessage("Exporting: "+ filename+" as AI")
		out_AI= outputFolder + os.sep + mxd_name+ ".ai"
		map.ExportToAI(map_document, out_AI)
		
	if yesPRINT=="true":
		arcpy.AddMessage("Printing: "+filename)
		map.PrintMap(map_document, printer)
		

	del map #delete the map opject

if yesPDF=="true" and mergePDF =="true":
		combinedpdf.saveAndClose()
		del combinedpdf
# This gives feedback in the script tool dialog

arcpy.GetMessages()
