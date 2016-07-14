# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import pymysql

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
        
def writeOracleSQL_multiple(connection_string, sql_statements):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        for sql_statement in sql_statements:
            cur.execute(sql_statement)
 

def readMySQL(sql_statement, config):
    username = config['MYSQL']['username']
    password = config['MYSQL']['password']
    host = str(config['MYSQL']['host'])
    port = int(config['MYSQL']['port'])
    database = config['MYSQL']['database']

    conn = pymysql.connect(host=host, user=username, password=password, db=database, port=port)
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_statement)
            result_list = cursor.fetchall()
    finally:
        conn.close()
    
    return result_list

def get_syncable_codes_from_gdbp(config):
    sql = "select code from gdbp.geoprodukte where ARBEITSTARTDATUM_NORMIERUNG is not null and FREIGABEDATUM_NORMIERUNG is not null and FREIGABEDATUM_GEODB_WIPPE is null order by code asc"
    codes = []
    gdbp_results = readOracleSQL(config['GDBP']['connection_string'], sql)
    for row in gdbp_results:
        codes.append(row[0])

    return codes

def get_uuid(config, code):
    uuid = ""
    gdbp_schema = config['GDBP']['schema']
    sql = "SELECT id_geodbmeta FROM " + gdbp_schema + ".geoprodukte WHERE code='" + code + "'"
    gdbp_results = readOracleSQL(config['GDBP']['connection_string'], sql)
    if len(gdbp_results) == 1:
        if gdbp_results[0][0]:
            uuid = gdbp_results[0][0]

    return uuid

def uuid_exists_in_dd(config, uuid):
    uuid_exists = True
    schema = config['DD']['schema']
    sql = "select gzs_objectid from " + schema + ".TB_GEOPRODUKT_ZEITSTAND where uuid='" + uuid + "'"
    res = readOracleSQL(config['DD']['connection_string'], sql)
    if len(res) == 0:
        uuid_exists = False;

    return uuid_exists

def get_dd_sequence_number(config):
    schema = config['DD']['schema']
    sql = "select GDBBE_SEQ.NEXTVAL as GPR_OBJECTID from dual"
    connection_string = config['DD']['connection_string']
    res = readOracleSQL(connection_string, sql)
    sequence_number =  unicode(res[0][0])
    return sequence_number

def clean(text):
    cleaned = text.replace("'", "''")
    return cleaned

