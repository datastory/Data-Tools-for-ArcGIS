ARCGIS=False
try:
    import arcpy
    ARCGIS=True
except:
    ARCGIS=False

import os
from osgeo import ogr
from osgeo import osr
import shutil
import tempfile
import logging

class Toolbox(object):
    """Some nasty ArcGIS class
    """
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Service Downloader"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Edown]

def _get_first_source_dataset(folder):
    """
    :return: osgeo.ogr.DataSource
    """

    first_source_file = os.listdir(folder)[0]
    first_source_ds = ogr.Open(os.path.join(folder, first_source_file))
    return first_source_ds

def transform(infile, output, insrs):
    """Transform input file to output target file, based on input coordinate
    reference system to WGS84

    :param infile: name of the input file
    :param output: name of the output file
    :param insrs: epsg code of input file
    """

    logging.info('Transforming %s from %s to %s' % (infile, insrs, output)) 
    in_srs = osr.SpatialReference()
    in_srs.ImportFromEPSG(insrs)
    out_srs = osr.SpatialReference()
    out_srs.ImportFromEPSG(4324)
    coordTrans = osr.CoordinateTransformation(in_srs, out_srs)

    in_dsn = ogr.Open(infile)
    in_layer = in_dsn.GetLayer()
    in_feature_definition = in_layer.GetLayerDefn()

    out_driver = ogr.GetDriverByName('GeoJSON')
    out_dsn = out_driver.CreateDataSource(output)
    out_layer = out_dsn.CreateLayer(in_layer.GetName(),
            geom_type=in_layer.GetGeomType())

    # add fields
    for i in range(0, in_feature_definition.GetFieldCount()):
        fieldDefn = in_feature_definition.GetFieldDefn(i)
        out_layer.CreateField(fieldDefn)

    # get the output layer's feature definition
    out_feature_definition = out_layer.GetLayerDefn()

    # loop through the input features
    inFeature = in_layer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef().Clone()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(out_feature_definition)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, out_feature_definition.GetFieldCount()):
            outFeature.SetField(out_feature_definition.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        out_layer.CreateFeature(outFeature)
        # destroy the features and get the next input feature
        outFeature.Destroy()
        inFeature.Destroy()
        inFeature = in_layer.GetNextFeature()

    # close the shapefiles
    in_dsn.Destroy()
    out_dsn.Destroy()


def join_files(folder):
    """
    Merge all files in given folder into one datasource

    :param folder: name of temporary folder to be joined
    :return: resulting joined files file name
    """

    first_ds = _get_first_source_dataset(folder)
    first_layer = first_ds.GetLayer(0)

    drv = ogr.GetDriverByName('GeoJSON')
    tmpfile = tempfile.mktemp(suffix=".json")
    out_dsn = drv.CreateDataSource(tmpfile)
    out_layer = out_dsn.CopyLayer(first_layer, new_name=first_layer.GetName())

    for source in os.listdir(folder)[1:]:
        logging.info('Joining file %s to %s' % (source, tmpfile)) 
        dsn = ogr.Open(os.path.join(folder, source))
        layer = dsn.GetLayer()
        nfeatures = layer.GetFeatureCount()

        for i in range(nfeatures):
            feature = layer.GetNextFeature()
            out_layer.CreateFeature(feature.Clone())

    out_dsn.Destroy()

    return tmpfile

def download_data(url, encoding):
    """
    Download data to folder
    
    :param url: url of the service
    :param encoding: input data encoding
    :return: folder with downloaded data
    """

    import urllib2
    import json
    import time

    folder = tempfile.mkdtemp('arcgis-scratch')

    if (url.endswith('/')):
            url = url.rstrip('/')

    start = 0

    while (start >= 0):
            time.sleep(0.5)
            scratchurl = url + '/query?where=OBJECTID+>+' + str(start) + '&f=pjson&outFields=*'
            f = urllib2.urlopen(scratchurl)
            content = f.read().decode('utf-8')
            output_name = os.path.join(folder, str(start) + '.json')
            logging.info('Downloading scratch %s' % output_name) 
            out = open(output_name, 'wb')
            out.write(content.encode(encoding))
            out.close()
            
            jsn = json.load(open(os.path.join(folder, str(start) + '.json'), "r"),
                            encoding=encoding)
            try:
                    if (jsn['exceededTransferLimit']):
                            start += 1000
            except:
                    start = -1

    return folder

def download(url, output, encoding, insrs):
    """Download and store given data

    :param url: url of the service
    :param output: name of output file
    :param encoding: encoding of input data
    :param insrs: input source reference system
    """

    folder = download_data(url, encoding)
    joined_file = join_files(folder)
    transform(joined_file, output, insrs)

    shutil.rmtree(folder)
    #os.remove(joined_file)
    print joined_file

    if not os.path.isfile(output):
        raise Error("Output file not created, the whole process failed")
    else:
        logging.info("File %s successfuly created" % output)
    

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Download data via ESRI ArcGIS Rest  API')

    parser.add_argument('--url', 
                        help='URL of the service', required=True)

    parser.add_argument('--output',
                       help='output file name', required=True)

    parser.add_argument('--encoding', default='utf-8',
                       help='encoding of input data, default "utf-8"')

    parser.add_argument('--srs', default='5514',
                       help='coordinate reference system code of input data, default "5514"')

    parser.add_argument('--overwrite', action='store_true',
                       help='output file name')

    parser.add_argument('--verbose', action='store_true',
                       help='verbose output')

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if os.path.exists(args.output):
        logging.warning('Output file %s already exists and will be overwritten' % args.output)
        if args.overwrite:
            os.remove(args.output)
            logging.info('Output file %s removed' % args.output)
        else:
            raise IOError("File already exists, try --overwrite")

    download(
            args.url,
            args.output,
            args.encoding,
            int(args.srs))

if __name__ == '__main__':
    main()


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
		import urllib2
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
			f = urllib2.urlopen(url)
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

		for jsn in jsons:
			arcpy.Delete_management(jsn, '')
		for jsn in jsons:
			os.remove(scratch + '\\' + jsn + '.json')

		mxd = arcpy.mapping.MapDocument('CURRENT')
		df = arcpy.mapping.ListDataFrames(mxd)[0]
		layer = arcpy.mapping.Layer(outFe)
		arcpy.mapping.AddLayer(df, layer, 'TOP')
		del mxd

		return
