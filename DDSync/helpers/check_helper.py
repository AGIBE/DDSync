# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import os

def run_checkscript_normierung(config, code, jahr, version):

    toolbox = config['CHECKSCRIPT_NORMIERUNG']['toolbox']
    
    result = os.popen(toolbox + " " + code + " " + str(jahr) + " " + str(version) + " true true true true false").read()
    result = [i for i in result.decode('cp1252').split('\n') if i][-1]

    if unicode(result) == "Successfull":
        status_checkscript_normierung = True
    else:
        status_checkscript_normierung = False  
                        
    return status_checkscript_normierung