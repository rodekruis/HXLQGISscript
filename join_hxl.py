##Join HXL file=name
##adm=vector
##adm_field=field adm 
##hxl_loc=longstring https://proxy.hxlstandard.org/data.csv?url=https%3A//data.humdata.org/dataset/3cb60971-0dc7-4743-a7ae-e65744b2dbba/resource/968202f1-856a-4906-ae87-c730e9b1dd27/download/PHL_haima_houses_damaged_pcoded_ndrrmc_sitrep_9_20161025.csv
#hxl_loc=longstring https://proxy.hxlstandard.org/data.json?url=https%3A//data.humdata.org/dataset/3cb60971-0dc7-4743-a7ae-e65744b2dbba/resource/968202f1-856a-4906-ae87-c730e9b1dd27/download/PHL_haima_houses_damaged_pcoded_ndrrmc_sitrep_9_20161025.csv
##hxl_field_name=string mun_code
##hxl_field_select=selection other;#mun_code;#adm2+code;#adm3+code
##do_log=boolean True

hxl_field_select_lookup = 'other;#mun_code;#adm2+code;#adm3+code'.split(';')

from qgis.core import QgsMessageLog, QgsMapLayerRegistry, QgsVectorJoinInfo
import urllib2
from PyQt4.QtCore import *
#from qgis.gui import *
from qgis.utils import iface
import time

#from shapely.geometry import Polygon, MultiPolygon
#from shapely.wkb import loads
#from shapely.wkt import dumps

def log(m):
    if do_log:
        QgsMessageLog.logMessage(str(m), 'hxl', QgsMessageLog.INFO )
        progress.setText('  '+str(m))


#TODO: unique temp file  creator
def download_file(url, fn):
    response = urllib2.urlopen(url)
    f = open(fn, 'w')
    f.write(response.read())
    f.close()
    return True

def get_input_type(hxl_loc):
    result = 'unknown'
    if 'data.csv' in hxl_loc:
        return 'csv'
    if 'data.json' in hxl_loc:
        return 'csv'
    return 'unknown'

#TODO make this more beautiful by using a csv- or hxl parser
def remove_header_lines(fn, n=1):
    fl = open(fn, 'r')
    #read in mem
    lines = []
    for line in fl:
        lines.append(line)
    fl.close()
    fl = open(fn, 'w')
    for line in lines[n:]:
        fl.write(line)
    fl.close()

def zoom_and_redraw(layer=None):
    canvas = iface.mapCanvas()
    if layer is not None:
        canvas.setExtent(layer.extent())
    canvas.refresh()



log('---------- start ----------')

geo_layer = processing.getObject(adm)
#log(geo_layer.name())
#url = processing.getObject(hxl_loc)
#log(hxl_loc)

#find hxl fieldname
if not hxl_field_select_lookup[hxl_field_select] == 'other':
    hxl_field_name = hxl_field_select_lookup[hxl_field_select]



data_type = get_input_type(hxl_loc)
log(data_type)

# download
progress.setText('Downloading data...')
temp_fn = '/home/raymond/tmp/hxl.csv'

download_succes = download_file(hxl_loc, temp_fn)
if download_succes:
    log('download succeeded')
else:
    log('download failed')

# fixing table (deleting first header line)
progress.setText('Fixing table...')
remove_header_lines(temp_fn)



# add table
progress.setText('Adding table...')

hxl_layer = iface.addVectorLayer(temp_fn, "hxl", "ogr")
log(hxl_layer.name())

#remove existing joins and joined layers
#TODO: only remove join to actual hxl file
progress.setText('Removing existing join...')
joinLayerIds = []
allJoins = geo_layer.vectorJoins()
for join in allJoins:
    log(join.joinLayerId)
    joinLayerIds.append(join.joinLayerId)
for jlid in joinLayerIds:
    log('removing join and layer: ' + jlid)
    time.sleep(.5)
    geo_layer.removeJoin(jlid)
    QgsMapLayerRegistry.instance().removeMapLayer(jlid)


#join table
progress.setText('Joining data...')
log(hxl_field_name)
time.sleep(.5)

joinInfo = QgsVectorJoinInfo()
log('--- joining ---')
log(hxl_layer.id())
log(hxl_field_name)
log(adm_field)

joinInfo.joinLayerId = hxl_layer.id()
joinInfo.joinFieldName = hxl_field_name
joinInfo.targetFieldName = adm_field

geo_layer.addJoin(joinInfo)


#update display
zoom_and_redraw(geo_layer)







