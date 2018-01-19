# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Valuetable
import DDSync.Legend
import DDSync.helpers.sql_helper
from DDSync.helpers.sql_helper import clean
import requests
from lxml import etree
import os
import arcpy
import sys

class Layer(object):
    def __init__(self, code, uuid, status, gzs_objectid, gprcode, config):
        self.config = config
        self.code = code
        self.gprcode = gprcode
        self.uuid = uuid

        self.gdbm_status = status
        self.gzs_objectid = gzs_objectid
        
        self.logger = self.config['LOGGING']['logger']

        self.validation_messages = []
        self.valuetables = []
        self.legends = []
        self.xml = self.__get_xml()
        
        self.sql_statements= []
        
        self.is_valid = self.__validate()
        if self.is_valid:
            self.logger.info("DD-Infos der Ebene " + self.code + " werden zusammengetragen.")
            self.extract_dd_infos()
            self.__collect_sql_statements()
        else:
            for msg in self.validation_messages:
                self.logger.error(msg)
            raise ValueError("Basis-Check der Ebene nicht bestanden.")
        
    def extract_dd_infos(self):
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=self.config['XML_NAMESPACES'])
        dd_schema = self.config['DD']['schema']

        # TB_EBENE
        self.ebe_objectid = self.__get_ebe_objectid()
        if self.ebe_objectid == "0":
            self.ebe_exists = False
            self.ebe_objectid = DDSync.helpers.sql_helper.get_dd_sequence_number(self.config)
        else:
            self.ebe_exists = True
        datatype = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/bee:dataType/bee:dataTypecode/@codeListValue)"))
        self.dat_objectid = self.__get_dat_objectid(datatype)
        self.ebe_bezeichnung_mittel_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gco:CharacterString)"))
        self.ebe_bezeichnung_mittel_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:title/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        self.ebe_bezeichnung_lang_de = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gco:CharacterString)"))
        self.ebe_bezeichnung_lang_fr = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:citation/gmd:CI_Citation/gmd:otherCitationDetails/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        
        # TB_EBENE_ZEITSTAND
        self.ezs_objectid = DDSync.helpers.sql_helper.get_dd_sequence_number(self.config)
        self.leg_objectid_de = "NULL"
        self.leg_objectid_fr = "NULL"
        self.ezs_reihenfolge = self.__get_ezs_reihenfolge()
        self.imp_objectid = "14"
        self.ezs_importname = "x"
        self.ezs_lv95_transf_methode = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/bee:transformationmethod/bee:transformationmethod)"))
        self.ezs_lv95_transf_ds = unicode(xpatheval("string(/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:referenceSystemInfo/gmd:MD_ReferenceSystem/gmd:referenceSystemIdentifier/gmd:RS_Identifier/bee:transformationdata/bee:transformationdata)"))

        # WERTETABELLEN
        self.__get_valuetables(xpatheval("/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:contentInfo/gmd:MD_FeatureCatalogueDescription/gmd:class/gmd:MD_Class/gmd:attribute/gmd:MD_Attribute"))
        
        # LEGENDEN
        self.__get_legends(xpatheval("/csw:GetRecordByIdResponse/gmd:MD_Metadata/gmd:identificationInfo/gmd:MD_DataIdentification/gmd:graphicOverview/gmd:MD_BrowseGraphic"))
        self.__get_standard_legends()
        
        # Wenn es die Ebene (TB_EBENE) schon gibt, dann muss sie nicht aktualisiert werden.
        if not self.ebe_exists:
            self.sql_statements.append("INSERT INTO %s.TB_EBENE (EBE_OBJECTID, DAT_OBJECTID, EBE_BEZEICHNUNG, EBE_BEZEICHNUNG_MITTEL_DE, EBE_BEZEICHNUNG_MITTEL_FR, EBE_BEZEICHNUNG_LANG_DE, EBE_BEZEICHNUNG_LANG_FR) VALUES (%s, %s, '%s', '%s', '%s', '%s', '%s')" % (dd_schema, self.ebe_objectid, self.dat_objectid, self.code, clean(self.ebe_bezeichnung_mittel_de), clean(self.ebe_bezeichnung_mittel_fr), clean(self.ebe_bezeichnung_lang_de), clean(self.ebe_bezeichnung_lang_fr)))
        self.sql_statements.append("INSERT INTO %s.TB_EBENE_ZEITSTAND (EZS_OBJECTID, GZS_OBJECTID, EBE_OBJECTID, LEG_OBJECTID_DE, LEG_OBJECTID_FR, EZS_REIHENFOLGE, IMP_OBJECTID, UUID, EZS_BEZEICHNUNG_MITTEL_DE, EZS_BEZEICHNUNG_MITTEL_FR, EZS_BEZEICHNUNG_LANG_DE, EZS_BEZEICHNUNG_LANG_FR, EZS_IMPORTNAME, LV95_TRANSF_METHODE, LV95_TRANSF_DS) VALUES (%s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (dd_schema, self.ezs_objectid, self.gzs_objectid, self.ebe_objectid, self.leg_objectid_de, self.leg_objectid_fr, self.ezs_reihenfolge, self.imp_objectid, self.uuid, clean(self.ebe_bezeichnung_mittel_de), clean(self.ebe_bezeichnung_mittel_fr), clean(self.ebe_bezeichnung_lang_de), clean(self.ebe_bezeichnung_lang_fr), self.ezs_importname, clean(self.ezs_lv95_transf_methode), clean(self.ezs_lv95_transf_ds)))
        
        # DOKUMENTE
        self.__get_documents()
        
    def __get_valuetables(self, attributes):
        for attribute in attributes:
            xpatheval = etree.XPathEvaluator(attribute, namespaces=self.config['XML_NAMESPACES'])
            if len(xpatheval("gmd:name/gco:CharacterString/text()")) > 0:
                attribute_name = unicode(xpatheval("gmd:name/gco:CharacterString/text()")[0])
                valuetables = xpatheval("gmd:namedType/gmd:MD_CodeDomain")
                for valuetable in valuetables:
                    self.valuetables.append(DDSync.Valuetable.Valuetable(valuetable, attribute_name, self.ezs_objectid, self.config))
      
    def __get_legends(self, legends_xml):
        for legend in legends_xml:
            self.legends.append(DDSync.Legend.Legend(legend, self.ezs_objectid, self.config))
            
    def __get_standard_legends(self):
        # Nur wenn es überhaupt eine Legende hat, wird sie ausgewählt.
        if len(self.legends) > 0:
            # Es wird erst einmal die allererste Legende als Standard-Legende ausgewählt.
            self.leg_objectid_de = self.legends[0].leg_objectid_de
            self.leg_objectid_fr = self.legends[0].leg_objectid_fr
            # Sollte es eine Legende haben, die STANDARD heisst, dann wird diese als
            # Standard-Legende gewählt.
            for legend in self.legends:
                if legend.leg_bezeichnung == 'STANDARD':
                    self.leg_objectid_de = legend.leg_objectid_de
                    self.leg_objectid_fr = legend.leg_objectid_fr
    
    def __get_documents(self):
        dd_schema = self.config['DD']['schema']
        sql = "SELECT FELDER FROM gdbp.DOKUMENT_ATTRIBUT WHERE EBENE = '" + self.code + "'"
        result = DDSync.helpers.sql_helper.readOracleSQL(self.config['GDBP']['connection_string'], sql)
        if len(result) > 0:
            for row in result:
                self.sql_statements.append("INSERT INTO %s.tb_gp_dok (DOK_ATTRIBUT, EZS_OBJECTID) VALUES ('%s', %s)" % (dd_schema, row[0], self.ezs_objectid))
    
    def __get_ebe_objectid(self):
        ebe_objectid = "0"
        schema = self.config['DD']['schema']
        sql = "SELECT ebe_objectid FROM " + schema + ".tb_ebene WHERE ebe_bezeichnung = '" + self.code + "'"
        connection_string = self.config['DD']['connection_string']
        res = DDSync.helpers.sql_helper.readOracleSQL(connection_string, sql)
        if len(res) == 1:
            ebe_objectid = unicode(res[0][0])
        return ebe_objectid
    
    def __get_ezs_reihenfolge(self):
        ezs_reihenfolge = 99 # Default-Wert
        
        mxdfile = os.path.join(self.config['MXD']['mxd_base_path'], self.gprcode, "work", "mxd", self.gprcode + "_DE.mxd")
        mxd = arcpy.mapping.MapDocument(mxdfile)
        df = arcpy.mapping.ListDataFrames(mxd)[0]

        for index, layer in enumerate(arcpy.mapping.ListLayers(map_document_or_layer=mxd, data_frame=df)):
            # Annotations unterstützen die Property datasetName nicht (evtl. andere auch nicht)
            # In diesem Fall wird einfach der Layername verglichen
            if layer.supports("datasetName"):
                # der datasetName im mxd beginnt in der Regel mit NORM.
                # daher muss nur der hintere Teil per Split ermittelt werden.
                if "." in layer.datasetName:
                    dsname = layer.datasetName.split(".")[1]
                else:
                    dsname = layer.datasetName
                # ohne Schemaname vergleichen
                ebename = self.gprcode + "_" + self.code
    
                if  dsname == ebename: 
                    ezs_reihenfolge = index
            else:
                if layer.name.upper().strip() == self.ebe_bezeichnung_mittel_de:
                    ezs_reihenfolge = index

        if ezs_reihenfolge == 99:
            self.logger.warn("Ebene " + self.code + ": Ebenen-Reihenfolge nicht gefunden.")

        return unicode(ezs_reihenfolge)

    def __get_dat_objectid(self, datatype):
        dd_datatype = self.config['DATATYPE_MAPPING'][datatype]
        dd_schema = self.config['DD']['schema']
        sql = "SELECT dat_objectid FROM " + dd_schema + ".tb_datentyp WHERE dat_bezeichnung_de='" + dd_datatype + "'"
        connection_string = self.config['DD']['connection_string']
        res = DDSync.helpers.sql_helper.readOracleSQL(connection_string, sql)
        dat_objectid =  unicode(res[0][0])
        return dat_objectid

    def __get_xml(self):
        '''
        Holt das XML vom EasySDI Proxy und parst es. Zurückgegeben
        wird das XML als String.
        '''
        xml = ""
        xml_url = self.config['EASYSDI_PROXY']['baseurl'] + self.uuid
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
            self.validation_messages.append("Für die Ebene " + self.code + " konnte in GeoDBProzess keine UUID ermittelt werden!")
            
        if self.gdbm_status <> "Published":
            is_valid = False
            self.validation_messages.append("Die Ebene " + self.code + " (" + self.uuid + ") hat in GeoDBmeta nicht den Status 'Published'!")
            
        if self.xml == "".encode('utf-8'):
            is_valid = False
            self.validation_messages.append("Für die Ebene " + self.code + " (" + self.uuid + ") konnte aus GeoDBmeta kein XML heruntergeladen werden!")
            
        return is_valid
    
    def __collect_sql_statements(self):
        for vt in self.valuetables:
            self.sql_statements = self.sql_statements + vt.sql_statements
            
        for leg in self.legends:
            self.sql_statements = self.sql_statements + leg.sql_statements
            