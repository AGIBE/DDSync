# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from lxml import etree
import DDSync.helpers.sql_helper

class Legend(object):
    def __init__(self, legend_xml, ezs_objectid, config):
        self.config = config
        self.xml = legend_xml
        self.ezs_objectid = ezs_objectid
        
        self.__extract_dd_infos()
        
    def __extract_dd_infos(self):
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=self.config['XML_NAMESPACES'])
        dd_schema = self.config['DD']['schema']
        
        self.leg_objectid_de = DDSync.helpers.sql_helper.get_dd_sequence_number(self.config)
        self.leg_objectid_fr = DDSync.helpers.sql_helper.get_dd_sequence_number(self.config)
        
        self.leg_bezeichnung = unicode(xpatheval("string(gmd:fileName/gco:CharacterString)"))
        
        # Legende deutsch
        self.leg_bezeichnung_mittel_de_de = unicode(xpatheval("string(bee:legendTitleDE/gco:CharacterString)"))
        self.leg_bezeichnung_mittel_fr_de = unicode(xpatheval("string(bee:legendTitleFR/gco:CharacterString)"))
        
        # Legende französisch
        self.leg_bezeichnung_mittel_de_fr = unicode(xpatheval("string(bee:legendTitleDE/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        self.leg_bezeichnung_mittel_fr_fr = unicode(xpatheval("string(bee:legendTitleFR/gmd:PT_FreeText/gmd:textGroup/gmd:LocalisedCharacterString[@locale = '#FR'])"))
        
        sql_tb_legende_de = "INSERT INTO %s.tb_legende (LEG_OBJECTID, EZS_OBJECTID, SPR_OBJECTID, LEG_BEZEICHNUNG, LEG_BEZEICHNUNG_MITTEL_DE, lEG_BEZEICHNUNG_MITTEL_FR) VALUES (%s, %s, 1, '%s', '%s', '%s')" % (dd_schema, self.leg_objectid_de, self.ezs_objectid, self.leg_bezeichnung, self.leg_bezeichnung_mittel_de_de, self.leg_bezeichnung_mittel_fr_de) 
        sql_tb_legende_fr = "INSERT INTO %s.tb_legende (LEG_OBJECTID, EZS_OBJECTID, SPR_OBJECTID, LEG_BEZEICHNUNG, LEG_BEZEICHNUNG_MITTEL_DE, lEG_BEZEICHNUNG_MITTEL_FR) VALUES (%s, %s, 2, '%s', '%s', '%s')" % (dd_schema, self.leg_objectid_fr, self.ezs_objectid, self.leg_bezeichnung, self.leg_bezeichnung_mittel_de_fr, self.leg_bezeichnung_mittel_fr_fr)
        print(sql_tb_legende_de)
        print(sql_tb_legende_fr)