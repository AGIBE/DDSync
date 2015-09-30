# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Helper
import DDSync.Config
import requests
from lxml import etree

class Geoproduct(object):
    def __init__(self, code):
        self.config = DDSync.Config.config
        self.code = code
        self.uuid = self.__get_uuid()
        self.gdbm_status = self.__get_gdbm_status()
        self.validation_messages = []
        self.xml = self.__get_xml()
        
        self.is_valid = self.__validate()
    
    def __get_uuid(self):
        sql = "SELECT id_geodbmeta FROM gdbp.geoprodukte WHERE code='" + self.code + "'"
        uuid = ""
        return uuid
    
    def __get_gdbm_status(self):
        sql = "SELECT status FROM vw_objects WHERE guid='" + self.uuid + "'"
        status = ""
        return status
    
    def __get_xml(self):
        '''
        Holt das XML vom EasySDI Proxy und parst es. Zurückgegeben
        wird das XML als String.
        '''
        xml = ""
        xml_url = self.config['easysdi_proxy']['baseurl'] + self.uuid
        rsp = requests.get(xml_url)
        xml_tree = etree.fromstring(rsp.text)
        xml = rsp.text
        return xml

    def __validate(self):
        is_valid = True
        
        if self.code in DDSync.Helper.get_syncable_codes_from_gdbp():
            is_valid = False
            self.validation_messages.append("Das Geoprodukt " + self.code + " ist in GeoDBProzess nicht für den Import freigegeben!")
        
        if self.uuid == "":
            is_valid = False
            self.validation_messages.append("Für das Geoprodukt " + self.code + " konnte in GeoDBProzess keine UUID ermittelt werden!")
            
        if self.gdbm_status <> "Published":
            is_valid = False
            self.validation_messages.append("Das Geoprodukt " + self.code + " (" + self.uuid + ") hat in GeoDBmeta nicht den Status 'Published'!")
            
        if self.xml == "":
            is_valid = False
            self.validation_messages.append("Für das Geoprodukt " + self.code + " (" + self.uuid + ") konnte aus GeoDBmeta kein XML heruntergeladen werden!")
            
        return is_valid    

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
