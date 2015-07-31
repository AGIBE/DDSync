# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

def process_geoproduct(uuid):
    '''
    Sammelt alle Informationen zu einem Geoprodukt
    und verarbeitet diese zu den notwendigen SQL-
    Statements. Die folgenden Tabellen werden damit
    abgefüllt:
    - TB_GP_THEMA
    - TB_GEOPRODUKT
    - TB_GEOPRODUKT_ZEITSTAND
    
    Folgende Prozessschritte werden ausgeführt:
    - alle EasySDI-Infos ermitteln
    - xml holen
    - prüfen, ob EasySDI-Status=published (wenn nicht: mit Fehler abbrechen)
    - prüfen, ob neues Geoprodukt oder Aktualisierung
    - GPR_OBJECTID ermitteln:
    -- entweder: TB_GEOPRODUKT.GPR_OBJECTID bei bestehendem Geoprodukt
    -- oder: nächster Wert in der Geo7-Sequenz bei neuem Geoprodukt
    - GZS_OBJECTID ermitteln (nächster Wert in der Geo7-Sequenz)
    - xml parsen und DD-Felder extrahieren:
    -- TB_GP_THEMA.GPR_OBJECTID
    -- TB_GP_THEMA.THE_OBJECTID
    -- TB_GEOPRODUKT.GPR_OBJECTID
    -- TB_GEOPRODUKT.THE_OBJECTID (entfällt bald)
    -- TB_GEOPRODUKT.GPR_BEZEICHNUNG
    -- TB_GEOPRODUKT.GPR_BEZEICHNUNG_MITTEL_DE (entfällt bald)
    -- TB_GEOPRODUKT.GPR_BEZEICHNUNG_MITTEL_FR (entfällt bald)
    -- TB_GEOPRODUKT.GPR_BEZEICHNUNG_LANG_DE (entfällt bald)
    -- TB_GEOPRODUKT.GPR_BEZEICHNUNG_LANG_FR (entfällt bald)
    -- TB_GEOPRODUKT_ZEITSTAND.GPR_OBJECTID
    -- TB_GEOPRODUKT_ZEITSTAND.GZS_OBJECTID
    -- TB_GEOPRODUKT_ZEITSTAND.STA_OBJECTID (immer =1)
    -- TB_GEOPRODUKT_ZEITSTAND.GZS_ZEITSTAND
    -- TB_GEOPRODUKT_ZEITSTAND.GZS_JAHR
    -- TB_GEOPRODUKT_ZEITSTAND.VERSION
    -- TB_GEOPRODUKT_ZEITSTAND.KLASSIFIKATION
    -- TB_GEOPRODUKT_ZEITSTAND.UUID
    -- TB_GEOPRODUKT_ZEITSTAND.URL1 (werden die noch benötigt?)
    -- TB_GEOPRODUKT_ZEITSTAND.URL2 (werden die noch benötigt?)
    -- TB_GEOPRODUKT_ZEITSTAND.GZS_BEZEICHNUNG_MITTEL_DE
    -- TB_GEOPRODUKT_ZEITSTAND.GZS_BEZEICHNUNG_MITTEL_FR
    -- TB_GEOPRODUKT_ZEITSTAND.GZS_BEZEICHNUNG_LANG_DE
    -- TB_GEOPRODUKT_ZEITSTAND.GZS_BEZEICHNUNG_LANG_FR
    
    :param uuid: UUID des zu prozessierenden Geoprodukts
    '''
    pass
