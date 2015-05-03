import arcpy

class Toolbox(object):
	def __init__(self):
		"""Define the toolbox (the name of the toolbox is the name of the
		.pyt file)."""
		self.label = "Service Downloader (ArcGis Pro)"
		self.alias = ""

		# List of tool classes associated with this toolbox
		self.tools = [Edown]


class Edown(object):
	def __init__(self):
		"""Define the tool (tool name is the name of the class)."""
		self.label = "Endpoint Downloader"
		self.description = "This tool downloads geometry from queryable ArcGis Server endpoint."
		self.canRunInBackground = False

	def getParameterInfo(self):
		"""Define parameter definitions"""
		param0 = arcpy.Parameter(
			displayName="ArcGis Server Endpoint URL",
			name="url",
			datatype="GPString",
			parameterType="Required",
			direction="Input")

		param1 = arcpy.Parameter(
			displayName="Scratch Folder",
			name="scratch",
			datatype="DEFolder",
			parameterType="Required",
			direction="Input")

		param2 = arcpy.Parameter(
			displayName="Output Geodatabase",
			name="outDB",
			datatype="DEWorkspace",
			parameterType="Required",
			direction="Input")

		param3 = arcpy.Parameter(
			displayName="Output Feature Class",
			name="outFe",
			datatype="GPString",
			parameterType="Required",
			direction="Output")

		params = [param0, param1, param2, param3]
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
		"""The source code of the tool."""
		from urllib import request
		import json
		import time
		import os

		esriServer = parameters[0].valueAsText
		scratch = parameters[1].valueAsText
		outDB = parameters[2].valueAsText
		outFe = parameters[3].valueAsText

		arcpy.env.workspace = outDB
		arcpy.env.overwriteOutput = True

		if (esriServer.endswith('/')):
			esriServer = esriServer.rstrip('/')

		start = 0

		while (start >= 0):
			time.sleep(0.5)
			url = esriServer + '/query?where=OBJECTID+>+' + str(start) + '&f=pjson&outFields=*'
			with request.urlopen(url) as f:
				content = f.read().decode('utf-8')
				out = open(scratch + '\\feDownTemp_' + str(start) + '.json', 'wb')
				out.write(content.encode('windows-1250'))
				out.close()
			
			jsn = json.load(open(scratch + '\\feDownTemp_' + str(start) + '.json'), encoding="windows-1250")
			try:
				if (jsn['exceededTransferLimit']):
					start += 1000
			except:
				start = -1

		jsons = []
		for fle in os.listdir(scratch + '\\'):
			if (fle.endswith('.json')):
				jsons.append(fle.split('.')[0])

		for jsn in jsons:
			arcpy.JSONToFeatures_conversion(scratch + '\\' + jsn + '.json', jsn)

		arcpy.Merge_management(jsons, outFe)

		for json in jsons:
			arcpy.Delete_management(json, '')
		for jsn in jsons:
			os.remove(scratch + '\\' + jsn + '.json')

		return
