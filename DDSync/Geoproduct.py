# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.helpers.config_helper
import DDSync.helpers.sql_helper
from DDSync.helpers.sql_helper import clean
import DDSync.helpers.check_helper
import DDSync.Layer
import requests
import codecs
from lxml import etree
import sys

class Geoproduct(object):
    def __init__(self, code):
        self.config = DDSync.helpers.config_helper.get_config()
        self.logger = self.config['LOGGING']['logger']
        
        self.code = code.upper()
        self.logger.info("Starte Synchronisierung des Geoprodukts " + self.code)
        
        self.uuid = DDSync.helpers.sql_helper.get_uuid(self.config, self.code)
        self.logger.info("Metadaten-UUID: " + self.uuid)

        self.gdbm_status = self.__get_gdbm_status()
        self.gdbm_versionid = self.__get_gdbm_versionid()
        
        self.xml = self.__get_xml()

        self.__get_jahr_version()

        self.validation_messages = []
        self.is_valid = self.__validate()
        
        self.sql_statements = []

        if self.is_valid:
            self.logger.info("Basis-Check erfolgreich absolviert.")
            self.logger.info("DD-Infos werden zusammengetragen.")
            self.extract_dd_infos()
            self.layers = self.__get_layers()
            self.__collect_sql_statements()
        else:
            for msg in self.validation_messages:
                self.logger.error(msg)
            sys.exit()
    
    def write_sql_to_file(self, sql_filename):
        with codecs.open(sql_filename, "w", "utf-8") as f:
            self.logger.info("Schreibe SQL-Statements in " + sql_filename)
            for sql in self.sql_statements:
                f.write(sql + ";\n")

    def write_sql_to_dd(self):
        self.logger.info("Schreibe folgende SQL-Statements ins DataDictionary:")
        for sql in self.sql_statements:
            self.logger.info(sql)
        DDSync.helpers.sql_helper.writeOracleSQL_multiple(self.config['DD']['connection_string'], self.sql_statements)
        self.logger.info("Das Geoprodukt " + self.code + " wurde erfolgreich ins DataDictionary der GeoDB synchronisiert.")
            
    def extract_dd_infos(self):
   
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=self.config['XML_NAMESPACES'])
        dd_schema = self.config['DD']['schema']
        
        # TB_GEOPRODUKT
        self.gpr_objectid = self.__get_gpr_objectid()
        if self.gpr_objectid == "0":
            self.gpr_exists = False
            self.gpr_objectid = DDSync.helpers.sql_helper.get_dd_sequence_number(self.config)
        else:
            self.gpr_exists = True
        
        category = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:topicCategory/gmd:MD_TopicCategoryCode/@codeListValue)"))
        self.the_objectid = self.__get_the_objectid(category)
        self.gpr_bezeichnung = self.code
        self.gpr_bezeichnung_mittel_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString)"))
        self.gpr_bezeichnung_mittel_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString)"))
        self.gpr_bezeichnung_lang_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gco:CharacterString)"))
        self.gpr_bezeichnung_lang_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString/text())"))
        
        # TB_GEOPRODUKT_ZEITSTAND
        self.gzs_objectid = DDSync.helpers.sql_helper.get_dd_sequence_number(self.config)
        dates = xpatheval("/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:date")
        self.gzs_zeitstand = self.__get_revision_date(dates) 
        self.gzs_jahr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/bee:version/bee:DD_DataDictionary/bee:versionYear/gco:Decimal)"))
        self.gzs_version = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/bee:version/bee:DD_DataDictionary/bee:versionNumber/gco:Decimal)"))
        self.gzs_klassifikation = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString)"))[0]
        if len(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString)")) > 0:
            self.gzs_klassifikation = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints/gmd:otherConstraints/gco:CharacterString)"))[0]
        self.gzs_bezeichnung_mittel_de = self.gpr_bezeichnung_mittel_de
        self.gzs_bezeichnung_mittel_fr = self.gpr_bezeichnung_mittel_fr
        self.gzs_bezeichnung_lang_de = self.gpr_bezeichnung_lang_de
        self.gzs_bezeichnung_lang_fr = self.gpr_bezeichnung_lang_fr
        self.sta_objectid = "1"

        # Wenn es das Geoprodukt (TB_GEOPRODUKT) schon gibt, dann muss es nicht aktualisiert werden.
        if not self.gpr_exists:        
            self.sql_statements.append("INSERT INTO %s.TB_GEOPRODUKT (gpr_bezeichnung, gpr_bezeichnung_mittel_de, gpr_bezeichnung_mittel_fr, gpr_bezeichnung_lang_de, gpr_bezeichnung_lang_fr, the_objectid) VALUES ('%s', '%s', '%s', '%s', '%s', %s)" % (dd_schema, self.gpr_bezeichnung, clean(self.gpr_bezeichnung_mittel_de), clean(self.gpr_bezeichnung_mittel_fr), clean(self.gpr_bezeichnung_lang_de), clean(self.gpr_bezeichnung_lang_fr), self.the_objectid))
            self.sql_statements.append("INSERT INTO %s.TB_GP_THEMA (gpr_objectid, the_objectid) VALUES (%s, %s)" % (dd_schema, self.gpr_objectid, self.the_objectid))
        self.sql_statements.append("INSERT INTO %s.TB_GEOPRODUKT_ZEITSTAND (gzs_objectid, gpr_objectid, sta_objectid, gzs_zeitstand, gzs_jahr, gzs_version, gzs_klassifikation, uuid, gzs_bezeichnung_mittel_de, gzs_bezeichnung_mittel_fr, gzs_bezeichnung_lang_de, gzs_bezeichnung_lang_fr) VALUES (%s, %s, %s, TO_DATE('%s', 'YYYY-MM-DD'), %s, %s, %s, '%s', '%s', '%s', '%s', '%s')" % (dd_schema, self.gzs_objectid, self.gpr_objectid, self.sta_objectid, self.gzs_zeitstand, self.gzs_jahr, self.gzs_version, self.gzs_klassifikation, self.uuid, clean(self.gzs_bezeichnung_mittel_de), clean(self.gzs_bezeichnung_mittel_fr), clean(self.gzs_bezeichnung_lang_de), clean(self.gzs_bezeichnung_lang_fr)))
        
