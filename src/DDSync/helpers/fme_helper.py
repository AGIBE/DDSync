# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import AGILib.fme
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
    fme_script_logfile = os.path.join(config['LOGGING']['basedir'], "CreateTaskTicket_fme.log")

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

    logger.info("Script " + fme_path + " wird ausgeführt.")
    logger.info("Das FME-Logfile heisst: " + fme_script_logfile)

    fme_runner = AGILib.FMERunner(fme_workbench=fme_script, fme_workbench_parameters=parameters, fme_logfile=fme_script_logfile, fme_logfile_archive=True)
    fme_runner.run()         
    if fme_runner.returncode != 0:
        logger.error("FME-Script %s abgebrochen." % (fme_script))
        raise RuntimeError("FME-Script %s abgebrochen." % (fme_script))
        sys.exit()

    logger.info("Script " +  fme_script + " ausgefuehrt.")