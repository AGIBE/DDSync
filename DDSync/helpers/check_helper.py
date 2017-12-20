# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import arcpy

def run_checkscript_normierung(config, code, jahr, version):
    logger = config['LOGGING']['logger']
    toolbox = config['CHECKSCRIPT_NORMIERUNG']['toolbox']
    
    arcpy.ImportToolbox(toolbox)
    result = arcpy.CheckGeoproduct_tatata(Geoprodukt=code,Jahr=jahr,Version=version,Pruefe_GeoDBProzess="true",Pruefe_Filesystem="true",Pruefe_GeoDBmeta="true",Pruefe_Geodaten="true",Pruefe_GeoDBmeta_DD="false")

    if unicode(result[0]) == "true":
        status_checkscript_normierung = True
    else:
        status_checkscript_normierung = False
        
    arcpy.RemoveToolbox(toolbox)
                        
    return status_checkscript_normierung