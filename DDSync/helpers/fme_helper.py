# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import fmeobjects
import sys
import os
import DDSync.helpers.config_helper
import DDSync.helpers.sql_helper

def fme_runner(logger):
    '''
    Ausführen des FME-Skripts für die Erstellung des Tasks im DataDictionary.
    '''
    
    config = DDSync.helpers.config_helper.config
    logger = logger
    fme_script = "CreateTaskTicket.fmw"

    oereb_gpr_sql = "select 1 as id, string_agg(oereb.workflow_gpr.gprcode , ',' order by oereb.workflow_gpr.gprcode) as gprcode from oereb.workflow_gpr group by 1"

    oereb_gpr_result = DDSync.helpers.sql_helper.readPostgreSQL(config['POSTGRESQL']['connection_string'], oereb_gpr_sql)
    oereb_gpr = oereb_gpr_result[0][1]
    
    fme_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..')) + "\\" + fme_script
    
    parameters = {
        'database_work': str(config['GDBP']['database']),
        'pw_gpdb': str(config['GDBP']['password']),
        'User_gdbp': str(config['GDBP']['username']),
        'database_team': str(config['DD']['database']),
        'PW_geodb_dd': str(config['DD']['password']),
        'User_geodb_dd': str(config['DD']['username']),
        'OEREB_GPR': str(oereb_gpr),
        'OEREB_DATABASE': str(config['POSTGRESQL']['database']),
        'OEREB_USERNAME': str(config['POSTGRESQL']['username']),
        'OEREB_PASSWORD': str(config['POSTGRESQL']['password']),
        'OEREB_PORT': str(config['POSTGRESQL']['port']),
        'OEREB_HOST': str(config['POSTGRESQL']['host']),
    }
        
    runner = fmeobjects.FMEWorkspaceRunner()

    try:
        runner.runWithParameters(str(fme_path), parameters)
        pass
    except fmeobjects.FMEException as ex:
        logger.error("FME-Workbench " + fme_script + " konnte nicht ausgefuehrt werden!")
        logger.error(ex)
        sys.exit()

    logger.info("Script " +  fme_script + " ausgefuehrt.")
