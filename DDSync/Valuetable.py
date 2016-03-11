# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Config
import DDSync.Helper
from lxml import etree


class Valuetable(object):
    def __init__(self, valuetable_xml, attribute_name, ezs_objectid):
        self.xml = valuetable_xml
        self.wtb_join_foreignkey = attribute_name
        self.ezs_objectid = ezs_objectid
        
        self.__extract_dd_infos()
        
    def __extract_dd_infos(self):
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=DDSync.Config.config['xml_namespaces'])
        dd_schema = DDSync.Config.config['dd']['schema']

        self.wtb_objectid = DDSync.Helper.get_dd_sequence_number()
        self.wtb_bezeichnung = unicode(xpatheval("string(gmd:name/gco:CharacterString)"))
        self.wtb_bezeichnung_mittel_de = unicode(xpatheval("string(gmd:description/gco:CharacterString)"))
        self.wtb_bezeichnung_mittel_fr = unicode(xpatheval("string(gmd:description/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        self.wtb_join_primarykey = unicode(xpatheval("string(bee:primaryKey/gco:CharacterString)"))
        self.wtb_join_typ = unicode(xpatheval("string(bee:joinType/bee:joinTypeCode/@codeListValue)"))
        self.wtb_autoload = unicode(xpatheval("string(bee:autoload/gco:Boolean)"))
        
        sql_tb_wertetabelle = "INSERT INTO %s.tb_wertetabelle (WTB_OBJECTID, EZS_OBJECTID, WTB_BEZEICHNUNG, WTB_BEZEICHNUNG_MITTEL_DE, WTB_BEZEICHNUNG_MITTEL_FR, WTB_JOIN_FOREIGNKEY, WTB_JOIN_PRIMARYKEY, WTB_JOIN_TYP, WTB_AUTOLOAD) VALUES (%s, %s, '%s', '%s', '%s', '%s', '%s', '%s', %s)" % (dd_schema, self.wtb_objectid, self.ezs_objectid, self.wtb_bezeichnung, self.wtb_bezeichnung_mittel_de, self.wtb_bezeichnung_mittel_fr, self.wtb_join_foreignkey, self.wtb_join_primarykey, self.wtb_join_typ, self.wtb_autoload)
        print(sql_tb_wertetabelle)