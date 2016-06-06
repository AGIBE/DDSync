# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import codecs
from DDSync import __version__
import DDSync.Geoproduct
import DDSync.helpers.sql_helper
import DDSync.helpers.config_helper

def list_geoproducts(args):
    config = DDSync.helpers.config_helper.get_config()
    for gpr in DDSync.helpers.sql_helper.get_syncable_codes_from_gdbp(config):
        print(gpr)

def sync_geoproduct(args):
    gpr = DDSync.Geoproduct.Geoproduct(args.GEOPRODUKT)
    for sql in gpr.sql_statements:
        print(sql)

def drysync_geoproduct(args):
    gpr = DDSync.Geoproduct.Geoproduct(args.GEOPRODUKT)
    output_filename = args.SQLFILE
    with codecs.open(output_filename, "w", "utf-8") as f:
        for sql in gpr.sql_statements:
            f.write(sql + "\n")

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
    
    # SYNC-Befehl
    drysync_parser = subparsers.add_parser('drysync', help='Gibt nur die SQL-Statements aus, schreibt aber nichts ins DataDicionary.')
    drysync_parser.add_argument("GEOPRODUKT", help="Geoprodukt-Code.")
    drysync_parser.add_argument("SQLFILE", help="Output-Datei für die SQL-Statements.")
    drysync_parser.set_defaults(func=drysync_geoproduct)
    
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()