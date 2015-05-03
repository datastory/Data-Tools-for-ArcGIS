# Data Tools for ArcGIS 10.3 and ArcGIS Pro

The Service Geometry Downloader Tool lets you to download geometry from ArcGis Server services, which has the Query request enabled. Especially handy when you are trying to obtain data from some governmental agency saying "We give you only crappy INSPIRE WMS." Just open the WMS, get URL of obtained images, strip everything after 'MapServer' so you get something like http://agency-server.com/arcgis/rest/services/SOME/SERVICE/MapServer. That´s your endpoints URL. So happy scraping, but always remember to obey (especially copyright) law.

Data Export Tool lets you to export data in XLSX format without having Data Interoperability extension for ArcGIS.

##Instaling prerequisities for Data Export

For exporting to XLSX in ArcGIS Pro you have to install openpyxl compatibile with Pandas (version >=1.6.1 and <2.0.0).

> Simple run `C:\Python34> .\python.exe -m pip install openpyxl==1.8.6`.

For exporting to XLSX on ArcGIS 10.3 you have to install pandas 0.13.1 (compatible with preinstalled Numpy 1.7.1) and openpyxl compatibile with Pandas (version >=1.6.1 and <2.0.0). And for both of them you have to install pip and C++ compiler for Python.

> Download and install [Microsoft Visual C++ Compiler for Python 2.7](http://aka.ms/vcpython27)

> Download file [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and run it: `C:\Python27\ArcGIS10.3> .\python.exe PATH\TO\get-pip.py`

> Install Pandas by running `C:\Python27\ArcGIS10.3> .\python.exe -m pip install pandas==0.13.1`

> Install OpenPyXL by running `C:\Python27\ArcGIS10.3> .\python.exe -m pip install openpyxl==1.8.6`

This project is open under MIT License.

