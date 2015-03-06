'''
contour_post.py
Contour post processing

Simplifies lines and smooths them based on user input regarding precision
This is intended for use with DEM derived contours

Steven Porter
snowballsteve3+git@gmail.com
3/7/12
'''

import arcpy, sys

contours = sys.argv[0]
precision = sys.argv[2]
output = sys.argv[3]

from arcpy import env
env.workspace = 'C:\\Windows\\Temp'

#simplify line by removing unneeded vertices
temp = arcpy.SimplifyLine_cartography(contours,"temp",precision)

#smooth line of any sharp bends
arcpy.SmoothLine_cartography(temp,output,"PAEK",precision^2*math.pi)

#delete temp file
arcpy.Delete_managment(temp)





