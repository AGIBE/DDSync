# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import arcpy

def run_checkscript_normierung(config, code, jahr, version):
    status_checkscript_normierung = True
    
    logger = config['LOGGING']['logger']
    toolbox = config['CHECKSCRIPT_NORMIERUNG']['toolbox']
    
    arcpy.ImportToolbox(toolbox)
    logger.info("Führe das Checkscript Normierung aus für:")
    logger.info("Geoprodukt: " + code)
    logger.info("Jahr: " + unicode(jahr))
    logger.info("Version: " + unicode(version))
#     result = arcpy.CheckskriptNormierung(code, jahr, version, "true", "true", "true", "true")
#     
#     if unicode(result[0]) == "true":
#         status_checkscript_normierung = True
        
    return status_checkscript_normierung