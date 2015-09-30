# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Config
import DDSync.Geoproduct

def sync_geoproduct(code):
    
    gpr = DDSync.Geoproduct.Geoproduct(code)
    
    if not gpr.is_valid:
        print("Geoprodukt kann nicht synchronisiert werden!")
        for m in gpr.validation_messages:
            print(m)
        raise Exception