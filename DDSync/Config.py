# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import configobj

'''
Folgende Konfigurationsinformationen werden hier
definiert oder von hier aus geholt:
- Connection-String MySQL
- Connection-String Oracle (DataDictionary)
- Connection-String Oracle (GeoDBProzess)
- XML-Namespaces
- XPath-Angaben (inkl. DD-Name)
- Logging (Logfile und farbigen Stream)
'''
config_filename = r"D:\\Daten\\repos\\DDSync\\config.ini"
config = configobj.ConfigObj(config_filename, encoding="UTF-8")