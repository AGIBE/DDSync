# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.Config
import DDSync.Geoproduct

def sync_geoproduct(code):
    
    gpr = DDSync.Geoproduct.Geoproduct(code)
    
    print("Code: " + gpr.code)
    print("UUID: " + gpr.uuid)
    print("Status: " + gpr.gdbm_status)