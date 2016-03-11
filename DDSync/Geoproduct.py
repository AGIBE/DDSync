# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Helper
import DDSync.Config
import DDSync.Layer
import requests
from lxml import etree
import datetime
import sys

class Geoproduct(object):
    def __init__(self, code):
        self.config = DDSync.Config.config
        self.code = code
        self.uuid = self.__get_uuid()

        self.gdbm_status = self.__get_gdbm_status()
        self.gdbm_versionid = self.__get_gdbm_versionid()
        
        self.xml = self.__get_xml()

        self.validation_messages = []
        self.is_valid = self.__validate()

        if self.is_valid:
            self.extract_dd_infos()
            self.layers = self.__get_layers()
        else:
            for msg in self.validation_messages:
                print(msg)
    
    def extract_dd_infos(self):
   
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=DDSync.Config.config['xml_namespaces'])
        dd_schema = DDSync.Config.config['dd']['schema']
        
        # TB_GEOPRODUKT
        self.gpr_objectid = self.__get_gpr_objectid()
        if self.gpr_objectid == "0":
            self.gpr_exists = False
            self.gpr_objectid = DDSync.Helper.get_dd_sequence_number()
        else:
            self.gpr_exists = True
        
        category = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode/@codeListValue)"))
        self.the_objectid = self.__get_the_objectid(category)
        self.gpr_bezeichnung = self.code
        self.gpr_bezeichnung_mittel_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString)"))
        self.gpr_bezeichnung_mittel_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString)"))
        self.gpr_bezeichnung_lang_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gco:CharacterString)"))
        self.gpr_bezeichnung_lang_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString/text())"))
        
        print("GPR_OBJECTID: " + self.gpr_objectid)
        print("THE_OBJECTID: " + self.the_objectid)
        print("GPR_BEZEICHNUNG: " + self.gpr_bezeichnung)
        print("GPR_BEZEICHNUNG_MITTEL_DE: " + self.gpr_bezeichnung_mittel_de)
        print("GPR_BEZEICHNUNG_MITTEL_FR: " + self.gpr_bezeichnung_mittel_fr)
        print("GPR_BEZEICHNUNG_LANG_DE: " + self.gpr_bezeichnung_lang_de)
        print("GPR_BEZEICHNUNG_LANG_FR: " + self.gpr_bezeichnung_lang_fr)
        
        # TB_GEOPRODUKT_ZEITSTAND
        self.gzs_objectid = DDSync.Helper.get_dd_sequence_number()
        dates = xpatheval("/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date")
        self.gzs_zeitstand = self.__get_revision_date(dates) 
        self.gzs_jahr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/bee:version/bee:DD_DataDictionary/bee:versionYear/gco:Decimal)"))
        self.gzs_version = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/bee:version/bee:DD_DataDictionary/bee:versionNumber/gco:Decimal)"))
        self.gzs_klassifikation = ""
        if len(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString)")) > 0:
            self.gzs_klassifikation = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString)"))[0]
        self.gzs_bezeichnung_mittel_de = self.gpr_bezeichnung_mittel_de
        self.gzs_bezeichnung_mittel_fr = self.gpr_bezeichnung_mittel_fr
        self.gzs_bezeichnung_lang_de = self.gpr_bezeichnung_lang_de
        self.gzs_bezeichnung_lang_fr = self.gpr_bezeichnung_lang_fr
        self.sta_objectid = "1"
        
        print("GZS_OBJECTID: " + self.gzs_objectid)
        print("GZS_ZEITSTAND: " + datetime.datetime.strftime(self.gzs_zeitstand, '%Y.%m.%d'))
        print("GZS_JAHR: " + self.gzs_jahr)
        print("GZS_VERSION: " + self.gzs_version)
        print("GZS_KLASSIFIKATION: " + self.gzs_klassifikation)
        print("GZS_BEZEICHNUNG_MITTEL_DE: " + self.gzs_bezeichnung_mittel_de)
        print("GZS_BEZEICHNUNG_MITTEL_FR: " + self.gzs_bezeichnung_mittel_fr)
        print("GZS_BEZEICHNUNG_LANG_DE: " + self.gzs_bezeichnung_lang_de)
        print("GZS_BEZEICHNUNG_LANG_FR: " + self.gzs_bezeichnung_lang_fr)
        print("STA_OBJECTID: " + self.sta_objectid)
        print("UUID: " + self.uuid)
        
        self.sql_tb_geoprodukt = "INSERT INTO %s.TB_GEOPRODUKT (gpr_bezeichnung, gpr_bezeichnung_mittel_de, gpr_bezeichnung_mittel_fr, gpr_bezeichnung_lang_de, gpr_bezeichnung_lang_fr) VALUES ('%s', '%s', '%s', '%s', '%s')" % (dd_schema, self.gpr_bezeichnung, self.gpr_bezeichnung_mittel_de, self.gpr_bezeichnung_mittel_fr, self.gpr_bezeichnung_lang_de, self.gpr_bezeichnung_lang_fr)
        self.sql_tb_gp_thema = "INSERT INTO %s.TB_GP_THEMA (gpr_objectid, the_objectid) VALUES (%s, %s)" % (dd_schema, self.gpr_objectid, self.the_objectid)
        self.sql_tb_geoprodukt_zeitstand = "INSERT INTO %s.TB_GEOPRODUKT_ZEITSTAND (gzs_bezeichnung_mittel_de, gzs_bezeichnung_mittel_fr, gzs_bezeichnung_lang_de, gzs_bezeichung_lang_fr) VALUES ('%s', '%s', '%s', '%s')" % (dd_schema, self.gzs_bezeichnung_mittel_de, self.gzs_bezeichnung_mittel_fr, self.gzs_bezeichnung_lang_de, self.gzs_bezeichnung_lang_fr)
        
        print(self.sql_tb_geoprodukt)
        print(self.sql_tb_gp_thema)
        print(self.sql_tb_geoprodukt_zeitstand)
    
    def __get_uuid(self):
        uuid = ""
        gdbp_schema = DDSync.Config.config['gdbp']['schema']
        sql = "SELECT id_geodbmeta FROM " + gdbp_schema + ".geoprodukte WHERE code='" + self.code + "'"
        gdbp_results = DDSync.Helper.read_from_gdbp(sql)
        if len(gdbp_results) == 1:
            uuid = gdbp_results[0][0]

        return uuid
    
    def __get_gdbm_status(self):
        status = ""
        sql = "SELECT status FROM vw_objects WHERE guid='" + self.uuid + "'"
        gdbm_results = DDSync.Helper.read_from_gdbm(sql)
        if len(gdbm_results) == 1:
            status = gdbm_results[0][0]

        return status
    
    def __get_gdbm_versionid(self):
        versionid = ""
        sql = "SELECT versionid FROM vw_objects WHERE guid='" + self.uuid + "'"
        gdbm_results = DDSync.Helper.read_from_gdbm(sql)
        if len(gdbm_results) == 1:
            versionid = unicode(gdbm_results[0][0])

        return versionid
    
    def __get_layers(self):
        layers = []
        sql = "SELECT code, guid, status FROM vw_objects WHERE versionid in (SELECT child_id FROM jos_sdi_objectversionlink WHERE parent_id=" + self.gdbm_versionid + ") ORDER BY code asc"
        gdbm_results = DDSync.Helper.read_from_gdbm(sql)
        if len(gdbm_results) > 0:
            for gdbm_result in gdbm_results:
                layer = DDSync.Layer.Layer(gdbm_result[0], gdbm_result[1], gdbm_result[2], self.gzs_objectid)
                layers.append(layer)

        return layers
    
    def __get_xml(self):
        '''
        Holt das XML vom EasySDI Proxy und parst es. Zurückgegeben
        wird das XML als String.
        '''
        xml_url = self.config['easysdi_proxy']['baseurl'] + self.uuid
        rsp = requests.get(xml_url)
        # Der XML-String muss vom Typ bytes sein und nicht unicode
        # Ansonsten gibt lxml einen Fehler aus
        # http://lxml.de/parsing.html#python-unicode-strings
        utf8_parser = etree.XMLParser(encoding='utf-8')
        encoded_xml = rsp.text.encode('utf-8')
        xml_tree = etree.fromstring(encoded_xml, utf8_parser)

        return xml_tree
    
    def __get_revision_date(self, dates):
        revision_date = ""
        for date in dates:
            xpatheval = etree.XPathEvaluator(date, namespaces=DDSync.Config.config['xml_namespaces'])
            dateType = unicode(xpatheval("gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode/@codeListValue")[0])
            if dateType == 'revision':
                revision_date = unicode(xpatheval("gmd:CI_Date/gmd:date/gco:Date/text()")[0])
                revision_date = datetime.datetime.strptime(revision_date, '%Y-%m-%d') 
        return revision_date
    
    def __get_gpr_objectid(self):
        gpr_objectid = "0"
        schema = DDSync.Config.config['dd']['schema']
        sql = "SELECT gpr_objectid FROM " + schema + ".tb_geoprodukt WHERE gpr_bezeichnung = '" + self.code + "'"
        connection_string = self.config['dd']['connection_string']
        res = DDSync.Helper.readOracleSQL(connection_string, sql)
        if len(res) == 1:
            gpr_objectid = unicode(res[0][0])
        return gpr_objectid
    
    def __get_the_objectid(self, category):
        print("KATEGORIE:" + category)
        dd_category = self.config['category_mapping'][category]
        dd_schema = DDSync.Config.config['dd']['schema']
        sql = "SELECT the_objectid FROM " + dd_schema + ".tb_thema WHERE the_bezeichnung='" + dd_category + "'"
        connection_string = self.config['dd']['connection_string']
        res = DDSync.Helper.readOracleSQL(connection_string, sql)
        the_objectid =  unicode(res[0][0])
        return the_objectid

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
            
        if self.gdbm_versionid == "":
            is_valid = False
            self.validation_messages.append("Für das Geoprodukt " + self.code + " (" + self.uuid + ") konnte in GeoDBmeta keine ObjectversionID gefunden werden.!")
            
        if self.xml == "".encode('utf-8'):
            is_valid = False
            self.validation_messages.append("Für das Geoprodukt " + self.code + " (" + self.uuid + ") konnte aus GeoDBmeta kein XML heruntergeladen werden!")
            
        return is_valid
