# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import fmeobjects
import sys
import os

def fme_runner(config, gzs_objectid):
    '''
    Ausführen des FME-Skripts für die Erstellung des Tasks im DataDictionary.
    :param config: config des Geoproduktes
    :param gzs_objectid: gzs_objectid aus dem DataDictionary
    '''

    logger = config['LOGGING']['logger']
    fme_script = config['FME_SKRIPT']['scriptname']
    
    fme_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + "\\" + fme_script
    
    parameters = {
        'gzs_objectid': str(gzs_objectid)
    }
        
    runner = fmeobjects.FMEWorkspaceRunner()
    try:
        runner.runWithParameters(str(fme_path), parameters)
        pass
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgeführt werden!")
        logger.error(ex)
        sys.exit()

    logger.info("Script " +  fme_script + " ausgeführt.")
