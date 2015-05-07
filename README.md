#ArcGIS Scripts

Add the ArcGIS_Scripts to your toolbox in Arcmap or Arccatalog to start using the tools.

Python files are in /bin

##New - Python Toolbox
Hello everyone. I am adding new scripts as a python toolbox and will likely cease making changes to the older toolbox style

###Changelog
2015-05-07 - Added a tool that will calculate all angles of intersection between polylines for a chosen polyline error. You give it a polyline feature class, choose the unique id field, and set a snap tolerance that will be used to decide if two endpoints touch. The script is kind of slow, O(n^2).

