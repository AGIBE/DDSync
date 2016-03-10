# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import mysql.connector
import DDSync.Config

# Diverse Hilfsfunktionen
def get_syncable_codes_from_gdbp():
    codes = []
    return codes

def readOracleSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        result_list = cur.fetchall()
    
    return result_list

def read_from_gdbp(sql):
    username = DDSync.Config.config['gdbp']['username']
    password = DDSync.Config.config['gdbp']['password']
    database = DDSync.Config.config['gdbp']['database']

    connection_string = username + "/" + password + "@" + database
    connection = cx_Oracle.connect(connection_string)
    
    cursor = connection.cursor()
    cursor.execute(sql)
    
    resultList = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return resultList

def read_from_gdbm(sql):
    username = DDSync.Config.config['mysql']['username']
    password = DDSync.Config.config['mysql']['password']
    host = DDSync.Config.config['mysql']['host']
    port = DDSync.Config.config['mysql']['port']
    database = DDSync.Config.config['mysql']['database']
    
    connection = mysql.connector.connect(user=username, password=password, host=host, port=port, database=database)
    
    cursor = connection.cursor()
    cursor.execute(sql)
    
    resultList = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return resultList

def get_dd_sequence_number():
    schema = DDSync.Config.config['dd']['schema']
    sql = "select GDBBE_SEQ.NEXTVAL as GPR_OBJECTID from dual"
    connection_string = DDSync.Config.config['dd']['connection_string']
    res = DDSync.Helper.readOracleSQL(connection_string, sql)
    sequence_number =  unicode(res[0][0])
    return sequence_number
