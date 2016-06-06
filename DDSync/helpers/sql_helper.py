# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import mysql.connector

def readOracleSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        result_list = cur.fetchall()
    
    return result_list

def writeOracleSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        
def readMySQL(sql_statement, config):
    username = config['MYSQL']['username']
    password = config['MYSQL']['password']
    host = config['MYSQL']['host']
    port = config['MYSQL']['port']
    database = config['MYSQL']['database']
    # mysql.connector ist wahrscheinlich kein contextmanager
    conn = mysql.connector.connect(user=username, password=password, host=host, port=port, database=database)
    cur = conn.cursor()
    cur.execute(sql_statement)
    result_list = cur.fetchall()
    
    cur.close()
    conn.close()
        
    return result_list

def get_syncable_codes_from_gdbp(config):
    sql = "select code from gdbp.geoprodukte where ARBEITSTARTDATUM_NORMIERUNG is not null and FREIGABEDATUM_NORMIERUNG is not null and FREIGABEDATUM_GEODB_WIPPE is null order by code asc"
    codes = []
    gdbp_results = readOracleSQL(config['GDBP']['connection_string'], sql)
    for row in gdbp_results:
        codes.append(row[0])

    return codes

def get_dd_sequence_number(config):
    schema = config['DD']['schema']
    sql = "select GDBBE_SEQ.NEXTVAL as GPR_OBJECTID from dual"
    connection_string = config['DD']['connection_string']
    res = readOracleSQL(connection_string, sql)
    sequence_number =  unicode(res[0][0])
    return sequence_number