# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Config
import DDSync.Helper
from lxml import etree

class Legend(object):
    def __init__(self, legend_xml, ezs_objectid):
        self.xml = legend_xml
        self.ezs_objectid = ezs_objectid
        
        self.__extract_dd_infos()
        
    def __extract_dd_infos(self):
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=DDSync.Config.config['xml_namespaces'])
        dd_schema = DDSync.Config.config['dd']['schema']
        
        self.leg_objectid_de = DDSync.Helper.get_dd_sequence_number()
        self.leg_objectid_fr = DDSync.Helper.get_dd_sequence_number()
        
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