# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import fmeobjects
import sys
import os
import DDSync.helpers.config_helper

def fme_runner():
    '''
    Ausführen des FME-Skripts für die Erstellung des Tasks im DataDictionary.
    '''
    
    config = DDSync.helpers.config_helper.config
    logger = config['LOGGING']['logger']
    fme_script = "CreateTaskTicket.fmw"
    
    fme_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + "\\" + fme_script
    
    parameters = {
        'database_work': str(config['GDBP']['database']),
        'pw_gpdb': str(config['GDBP']['password']),
        'User_gdbp': str(config['GDBP']['username']),
        'database_team': str(config['DD']['database']),
        'PW_geodb_dd': str(config['DD']['password']),
        'User_geodb_dd': str(config['DD']['username']),
        'OEREB_GPR': str(config['OEREB']['gpr']),
        'OEREB_DATABASE': str(config['OEREB']['database']),
        'OEREB_USERNAME': str(config['OEREB']['username']),
        'OEREB_PASSWORD': str(config['OEREB']['password'])
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
