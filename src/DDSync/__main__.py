# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import sys
from DDSync import __version__
import DDSync.Geoproduct
import DDSync.helpers.sql_helper
import DDSync.helpers.config_helper
from DDSync.helpers import fme_helper
import AGILib.agilogger as al


def list_geoproducts(args):
    config = DDSync.helpers.config_helper.config
    syncable_gpr = []

    for gpr in DDSync.helpers.sql_helper.get_syncable_codes_from_gdbp(config, args.nextwippe):
        uuid = DDSync.helpers.sql_helper.get_uuid(config, gpr)
        if not DDSync.helpers.sql_helper.uuid_exists_in_dd(config, uuid):
            syncable_gpr.append(gpr)
            
    if len(syncable_gpr) > 0:
        for sync_gpr in syncable_gpr:
            print(sync_gpr)
    else:
        print("Es wurden keine Geoprodukte gefunden, die synchronisiert werden koennen.")
    
    return syncable_gpr

def sync_geoproduct(args):
    config = DDSync.helpers.config_helper.config
    log_dir = config['LOGGING']['basedir']
    logfile_name = 'DDSync.log'
    logger = al.initialize_agilogger(
        logfile_name=logfile_name,
        logfile_folder=log_dir,
        list_log_handler=['file', 'stream'],
        archive=True,
        logger_name='AGILogger'
    )
    logger.info('Folgendes GP wird synchronisiert: {}'.format(args.GEOPRODUKT))
    gpr = DDSync.Geoproduct.Geoproduct(args.GEOPRODUKT, args.check, args.nextwippe, logger)
    gpr.write_sql_to_dd()
    # Erstellen des Tasks im DataDictionary
    fme_helper.fme_runner(logger)
    # Ausgabe für SyncServ
    logger.info('SUCCESSFUL')
    al.destroy_agilogger()
    print("SUCCESSFUL")
    sys.exit(0)

def syncall_geoproduct(args):
    # liste alle Geoprodukte auf
    allgp = list_geoproducts(args)
    cnt = 0
    config = DDSync.helpers.config_helper.config
    nextwippe = args.nextwippe

    log_dir = config['LOGGING']['basedir']
    logfile_name = 'DDSync.log'
    logger = al.initialize_agilogger(
        logfile_name=logfile_name,
        logfile_folder=log_dir,
        list_log_handler=['file', 'stream'],
        archive=True,
        logger_name='AGILogger'
    )
    logger.info('Folgende GP werden synchronisiert: {}'.format(allgp))
    for gp in allgp:
        try:
            gpr = DDSync.Geoproduct.Geoproduct(gp, True, nextwippe, logger)
            gpr.write_sql_to_dd()
            logger.info("Erfolgreich synchronisiert. " + gp)
            cnt += 1
        except Exception as e:
            logger.warn("Konnte nicht synchronisiert werden. " + gp)
            logger.warn(e)
            continue
    # Usecase Korrektur abfangen
    corr_gprs = DDSync.helpers.sql_helper.set_status_gp_usecase_correction(config, nextwippe)
    for gpr in corr_gprs:
        logger.info("Usecase Korrektur: Status von " + gpr + " wurde im DD wieder auf 1 gesetzt.")
    # Erstellen des Tasks im DataDictionary
    fme_helper.fme_runner(logger)
    logger.info('Von ' + str(len(allgp)) + ' Geoprodukten wurden ' + str(cnt) + ' erfolgreich synchronisiert.')
    # Ausgabe für SyncServ
    logger.info('SUCCESSFUL')
    al.destroy_agilogger()
    print("SUCCESSFUL")
    sys.exit(0)

def drysync_geoproduct(args):
    config = DDSync.helpers.config_helper.config
    log_dir = config['LOGGING']['basedir']
    logfile_name = 'DDSync.log'
    logger = al.initialize_agilogger(
        logfile_name=logfile_name,
        logfile_folder=log_dir,
        list_log_handler=['file', 'stream'],
        archive=True,
        logger_name='AGILogger'
    )
    gpr = DDSync.Geoproduct.Geoproduct(args.GEOPRODUKT, True, False, logger)
    gpr.write_sql_to_file(args.file)

