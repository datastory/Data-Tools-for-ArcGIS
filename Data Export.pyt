import arcpy
import pandas as pd

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Data Export"
        self.alias = "data_export"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "To XLSX"
        self.description = "Tool export table or FeatureLayer data table to XLSX format of Microsoft Excel."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        dataSet = arcpy.Parameter(
            displayName = "Input Feature Layer or Table",
            name = "dataSet",
            datatype = "Layer",
            parameterType = "Required",
            direction = "Input")

        outFile = arcpy.Parameter(
            displayName = "Output file",
            name = "outFile",
            datatype = "File",
            parameterType = "Required",
            direction = "Output")

        parameters = [dataSet, outFile]

        return parameters

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

        dataSet = parameters[0].value
        outFile = str(parameters[1].value)

        if (len(arcpy.ListFields(dataSet)) > 16384):
            arcpy.AddMessage('Your table has more than 16384 columns, which is MS Excel maximum.')
            quit()

        # Comented because of error in arcpy on ArcGIS Pro 1.0.0
        #if (int(arcpy.GetCount_management(dataSet).getOutput(0)) > 1048576):
        #    print('Your table has more than 1048576 rows, which is MS Excel maximum.')
        #    quit()

        nullValues = {"Double": -999.0, "Integer": -999, "Single": -999, "SmallInteger": -999, "String": ""}
        nulls = {}

        fields = []

        for field in arcpy.ListFields(dataSet):
            if field.type in nullValues:
                fields.append(str(field.name))
                nulls[str(field.name)] = nullValues[str(field.type)]

        # numpy array to Pandas DataFrame
        outArray = arcpy.da.TableToNumPyArray(dataSet, fields, null_value=nulls)
        out = pd.DataFrame(outArray)

        # exports dataframe to xlsx
        out.to_excel(outFile.split('.')[0] + '.xlsx')
        return
