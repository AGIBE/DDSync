# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
import cx_Oracle
import pymysql
import psycopg2

def readOracleSQL(connection_string, sql_statement, fetchall=True):
    with cx_Oracle.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        if fetchall:
            result_list = cur.fetchall()
        else:
            result_list = cur.fetchone()
    
    return result_list

def writeOracleSQL(connection_string, sql_statement):
    with cx_Oracle.connect(connection_string) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql_statement)
        
def writeOracleSQL_multiple(connection_string, sql_statements):
    with cx_Oracle.connect(connection_string) as conn:
        conn.autocommit = True
        cur = conn.cursor()
        for sql_statement in sql_statements:
            cur.execute(sql_statement)
 
def readPostgreSQL(connection_string, sql_statement, fetchall=True):
    with psycopg2.connect(connection_string) as conn:
        cur = conn.cursor()
        cur.execute(sql_statement)
        if fetchall:
            result = cur.fetchall()
        else:
            result = cur.fetchone()
    return result

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

def get_syncable_codes_from_gdbp(config, nextwippe):
    # Server hat andere Spracheinstellung, diese wird teilweise durch das Checkskript beeinflusst
    # Hack: Es wird Tagname von einem Datum eines Donnerstages ausgegeben und damit das Datum des nächsten Donnerstages ausgegeben
    if nextwippe is True:
        sql = "select code from gdbp.geoprodukte where GEWUENSCHTES_WIPPENDATUM like NEXT_DAY(SYSDATE, to_char( to_date( '20180510', 'yyyymmdd' ), 'day' )) and ARBEITSTARTDATUM_NORMIERUNG is not null and FREIGABEDATUM_NORMIERUNG is not null and FREIGABEDATUM_GEODB_WIPPE is null order by code asc"
    else:
        # Es wird nicht geprüft, ob GP auf der nächsten Wippe ist. Wird verwendet, wenn z.B. über Jahreswechsel lange keine Wippe stattfindet und trotztdem Import werden soll.
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

def checkfor_gp_usecase_correction(config, uuid):
    sql = "select ID_GP_FALL from gdbp.geoprodukte where ID_GEODBMETA='" + uuid + "'"
    res = readOracleSQL(config['GDBP']['connection_string'], sql)
    usecase =  res[0][0]
    return usecase

def set_status_gp_usecase_correction(config, nextwippe):
    corr_gpr = []
    for gpr in get_syncable_codes_from_gdbp(config, nextwippe):
        uuid = get_uuid(config, gpr)
        usecase = checkfor_gp_usecase_correction(config, uuid)
        # Prüfen ob Usecase Korrektur
        if usecase == 4:
            schema = config['DD']['schema']
            sql = "SELECT count(*) FROM " + schema + ".TB_GEOPRODUKT_ZEITSTAND JOIN " + schema + ".TB_TASK ON TB_GEOPRODUKT_ZEITSTAND.GZS_OBJECTID=TB_TASK.GZS_OBJECTID WHERE UC_OBJECTID=4 AND (TB_TASK.TASK_ENDE is null OR (TB_TASK.TASK_ENDE > (sysdate - 5))) AND TB_GEOPRODUKT_ZEITSTAND.UUID='" + uuid + "'"
            res = readOracleSQL(config['DD']['connection_string'], sql, False)
            # Prüfen, ob es bereits ein Task-Ticket gibt
            if res[0] == 0:
                corr_gpr.append(gpr)
                sql = "UPDATE " + schema + ".TB_GEOPRODUKT_ZEITSTAND SET STA_OBJECTID = 1 where uuid = '" + uuid + "' and STA_OBJECTID = 9"
                writeOracleSQL(config['DD']['connection_string'], sql)
            
    return corr_gpr