def drysyncall_geoproduct(args):
    # liste alle Geoprodukte auf
    allgp = list_geoproducts(args)
    config = DDSync.helpers.config_helper.config
    log_dir = config['LOGGING']['basedir']
    logfile_name = 'DDSync.log'
    logger = al.initialize_agilogger(
        logfile_name=logfile_name,
        logfile_folder=log_dir,
        list_log_handler=['file', 'stream'],
        archive=True,
        logger_name='AGILogger'
    )
    for gp in allgp:
        try:
            gpr = DDSync.Geoproduct.Geoproduct(gp, True, True, logger)
            gpr.write_sql_to_file(args.file)
            logger.info("Erfolgreich in SQL-File geschrieben. " + gp)
        except Exception as e:
            logger.warn("Konnte nicht in SQL-File geschrieben werden. " + gp)
            logger.warn(e)
            continue

def main():
    version_text = "DDSync v" + __version__
    parser = argparse.ArgumentParser(description="Synchronisiert ein einzelnes Geoprodukt aus GeoDBmeta in das DataDicionary der GeoDB", prog="DDSync.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # LIST-Befehl
    list_parser = subparsers.add_parser('list', help='zeigt alle in GeoDBprozess freigegebenen Geoprodukte an.')
    list_parser.add_argument("-w", "--nextwippe", default=True, help="Soll geprüft werden, ob GP auf der nächsten Wippe ist? Default: True")
    list_parser.set_defaults(func=list_geoproducts)
    
    # SYNC-Befehl
    sync_parser = subparsers.add_parser('sync', help='synchronisiert das angegebene Geoprodukt in das DataDictionary.')
    sync_parser.add_argument("GEOPRODUKT", help="Geoprodukt-Code.")
    sync_parser.add_argument("-c", "--check", default=True, help="Soll Checkskript Normierung ausgeführt werden? Default: True")
    sync_parser.add_argument("-w", "--nextwippe", default=True, help="Soll geprüft werden, ob GP auf der nächsten Wippe ist? Default: True")
    sync_parser.set_defaults(func=sync_geoproduct)
    
    # SYNCALL-Befehl
    syncall_parser = subparsers.add_parser('syncall', help='synchronisiert das angegebene Geoprodukt in das DataDictionary.')
    syncall_parser.add_argument("-w", "--nextwippe", default=True, help="Soll geprüft werden, ob GP auf der nächsten Wippe ist? Default: True")
    syncall_parser.set_defaults(func=syncall_geoproduct)
    
    # DRYSYNC-Befehl
    drysync_parser = subparsers.add_parser('drysync', help='Gibt nur die SQL-Statements aus, schreibt aber nichts ins DataDicionary.')
    drysync_parser.add_argument("GEOPRODUKT", help="Geoprodukt-Code.")
    drysync_parser.add_argument("-f", "--file", help="Output-Datei für die SQL-Statements.")
    drysync_parser.add_argument("-c", "--check", default=True, help="Soll Checkskript Normierung ausgeführt werden? Default: True")
    drysync_parser.add_argument("-w", "--nextwippe", default=True, help="Soll geprüft werden, ob GP auf der nächsten Wippe ist? Default: True")
    drysync_parser.set_defaults(func=drysync_geoproduct)
    
    # DRYSYNCALL-Befehl
    drysyncall_parser = subparsers.add_parser('drysyncall', help='Gibt nur die SQL-Statements aus, schreibt aber nichts ins DataDicionary.')
    drysyncall_parser.add_argument("-f", "--file", help="Output-Datei für die SQL-Statements.")
    drysyncall_parser.add_argument("-w", "--nextwippe", default=True, help="Soll geprüft werden, ob GP auf der nächsten Wippe ist? Default: True")
    drysyncall_parser.set_defaults(func=drysyncall_geoproduct)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()