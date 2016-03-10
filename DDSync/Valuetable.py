# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Config
import DDSync.Helper
from lxml import etree


class Valuetable(object):
    def __init__(self, valuetable_xml, attribute_name, ezs_objectid):
        self.xml = valuetable_xml
        self.attribute_name = attribute_name
        self.ezs_objectid = ezs_objectid
        
        self.__extract_dd_infos()
        
    def __extract_dd_infos(self):
        xpatheval = etree.XPathEvaluator(self.xml, namespaces=DDSync.Config.config['xml_namespaces'])
        dd_schema = DDSync.Config.config['dd']['schema']

        self.wtb_objectid = DDSync.Helper.get_dd_sequence_number()
        self.wtb_bezeichnung = unicode(xpatheval("gmd:MD_CodeDomain/gmd:name/gco:CharacterString/text()"))
        
        print(self.wtb_bezeichnung)