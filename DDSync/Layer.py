# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Helper
import DDSync.Config
import DDSync.Valuetable
import requests
from lxml import etree

class Layer(object):
    def __init__(self, code, uuid, status, gzs_objectid):
        self.config = DDSync.Config.config
        self.code = code
        self.uuid = uuid
        self.gdbm_status = status
        self.gzs_objectid = gzs_objectid

        self.validation_messages = []
        self.valuetables = []
        self.xml = self.__get_xml()
        
        self.is_valid = self.__validate()
        self.extract_dd_infos()
        
        
    def extract_dd_infos(self):
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=DDSync.Config.config['xml_namespaces'])
        dd_schema = DDSync.Config.config['dd']['schema']

        # TB_EBENE
        self.ebe_objectid = self.__get_ebe_objectid()
        if self.ebe_objectid == "0":
            self.ebe_exists = False
            self.ebe_objectid = DDSync.Helper.get_dd_sequence_number()
        else:
            self.ebe_exists = True
        datatype = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/bee:dataType/bee:dataTypecode/@codeListValue)"))
        self.dat_objectid = self.__get_dat_objectid(datatype)
        self.ebe_bezeichnung_mittel_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString)"))
        self.ebe_bezeichnung_mittel_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        self.ebe_bezeichnung_lang_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gco:CharacterString)"))
        self.ebe_bezeichnung_lang_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        
        print("EBE_OBJECTID: " + self.ebe_objectid)
        print("DAT_OBJECTID: " + self.dat_objectid)
        print("EBE_BEZEICHNUNG: " + self.code)
        print("EBE_BEZEICHNUNG_MITTEL_DE: " + self.ebe_bezeichnung_mittel_de)
        print("EBE_BEZEICHNUNG_MITTEL_FR: " + self.ebe_bezeichnung_mittel_fr)
        print("EBE_BEZEICHNUNG_LANG_DE: " + self.ebe_bezeichnung_lang_de)
        print("EBE_BEZEICHNUNG_LANG_FR: " + self.ebe_bezeichnung_lang_fr)
      
        # TB_EBENE_ZEITSTAND
        self.ezs_objectid = DDSync.Helper.get_dd_sequence_number()
        self.leg_objectid_de = "-99"
        self.leg_objectid_fr = "-99"
        self.ezs_reihenfolge = "0"
        self.imp_objectid = "14"
        
        # WERTETABELLEN
        self.valuetables = self.__get_valuetables(xpatheval("/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:contentInfo/gmd:MD_FeatureCatalogueDescription/gmd:class/gmd:MD_Class/gmd:attribute/gmd:MD_Attribute"))
        
        sql_tb_ebene = "INSERT INTO %s.TB_EBENE (EBE_OBJECTID, DAT_OBJECTID, EBE_BEZEICHNUNG, EBE_BEZEICHNUNG_MITTEL_DE, EBE_BEZEICHNUNG_MITTEL_FR, EBE_BEZEICHNUNG_LANG_DE, EBE_BEZEICHNUNG_LANG_FR) VALUES (%s, %s, '%s', '%s', '%s', '%s', '%s')" % (dd_schema, self.ebe_objectid, self.dat_objectid, self.code, self.ebe_bezeichnung_mittel_de, self.ebe_bezeichnung_mittel_fr, self.ebe_bezeichnung_lang_de, self.ebe_bezeichnung_lang_fr)
        sql_tb_ebene_zeitstand = "INSERT INTO %s.TB_EBENE_ZEITSTAND (EZS_OBJECTID, GZS_OBJECTID, EBE_OBJECTID, EZS_REIHENFOLGE, IMP_OBJECTID, UUID, EZS_BEZEICHNUNG_MITTEL_DE, EZS_BEZEICHNUNG_MITTEL_FR, EZS_BEZEICHNUNG_LANG_DE, EZS_BEZEICHNUNG_LANG_FR) VALUES (%s, %s, %s, %s, %s, '%s', '%s', '%s', '%s', '%s')" % (dd_schema, self.ezs_objectid, self.gzs_objectid, self.ebe_objectid, self.ezs_reihenfolge, self.imp_objectid, self.uuid, self.ebe_bezeichnung_mittel_de, self.ebe_bezeichnung_mittel_fr, self.ebe_bezeichnung_lang_de, self.ebe_bezeichnung_lang_fr)
        
        print(sql_tb_ebene)
        print(sql_tb_ebene_zeitstand)
        
    def __get_valuetables(self, attributes):
        for attribute in attributes:
            xpatheval = etree.XPathEvaluator(attribute, namespaces=DDSync.Config.config['xml_namespaces'])
            attribute_name = unicode(xpatheval("gmd:name/gco:CharacterString/text()")[0])
            print(attribute_name)
            valuetables = xpatheval("gmd:namedType/gmd:MD_CodeDomain")
            for valuetable in valuetables:
                self.valuetables.append(DDSync.Valuetable.Valuetable(valuetable, attribute_name, self.ezs_objectid))
            

    def __get_ebe_objectid(self):
        ebe_objectid = "0"
        schema = DDSync.Config.config['dd']['schema']
        sql = "SELECT ebe_objectid FROM " + schema + ".tb_ebene WHERE ebe_bezeichnung = '" + self.code + "'"
        connection_string = self.config['dd']['connection_string']
        res = DDSync.Helper.readOracleSQL(connection_string, sql)
        if len(res) == 1:
            ebe_objectid = unicode(res[0][0])
        return ebe_objectid

    def __get_dat_objectid(self, datatype):
        dd_datatype = self.config['datatype_mapping'][datatype]
        dd_schema = DDSync.Config.config['dd']['schema']
        sql = "SELECT dat_objectid FROM " + dd_schema + ".tb_datentyp WHERE dat_bezeichnung_de='" + dd_datatype + "'"
        connection_string = self.config['dd']['connection_string']
        res = DDSync.Helper.readOracleSQL(connection_string, sql)
        dat_objectid =  unicode(res[0][0])
        return dat_objectid

    def __get_xml(self):
        '''
        Holt das XML vom EasySDI Proxy und parst es. Zurückgegeben
        wird das XML als String.
        '''
        xml = ""
        xml_url = self.config['easysdi_proxy']['baseurl'] + self.uuid
        rsp = requests.get(xml_url)
        # Der XML-String muss vom Typ bytes sein und nicht unicode
        # Ansonsten gibt lxml einen Fehler aus
        # http://lxml.de/parsing.html#python-unicode-strings
        utf8_parser = etree.XMLParser(encoding='utf-8')
        encoded_xml = rsp.text.encode('utf-8')
        xml_tree = etree.fromstring(encoded_xml, utf8_parser)

        return xml_tree

    def __validate(self):
        is_valid = True
        
        if self.uuid == "":
            is_valid = False
            self.validation_messages.append("Für das Geoprodukt " + self.code + " konnte in GeoDBProzess keine UUID ermittelt werden!")
            
        if self.gdbm_status <> "Published":
            is_valid = False
            self.validation_messages.append("Das Geoprodukt " + self.code + " (" + self.uuid + ") hat in GeoDBmeta nicht den Status 'Published'!")
            
        if self.xml == "".encode('utf-8'):
            is_valid = False
            self.validation_messages.append("Für das Geoprodukt " + self.code + " (" + self.uuid + ") konnte aus GeoDBmeta kein XML heruntergeladen werden!")
            
        return is_valid    


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
