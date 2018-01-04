# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import logging
import os
import datetime

def init_logging(config):
    log_directory = config['LOGGING']['basedir']
    config['LOGGING']['log_directory'] = log_directory
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    if not 'logfile' in config['LOGGING']:
        logfile = os.path.join(log_directory, "DDSync" + datetime.datetime.now().strftime("_%Y_%m_%d_%H_%M_%S") + ".log")
        config['LOGGING']['logfile'] = logfile
        
    logger = logging.getLogger("DDSyncLogger")
    logger.setLevel(logging.DEBUG)
    logger.handlers = []
    logger.addHandler(create_loghandler_file(config['LOGGING']['logfile']))
    logger.propagate = False
    
    config['LOGGING']['logger'] = logger
    
    return logger
    
def create_loghandler_file(filename):
    '''
    Konfiguriert einen File-Loghandler
    :param filename: Name (inkl. Pfad) des Logfiles 
    '''
    
    file_formatter = logging.Formatter('%(asctime)s.%(msecs)d|%(levelname)s|%(message)s', '%Y-%m-%d %H:%M:%S')
    
    h = logging.FileHandler(filename, encoding="UTF-8")
    h.setLevel(logging.DEBUG)
    h.setFormatter(file_formatter)
    
    return h