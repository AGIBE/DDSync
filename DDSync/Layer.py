# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

def process_ebene(uuid, gzs_objectid):
    '''
    Sammelt alle Informationen zu einer Ebene
    und verarbeitet diese zu den notwendigen SQL-
    Statements. Die folgenden Tabellen werden damit
    abgefüllt:
    - TB_EBENE
    - TB_EBENE_ZEITSTAND

    Folgende Prozessschritte werden ausgeführt:
    - alle EasySDI-Infos ermitteln
    - xml holen
    - prüfen, ob EasySDI-Status=published (wenn nicht: mit Fehler abbrechen)
    - prüfen, ob neue Ebene oder Aktualisierung
    - EBE_OBJECTID ermitteln:
    -- entweder: TB_EBENE.EBE_OBJECTID bei bestehender Ebene
    -- oder: nächster Wert in der Geo7-Sequenz bei neuer Ebene
    - EZS_OBJECTID ermitteln (nächster Wert in der Geo7-Sequenz)
    - EZS_Reihenfolge aus MXD auslesen
    - xml parsen und DD-Felder extrahieren:
    -- TB_EBENE.EBE_OBJECTID
    -- TB_EBENE.DAT_OBJECTID
    -- TB_EBENE.EBE_BEZEICHNUNG
    -- TB_EBENE.EBE_BEZEICHNUNG_MITTEL_DE (entfällt bald)
    -- TB_EBENE.EBE_BEZEICHNUNG_LANG_DE (entfällt bald)
    -- TB_EBENE.EBE_BEZEICHNUNG_MITTEL_FR (entfällt bald)
    -- TB_EBENE.EBE_BEZEICHNUNG_LANG_FR (entfällt bald)
    -- TB_EBENE_ZEITSTAND.EZS_OBJECTID
    -- TB_EBENE_ZEITSTAND.GZS_OBJECTID
    -- TB_EBENE_ZEITSTAND.EBE_OBJECTID
    -- TB_EBENE_ZEITSTAND.LEG_OBJECTID_DE
    -- TB_EBENE_ZEITSTAND.LEG_OBJECTID_FR
    -- TB_EBENE_ZEITSTAND.EZS_IMPORTNAME (entfällt?)
    -- TB_EBENE_ZEITSTAND.EZS_REIHENFOLGE
    -- TB_EBENE_ZEITSTAND.IMP_OBJECTID (entfällt?)
    -- TB_EBENE_ZEITSTAND.UUID
    -- TB_EBENE_ZEITSTAND.URL1 (werden die noch benötigt?)
    -- TB_EBENE_ZEITSTAND.URL2 (werden die noch benötigt?)
    -- TB_EBENE_ZEITSTAND.EZS_BEZEICHNUNG_MITTEL_DE
    -- TB_EBENE_ZEITSTAND.EZS_BEZEICHNUNG_LANG_DE
    -- TB_EBENE_ZEITSTAND.EZS_BEZEICHNUNG_MITTEL_FR
    -- TB_EBENE_ZEITSTAND.EZS_BEZEICHNUNG_LANG_FR
    -- TB_EBENE_ZEITSTAND.LV95_TRANSF_METHODE (nötig?)
    -- TB_EBENE_ZEITSTAND.LV95_TRANSF_DS (nötig?)

    :param uuid: UUID der zu prozessierenden Ebene
    :param gzs_objectid: gzs_objectid des Geoprodukts
    '''
