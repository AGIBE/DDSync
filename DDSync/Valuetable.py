# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from lxml import etree
import DDSync.helpers.sql_helper


class Valuetable(object):
    def __init__(self, valuetable_xml, attribute_name, ezs_objectid, config):
        self.config = config
        self.xml = valuetable_xml
        self.wtb_join_foreignkey = attribute_name
        self.ezs_objectid = ezs_objectid
        
        self.sql_statements = []
        
        self.__extract_dd_infos()
        
    def __extract_dd_infos(self):
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=self.config['XML_NAMESPACES'])
        dd_schema = self.config['DD']['schema']

        self.wtb_objectid = DDSync.helpers.sql_helper.get_dd_sequence_number(self.config)
        self.wtb_bezeichnung = unicode(xpatheval("string(gmd:name/gco:CharacterString)"))
        self.wtb_bezeichnung_mittel_de = unicode(xpatheval("string(gmd:description/gco:CharacterString)"))
        self.wtb_bezeichnung_mittel_fr = unicode(xpatheval("string(gmd:description/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        self.wtb_join_primarykey = unicode(xpatheval("string(bee:primaryKey/gco:CharacterString)"))
        self.wtb_join_typ = unicode(xpatheval("string(bee:joinType/bee:joinTypeCode/@codeListValue)"))
        self.wtb_autoload = unicode(xpatheval("string(bee:autoload/gco:Boolean)"))
        self.wtb_importname = "x"
        
        self.sql_statements.append("INSERT INTO %s.tb_wertetabelle (WTB_OBJECTID, EZS_OBJECTID, WTB_BEZEICHNUNG, WTB_BEZEICHNUNG_MITTEL_DE, WTB_BEZEICHNUNG_MITTEL_FR, WTB_JOIN_FOREIGNKEY, WTB_JOIN_PRIMARYKEY, WTB_JOIN_TYP, WTB_AUTOLOAD, WTB_IMPORTNAME) VALUES (%s, %s, '%s', '%s', '%s', '%s', '%s', '%s', %s, '%s');" % (dd_schema, self.wtb_objectid, self.ezs_objectid, self.wtb_bezeichnung, self.wtb_bezeichnung_mittel_de, self.wtb_bezeichnung_mittel_fr, self.wtb_join_foreignkey, self.wtb_join_primarykey, self.wtb_join_typ, self.wtb_autoload, self.wtb_importname))