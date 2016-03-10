# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Config
import DDSync.Geoproduct

def sync_geoproduct(code):
    
    gpr = DDSync.Geoproduct.Geoproduct(code)
    
    print("Code: " + gpr.code)
    print("UUID: " + gpr.uuid)
    print("Status: " + gpr.gdbm_status)
    # print("XML: " + gpr.xml.decode('utf-8'))
    
    
    if not gpr.is_valid:
        print("Geoprodukt kann nicht synchronisiert werden!")
        for m in gpr.validation_messages:
            print(m)
