# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

def process_legend(ezs_objectid, legend_list):
    '''
    Sammelt alle Informationen zu allen Legenden
    einer Ebene und verarbeitet diese zu den
    notwendigen SQL-Statements. Die folgenden
    Tabellen werden damit abgefüllt:
    - TB_LEGENDE

    Folgende Prozessschritte werden ausgeführt:
    - legend_list parsen, Infos extrahieren
    - SQL-Statement generieren
    - xml parsen und DD-Felder extrahieren:
    -- TB_LEGENDE.LEG_OBJECTID
    -- TB_LEGENDE.EZS_OBJECTID
    -- TB_LEGENDE.SPR_OBJECTID
    -- TB_LEGENDE.LEG_BEZEICHNUNG
    -- TB_LEGENDE.LEG_BEZEICHNUNG_MITTEL_DE
    -- TB_LEGENDE.LEG_BEZEICHNUNG_MITTEL_FR
    
    :param ezs_objectid: ezs_objectid der Ebene
    :param legend_list: Liste mit den aus dem XML geparsten Legenden
    '''
    pass