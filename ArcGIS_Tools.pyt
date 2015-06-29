import math
import os

import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [LineAngles, BatchExportAndPrint, SplitLayerByAttributes]


class BatchExportAndPrint(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Batch Export and Print"
        self.description = "For a bunch of mxd's, export the map as a various output formats, or print them"
        self.canRunInBackground = False

    def param_maker(self, p_name, plabel=None, enabled=True):
        p = arcpy.Parameter(
            name=p_name
            , direction='Input'
            , datatype='GPBoolean'
            , parameterType='Optional'
            ,enabled=enabled
        )
        p.value = False
        if plabel:
            p.displayName = plabel
        else:
            p.displayName = p_name
        return p

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        params.append(
            arcpy.Parameter(
                name='map_documents'
                , displayName='Map Documents'
                , direction='Input'
                , multiValue=True
                , datatype='DEMapDocument'
            )
        )
        params.append(self.param_maker('pdf'))
        params.append(self.param_maker('merge', 'Single PDF?','false'))
        params.append(self.param_maker('jpeg'))
        params.append(self.param_maker('png'))
        params.append(self.param_maker('emf'))
        params.append(self.param_maker('ai'))

        params.append(
            arcpy.Parameter(
                name='print'
                , displayName='Print Documents'
                , direction='Input'
                , datatype='GPBoolean'
                , parameterType='Optional'
            )
        )
        printer = arcpy.Parameter(
            name='printer'
            , displayName='Select Printer'
            , direction='Input'
            , datatype='GPString'
            , parameterType='Optional'
        )
        printer.enabled = False
        printer.filter.list = arcpy.ListPrinterNames()
        params.append(printer)
        params.append(
            arcpy.Parameter(
                name='output_folder'
                , displayName='Output Folder'
                , direction='Input'
                , datatype='DEFolder'
                , parameterType='Optional'
            )
        )

        return params

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        params = {p.name: p for p in parameters}
        if params['print'].altered:
            params['printer'].enabled = params['print'].value

        if params['pdf'].altered:
            params['merge'].enabled=params['pdf'].value
        return

    def execute(self, parameters, messages):
        params = {p.name: p for p in parameters}

        mxds = params['map_documents'].value

        if params['pdf'].value and params['merge'].value:
            pdf_out = params['output_folder'].valueAsText
            if pdf_out == '': pdf_out = os.path.dirname(mxds[0])
            combinedpdf = arcpy.mapping.PDFDocumentCreate(os.path.join(pdf_out, "CombinedMaps.pdf"))

        for mxd in mxds:
            mxd_name, ext = os.path.splitext(mxd)

            map = arcpy.mapping
            map_document = map.MapDocument(mxd)

            brokenList = arcpy.mapping.ListBrokenDataSources(map_document)
            if brokenList:
                errorString = mxd + " has broken data sources on layer(s): "
            for item in brokenList:
                errorString = errorString + "'" + item.name + "'"
            arcpy.AddWarning(errorString)

            output_folder = params['output_folder'].valueAsText
            if output_folder == '':
                output_folder = os.path.dirname(mxd)

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

            # perform selected operations
            if params['pdf'].value:
                arcpy.AddMessage("Exporting: " + mxd + " as PDF")
                out_pdf = os.path.join(output_folder, mxd_name + ".pdf")
                map.ExportToPDF(map_document, out_pdf, data_frame, 640, 480, resolution, image_quality, colorspace,
                                compress_vectors, image_compression, picture_symbol, convert_markers, embed_fonts,
                                layers_attributes, georef_info)
                if params['merge'].value:
                    combinedpdf.appendPages(out_pdf)

            if params['jpeg'].value:
                arcpy.AddMessage("Exporting: " + mxd + " as JPEG")
                out_jpg = os.path.join(output_folder, mxd_name + ".jpg")
                map.ExportToJPEG(map_document, out_jpg)

            if params['png'].value:
                arcpy.AddMessage("Exporting: " + mxd + " as PNG")
                out_png = os.path.join(output_folder, mxd_name + ".png")
                map.ExportToPNG(map_document, out_png, data_frame, 640, 480, resolution)

            if params['emf'].value:
                arcpy.AddMessage("Exporting: " + mxd + " as EMF")
                out_emf = os.path.join(output_folder, mxd_name + ".emf")
                map.ExportToEMF(map_document, out_emf, data_frame, 640, 480, resolution, image_quality, "#",
                                picture_symbol,
                                convert_markers)

            if params['ai'].value:
                arcpy.AddMessage("Exporting: " + mxd + " as AI")
                out_AI = os.path.join(output_folder, mxd_name + ".ai")
                map.ExportToAI(map_document, out_AI)

            if params['print'].value:
                arcpy.AddMessage("Printing: " + mxd)
                map.PrintMap(map_document, params['printer'].valueAsText)

            del map

            if params['pdf'].value and params['merge'].value:
                combinedpdf.saveAndClose()
                del combinedpdf


class LineAngles(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Angles Between Lines"
        self.description = "For all intersecting lines, will produce an output table of the angle between them."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        input = arcpy.Parameter(
            name='input_lines'
            , displayName='Input Polylines'
            , direction='Input'
            , datatype='GPLayer'
        )
        params.append(input)
        id = arcpy.Parameter(
            name='id'
            , displayName='Unique ID Field'
            , direction='Input'
            , datatype='Field'
        )
        id.parameterDependencies = [input.name]
        params.append(id)
        params.append(
            arcpy.Parameter(
                name='threshold'
                , displayName='Snap Tolerance'
                , direction='Input'
                , datatype='GPDouble'
            )
        )
        params.append(
            arcpy.Parameter(
                name='output_path'
                , displayName='Output Features'
                , direction='Output'
                , datatype='DEFeatureClass'
            )
        )
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def magnitude(self, v):
        return math.sqrt((v[0][0] - v[1][0]) ** 2 + (v[0][1] - v[1][1]) ** 2)

    def execute(self, parameters, messages):
        """The source code of the tool."""
        params = {p.name: p for p in parameters}

        # input parameters
        line_path = params['input_lines'].valueAsText
        out_path = params['output_path'].valueAsText
        fid = params['id'].valueAsText
        threshold = float(params['threshold'].valueAsText)

        # create the output feature class
        out_data = arcpy.CreateFeatureclass_management(os.path.dirname(os.path.abspath(out_path)),
                                                       os.path.basename(out_path), 'POINT',
                                                       spatial_reference=arcpy.Describe(line_path).spatialReference)
        arcpy.AddField_management(out_data, 'fid1', 'LONG')
        arcpy.AddField_management(out_data, 'fid2', 'LONG')
        arcpy.AddField_management(out_data, 'angle', 'FLOAT')

        #open an insert cursor so we can write data to the output
        out_cur = arcpy.InsertCursor(out_data)

        #create the progress bar
        n = sum([1 for x in arcpy.SearchCursor(line_path)])
        step = 1
        while 10 ** step < n:
            step = step + 1
        step = 10 ** (step - 2)
        if step < 1: step = 1
        arcpy.SetProgressor('step', 'Processing Polylines', 0, n, step)

        #nested loop, looking for a faster way
        count = 0

        for row1 in arcpy.SearchCursor(line_path):
            #step progress bar
            count += 1
            if count % step == 0:
                arcpy.SetProgressorPosition()

            for row2 in arcpy.SearchCursor(line_path):

                #we only want to compare differen rows that are within the threshold and are single part geometries
                if row1.getValue(fid) != row2.getValue(fid) and row1.SHAPE.distanceTo(
                        row2.SHAPE) < threshold and not row1.SHAPE.isMultipart and not row2.SHAPE.isMultipart:

                    #get all the points as point geometries
                    shape1_first = arcpy.PointGeometry(row1.SHAPE.firstPoint)
                    shape1_last = arcpy.PointGeometry(row1.SHAPE.lastPoint)
                    shape2_first = arcpy.PointGeometry(row2.SHAPE.firstPoint)
                    shape2_last = arcpy.PointGeometry(row2.SHAPE.lastPoint)
                    touches = False  #flag for if we have lines that touch

                    '''
                    notation below: vertex is the average of the coincident endpoints that touch each other
                    a is the first vertex away from the coincident endpoint of line 1
                    b is the first vertex away from the coincident endpiont of line 2

                    v_a is the vector from vertex to a
                    v_b is the vector from vertex to b
                    a_b is the vector from a to b

                    angle between v_a and v_b is determined using law of cosines, there are other ways but I had this off the top of my head
                    '''

                    #first endpoints touch
                    if shape1_first.distanceTo(shape2_first) < threshold:
                        vertex = ((shape1_first.firstPoint.X + shape2_first.firstPoint.X) / 2.0,
                                  (shape1_first.firstPoint.Y + shape2_first.firstPoint.Y) / 2.0)
                        a = row1.SHAPE.getPart(0).getObject(1)
                        b = row2.SHAPE.getPart(0).getObject(1)
                        touches = True

                    #last to first touch
                    if shape1_last.distanceTo(shape2_first) < threshold:
                        vertex = ((shape1_last.firstPoint.X + shape2_first.firstPoint.X) / 2.0,
                                  (shape1_last.firstPoint.Y + shape2_first.firstPoint.Y) / 2.0)
                        a = row1.SHAPE.getPart(0).getObject(row1.SHAPE.getPart(0).count - 2)
                        b = row2.SHAPE.getPart(0).getObject(1)
                        touches = True

                    #first to last touch
                    if shape1_first.distanceTo(shape2_last) < threshold:
                        vertex = ((shape1_first.firstPoint.X + shape2_last.firstPoint.X) / 2.0,
                                  (shape1_first.firstPoint.Y + shape2_last.firstPoint.Y) / 2.0)
                        a = row1.SHAPE.getPart(0).getObject(1)
                        b = row2.SHAPE.getPart(0).getObject(row2.SHAPE.getPart(0).count - 2)
                        touches = True

                    #last to last touch
                    if shape1_last.distanceTo(shape2_last) < threshold:
                        vertex = ((shape1_last.firstPoint.X + shape2_last.firstPoint.X) / 2.0,
                                  (shape1_last.firstPoint.Y + shape2_last.firstPoint.Y) / 2.0)
                        a = row1.SHAPE.getPart(0).getObject(row1.SHAPE.getPart(0).count - 2)
                        b = row2.SHAPE.getPart(0).getObject(row2.SHAPE.getPart(0).count - 2)
                        touches = True

                    #if any touched
                    if (touches):
                        #creating vectors
                        v_a = (vertex, (a.X, a.Y))
                        v_b = (vertex, (b.X, b.Y))
                        a_b = ((a.X, a.Y), (b.X, b.Y))
                        m_ab = self.magnitude(a_b)
                        m_va = self.magnitude(v_a)
                        m_vb = self.magnitude(v_b)
                        if m_va > 0 and m_vb > 0 and m_ab > 0:
                            #solving for angle using law of cosines
                            l = (m_ab ** 2 - m_va ** 2 - m_vb ** 2) / (-2 * m_va * m_vb)
                            #control for math domain issues, this seems to happen when lines are exactly 180 degrees apart
                            if l <= 1 and l >= -1:
                                angle = math.acos(l) * 180 / math.pi
                            else:
                                angle = -1
                        else:
                            angle = -1
                        #creating the output row and writing data to output feature class
                        out_row = out_cur.newRow()
                        out_row.setValue('fid1', row1.getValue(fid))
                        out_row.setValue('fid2', row2.getValue(fid))
                        out_row.setValue('angle', angle)
                        out_row.setValue('SHAPE', arcpy.Point(vertex[0], vertex[1]))
                        out_cur.insertRow(out_row)

        return

class SplitLayerByAttributes(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Angles Between Lines"
        self.description = "For all intersecting lines, will produce an output table of the angle between them."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        input = arcpy.Parameter(
            name='input_layer'
            , displayName='Input Layer'
            , direction='Input'
            , datatype='GPLayer'
        )
        params.append(input)
        attribute = arcpy.Parameter(
            name='attribute'
            , displayName='Attribute'
            , direction='Input'
            , datatype='Field'
        )
        attribute.parameterDependencies = [input.name]
        params.append(attribute)
        params.append(
            arcpy.Parameter(
                name='output_path'
                , displayName='Output Folder'
                , direction='Input'
                , datatype='DEFolder'
            )
        )
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        params = {p.name: p for p in parameters}
        unique_values = [row.getValue(params['attribue']) for row in arcpy.SearchCursor(params['input_layer'])]
        for v in unique_values:
            selection = arcpy.SelectLayerByAttribute_management(params['input_layer'],'NEW_SELECTION','%s = %s' %(params['attribue'],v))
            out_shapefile = os.path.join(params['output_path'],v.replace(' ','_'))
            arcpy.CopyFeatures_management(selection,out_shapefile)