#     def get_uuid(self, code):
#         uuid = ""
#         gdbp_schema = self.config['GDBP']['schema']
#         sql = "SELECT id_geodbmeta FROM " + gdbp_schema + ".geoprodukte WHERE code='" + self.code + "'"
#         gdbp_results = DDSync.helpers.sql_helper.readOracleSQL(self.config['GDBP']['connection_string'], sql)
#         if len(gdbp_results) == 1:
#             if gdbp_results[0][0]:
#                 uuid = gdbp_results[0][0]
# 
#         return uuid
    
    def __get_gdbm_status(self):
        status = ""
        sql = "SELECT status FROM vw_objects WHERE guid='" + self.uuid + "'"
        gdbm_results = DDSync.helpers.sql_helper.readMySQL(sql, self.config)
        if len(gdbm_results) == 1:
            status = gdbm_results[0][0]

        return status
    
    def __get_gdbm_versionid(self):
        versionid = ""
        sql = "SELECT versionid FROM vw_objects WHERE guid='" + self.uuid + "'"
        gdbm_results = DDSync.helpers.sql_helper.readMySQL(sql, self.config)
        if len(gdbm_results) == 1:
            versionid = unicode(gdbm_results[0][0])

        return versionid
    
    def __get_layers(self):
        layers = []
        sql = "SELECT code, guid, status FROM vw_objects WHERE versionid in (SELECT child_id FROM jos_sdi_objectversionlink WHERE parent_id=" + self.gdbm_versionid + ") ORDER BY code asc"
        gdbm_results = DDSync.helpers.sql_helper.readMySQL(sql, self.config)
        if len(gdbm_results) > 0:
            for gdbm_result in gdbm_results:
                layer = DDSync.Layer.Layer(gdbm_result[0], gdbm_result[1], gdbm_result[2], self.gzs_objectid, self.code, self.config)
                layers.append(layer)

        return layers
    
    def __get_xml(self):
        '''
        Holt das XML vom EasySDI Proxy und parst es. Zurückgegeben
        wird das XML als String.
        '''
        xml_url = self.config['EASYSDI_PROXY']['baseurl'] + self.uuid
        rsp = requests.get(xml_url)
        # Der XML-String muss vom Typ bytes sein und nicht unicode
        # Ansonsten gibt lxml einen Fehler aus
        # http://lxml.de/parsing.html#python-unicode-strings
        utf8_parser = etree.XMLParser(encoding='utf-8')
        encoded_xml = rsp.text.encode('utf-8')
        xml_tree = etree.fromstring(encoded_xml, utf8_parser)

        return xml_tree
    
    def __get_jahr_version(self):
        sql = "select zeitstand_jahr, zeitstand_version from gdbp.geoprodukte where code='" + self.code + "'"
        result = DDSync.helpers.sql_helper.readOracleSQL(self.config['GDBP']['connection_string'], sql)
        self.jahr = result[0][0]
        self.version = result[0][1]
    
    def __get_revision_date(self, dates):
        revision_date = ""
        for date in dates:
            xpatheval = etree.XPathEvaluator(date, namespaces=self.config['XML_NAMESPACES'])
            dateType = unicode(xpatheval("gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode/@codeListValue")[0])
            if dateType == 'revision':
                revision_date = unicode(xpatheval("gmd:CI_Date/gmd:date/gco:Date/text()")[0])
#                 revision_date = datetime.datetime.strptime(revision_date, '%Y-%m-%d') 
        return revision_date
    
    def __get_gpr_objectid(self):
        gpr_objectid = "0"
        schema = self.config['DD']['schema']
        sql = "SELECT gpr_objectid FROM " + schema + ".tb_geoprodukt WHERE gpr_bezeichnung = '" + self.code + "'"
        connection_string = self.config['DD']['connection_string']
        res = DDSync.helpers.sql_helper.readOracleSQL(connection_string, sql)
        if len(res) == 1:
            gpr_objectid = unicode(res[0][0])
        return gpr_objectid
    
    def __get_the_objectid(self, category):
        dd_category = self.config['category_mapping'][category]
        dd_schema = self.config['DD']['schema']
        sql = "SELECT the_objectid FROM " + dd_schema + ".tb_thema WHERE the_bezeichnung='" + dd_category + "'"
        connection_string = self.config['DD']['connection_string']
        res = DDSync.helpers.sql_helper.readOracleSQL(connection_string, sql)
        the_objectid =  unicode(res[0][0])
        return the_objectid

    def __validate(self):
        is_valid = True
        
        if DDSync.helpers.sql_helper.uuid_exists_in_dd(self.config, self.uuid):
            is_valid = False
            self.validation_messages.append("Der Zeitstand existiert bereits im DataDictionary!")
        
        if self.code not in DDSync.helpers.sql_helper.get_syncable_codes_from_gdbp(self.config):
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
            
#         if DDSync.helpers.check_helper.run_checkscript_normierung(self.config, self.code, self.jahr, self.version) == False:
#             is_valid = False
#             self.validation_messages.append("Das Geoprodukt " + self.code + " hat das Checkscript Normierung nicht erfolgreich absolviert.")
            
        return is_valid
    
    def __collect_sql_statements(self):
        for layer in self.layers:
            self.sql_statements = self.sql_statements + layer.sql_statements
