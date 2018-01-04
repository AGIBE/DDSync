# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import DDSync.helpers.crypto_helper
import DDSync.helpers.log_helper
import configobj
import os

def decrypt_passwords(section, key):
    '''
    Entschlüsselt sämtliche Passworte in der zentralen
    Konfigurationsdatei. Wird aus der ConfigObj.walk-Funktion
    aus aufgerufen. Deshalb sind section und key als
    Parameter obligatorisch.
    :param section: ConfigObj.Section-Objekt
    :param key: aktueller Schlüssel im ConfigObj-Objekt
    '''
    # Hilfsklasse für die Entschlüsselung
    
    # Annahme: alle Keys, die "password" heissen, enthalten zu entschlüsselnde Passwörter
    crypter = DDSync.helpers.crypto_helper.Crypter()
    if key == "password":
        encrypted_password = section[key]
        decrypted_password = crypter.decrypt(encrypted_password)
        # Wert in der Config ersetzen
        section[key] = decrypted_password


def get_general_configfile_from_envvar():
    '''
    Holt den Pfad zur Konfigurationsdatei aus der Umgebungsvariable
    DDSYNCHOME und gibt dann den vollständigen Pfad (inkl. Dateiname)
    der Konfigurationsdatei zurück.
    '''
    config_directory = os.environ['DDSYNCHOME']
    config_filename = "config.ini"
    
    config_file = os.path.join(config_directory, config_filename)
    
    return config_file

def init_generalconfig():
    '''
    liest die zentrale Konfigurationsdatei in ein ConfigObj-Objet ein.
    Dieser kann wie ein Dictionary gelesen werden.
    '''
    config_filename = get_general_configfile_from_envvar()
    config_file = configobj.ConfigObj(config_filename, encoding="UTF-8")
    
    # Die Walk-Funktion geht rekursiv durch alle
    # Sections und Untersections der Config und 
    # ruft für jeden Key die angegebene Funktion
    # auf
    config_file.walk(decrypt_passwords)
    
    return config_file.dict()

def create_connection_string(config, key):
    username = config[key]['username']
    password = config[key]['password']
    database = config[key]['database']
    
    connection_string = username + "/" + password + "@" + database
    config[key]['connection_string'] = connection_string

# Config wird immer eingelesen
config = init_generalconfig()
  
logger_dd = DDSync.helpers.log_helper.init_logging(config)
logger_dd.info('Konfiguration wird eingelesen.')
logger_dd.info('Logfile: ' + config['LOGGING']['logfile'])

# Connection-Strings zusammensetzen
create_connection_string(config, 'GDBP')
create_connection_string(config, 'DD')
     
