# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.DDSync

import argparse

def main():
    '''
    -s --show-geoproducts: liste alle synchronisierbaren Geoprodukte auf
    -r --run-geoproduct CODE: synchronisiere das Geoprodukt CODE
    -d --dry-run: gib nur die SQL-Statements aus, schreibe nichts in die DB
    -v --version: gib die aktuelle Version aus
    -h --help: zeige die Hilfe an
    '''
    DDSync.DDSync.sync_geoproduct("DIPANU")

if __name__ == '__main__':
    main()