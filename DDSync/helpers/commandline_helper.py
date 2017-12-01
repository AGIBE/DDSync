# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
from DDSync import __version__
import DDSync.Geoproduct
import DDSync.helpers.sql_helper
import DDSync.helpers.config_helper
from DDSync.helpers import fme_helper

def list_geoproducts(args):
    config = DDSync.helpers.config_helper.get_config()
    syncable_gpr = []

    for gpr in DDSync.helpers.sql_helper.get_syncable_codes_from_gdbp(config):
        uuid = DDSync.helpers.sql_helper.get_uuid(config, gpr)
        if not DDSync.helpers.sql_helper.uuid_exists_in_dd(config, uuid):
            syncable_gpr.append(gpr)
            
    if len(syncable_gpr) > 0:
        for sync_gpr in syncable_gpr:
            print(sync_gpr)
    else:
        config['LOGGING']['logger'].warn("Es wurden keine Geoprodukte gefunden, die synchronisiert werden können.")
    
    return syncable_gpr

def sync_geoproduct(args):
    gpr = DDSync.Geoproduct.Geoproduct(args.GEOPRODUKT)
    gpr.write_sql_to_dd()
    # Erstellen des Tasks im DataDictionary
    fme_helper.fme_runner(gpr.config, gpr.gzs_objectid)

def syncall_geoproduct(args):
    # liste alle Geoprodukte auf
    allgp = list_geoproducts(args)
    for gp in allgp:
        gpr = DDSync.Geoproduct.Geoproduct(gp)
        gpr.write_sql_to_dd()

def drysync_geoproduct(args):
    gpr = DDSync.Geoproduct.Geoproduct(args.GEOPRODUKT)
    gpr.write_sql_to_file(args.file)

def drysyncall_geoproduct(args):
    # liste alle Geoprodukte auf
    allgp = list_geoproducts(args)
    for gp in allgp:
        gpr = DDSync.Geoproduct.Geoproduct(gp)
        gpr.write_sql_to_file(args.file)

def main():
    version_text = "DDSync v" + __version__
    parser = argparse.ArgumentParser(description="Synchronisiert ein einzelnes Geoprodukt aus GeoDBmeta in das DataDicionary der GeoDB", prog="DDSync.exe", version=version_text)
    subparsers = parser.add_subparsers(help='Folgende Befehle sind verfuegbar:')
    
    # LIST-Befehl
    list_parser = subparsers.add_parser('list', help='zeigt alle in GeoDBprozess freigegebenen Geoprodukte an.')
    list_parser.set_defaults(func=list_geoproducts)
    
    # SYNC-Befehl
    sync_parser = subparsers.add_parser('sync', help='synchronisiert das angegebene Geoprodukt in das DataDictionary.')
    sync_parser.add_argument("GEOPRODUKT", help="Geoprodukt-Code.")
    sync_parser.set_defaults(func=sync_geoproduct)
    
    # SYNCALL-Befehl
    sync_parser = subparsers.add_parser('syncall', help='synchronisiert das angegebene Geoprodukt in das DataDictionary.')
    sync_parser.set_defaults(func=syncall_geoproduct)
    
    # DRYSYNC-Befehl
    drysync_parser = subparsers.add_parser('drysync', help='Gibt nur die SQL-Statements aus, schreibt aber nichts ins DataDicionary.')
    drysync_parser.add_argument("GEOPRODUKT", help="Geoprodukt-Code.")
    drysync_parser.add_argument("-f", "--file", help="Output-Datei für die SQL-Statements.")
    drysync_parser.set_defaults(func=drysync_geoproduct)
    
    # DRYSYNCALL-Befehl
    drysync_parser = subparsers.add_parser('drysyncall', help='Gibt nur die SQL-Statements aus, schreibt aber nichts ins DataDicionary.')
    drysync_parser.add_argument("-f", "--file", help="Output-Datei für die SQL-Statements.")
    drysync_parser.set_defaults(func=drysyncall_geoproduct)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()