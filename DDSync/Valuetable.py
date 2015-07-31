# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

def process_valuetable(ezs_objectid, valuetable_list):
    '''
    Sammelt alle Informationen zu allen Wertetabellen
    einer Ebene und verarbeitet diese zu den
    notwendigen SQL-Statements. Die folgenden
    Tabellen werden damit abgefüllt:
    - TB_WERTETABELLE

    Folgende Prozessschritte werden ausgeführt:
    - valuetable_list parsen, Infos extrahieren
    - SQL-Statement generieren
    - xml parsen und DD-Felder extrahieren:
    -- TB_WERTETABELLE.WTB_OBJECTID
    -- TB_WERTETABELLE.EZS_OBJECTID
    -- TB_WERTETABELLE.WTB_BEZEICHNUNG
    -- TB_WERTETABELLE.WTB_BEZEICHNUNG_MITTEL_DE
    -- TB_WERTETABELLE.WTB_BEZEICHNUNG_MITTEL_FR
    -- TB_WERTETABELLE.WTB_IMPORTNAME
    -- TB_WERTETABELLE.WTB_JOIN_FOREIGNKEY
    -- TB_WERTETABELLE.WTB_JOIN_PRIMARYKEY
    -- TB_WERTETABELLE.WTB_JOIN_TYP
    -- TB_WERTETABELLE.WTB_AUTOLOAD (neues Feld in GeoDBmeta)
    -- TB_WERTETABELLE.IMP_OBJECTID
    
    :param ezs_objectid:
    :param valuetable_list:
    '''
    pass